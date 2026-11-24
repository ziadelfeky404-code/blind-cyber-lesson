/**
 * اختبار التلاوة الصوتية والتنقل بالكيبورد.
 * نستبدل Audio بمُسجّل يوثّق كل مقطع يُشغّل وبأي مستوى صوت وسرعة،
 * ونستبدل speechSynthesis لرؤية الاحتياطي عند الحاجة.
 */
const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const pageUrl = pathToFileURL(path.join(__dirname, "..", "index.html")).href;

let failures = 0;
function check(name, cond, extra) {
  if (cond) console.log("PASS |", name);
  else { failures++; console.log("FAIL |", name, extra === undefined ? "" : "| " + JSON.stringify(extra)); }
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
const fileOf = src => (src || "").split("/").pop();

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));

  await page.evaluateOnNewDocument(() => {
    window.__played = [];
    window.__spoken = [];
    window.__cancelled = 0;

    window.Audio = function (src) {
      const self = this;
      this.src = src;
      this.volume = 1;
      this.playbackRate = 1;
      this.pause = function () {};
      this.play = function () {
        window.__played.push({ src: self.src, volume: self.volume, rate: self.playbackRate });
        setTimeout(function () { if (self.onended) self.onended(); }, 0);
        return Promise.resolve();
      };
      return this;
    };

    const synth = window.speechSynthesis;
    synth.cancel = function () { window.__cancelled++; };
    synth.speak = function (u) {
      window.__spoken.push(u.text);
      setTimeout(function () { if (u.onend) u.onend(); }, 0);
    };
  });

  await page.goto(pageUrl, { waitUntil: "load" });
  await sleep(250);

  const played = () => page.evaluate(() => { const p = window.__played.slice(); window.__played = []; return p; });
  const spoken = () => page.evaluate(() => { const s = window.__spoken.slice(); window.__spoken = []; return s; });

  // 1) السؤال الأول: أربعة مقاطع مستقلة بالترتيب
  await page.evaluate(() => document.getElementById("q1").focus());
  await sleep(350);
  let p = await played();
  let files = p.map(x => fileOf(x.src));
  check("السؤال الأول: 4 مقاطع منفصلة (ليس صوتًا واحدًا)", files.length === 4, files);
  check("السؤال الأول: يبدأ بمقطع رقم السؤال", files[0] === "q1_num.mp3", files);
  check("السؤال الأول: الموقف ثم نص السؤال ثم الإرشاد",
    files[1] === "q1_ctx.mp3" && files[2] === "q1_q.mp3" && files[3] === "q1_hint.mp3", files);
  check("لا نطق احتياطي عند وجود الملفات", (await spoken()).length === 0);

  // 2) ArrowDown ينقل للسؤال الثاني
  await page.keyboard.press("ArrowDown");
  await sleep(350);
  files = (await played()).map(x => fileOf(x.src));
  check("ArrowDown: صوت السؤال الثاني", files[0] === "q2_num.mp3", files);
  const focus2 = await page.evaluate(() => document.activeElement && document.activeElement.id);
  check("ArrowDown: التركيز على q2", focus2 === "q2", focus2);

  // 3) الوصول لبديل يعلن البديل وحده
  await page.focus('#q2 input[value="0"]');
  await sleep(300);
  files = (await played()).map(x => fileOf(x.src));
  check("بديل: مقطع البديل الأول فقط", files.length === 1 && files[0] === "q2_o1.mp3", files);

  // 4) السهم داخل البدائل ينقل ويعلن البديل الجديد + كلمة محدد
  await page.keyboard.press("ArrowDown");
  await sleep(300);
  files = (await played()).map(x => fileOf(x.src));
  check("ArrowDown داخل البدائل: البديل الثاني", files[0] === "q2_o2.mp3", files);
  check("البديل المختار يُعلَن أنه محدد", files.indexOf("msg_selected.mp3") > -1, files);
  const checked = await page.$eval('input[name="q1"]:checked', el => el.value);
  check("سلوك الراديو الأصلي محفوظ", checked === "1", checked);

  // 5) إعادة جزئية: السؤال
  await page.evaluate(() => document.getElementById("a11y-q").click());
  await sleep(250);
  files = (await played()).map(x => fileOf(x.src));
  check("إعادة السؤال: مقطع السؤال فقط", files.length === 1 && files[0] === "q2_qr.mp3", files);

  // 6) إعادة جزئية: الموقف
  await page.evaluate(() => document.getElementById("a11y-ctx").click());
  await sleep(250);
  files = (await played()).map(x => fileOf(x.src));
  check("إعادة الموقف: مقطع الموقف فقط", files.length === 1 && files[0] === "q2_ctx.mp3", files);

  // 7) إعادة البديل الحالي
  await page.evaluate(() => document.getElementById("a11y-opt").click());
  await sleep(250);
  files = (await played()).map(x => fileOf(x.src));
  check("إعادة البديل: البديل المحدد", files[0] === "q2_o2.mp3", files);

  // 8) إعادة التغذية قبل التحقق
  await page.evaluate(() => document.getElementById("a11y-fb").click());
  await sleep(250);
  files = (await played()).map(x => fileOf(x.src));
  check("إعادة التغذية قبل التحقق: تنبيه", files[0] === "msg_nofb.mp3", files);

  // 9) التحقق: مؤثر صوتي ثم حكم ثم إرشاد الأزرار الثلاثة
  await page.evaluate(() => document.getElementById("q2").querySelector("button").click());
  await sleep(400);
  files = (await played()).map(x => fileOf(x.src));
  check("بعد التحقق: مؤثر صوتي أولًا", files[0] === "clap.mp3" || files[0] === "buzz.mp3", files);
  check("بعد التحقق: حكم صوتي", files.indexOf("fb_ok.mp3") > -1 || files.indexOf("fb_bad.mp3") > -1, files);
  check("بعد التحقق: إرشاد الأزرار الثلاثة", files[files.length - 1] === "msg_choices.mp3", files);

  // 9ب) زر إعادة التغذية بعد التحقق يشرح الإجابة الصحيحة لهذا السؤال
  await page.evaluate(() => document.getElementById("a11y-fb").click());
  await sleep(250);
  files = (await played()).map(x => fileOf(x.src));
  check("إعادة التغذية بعد التحقق: شرح السؤال", files[0] === "q2_fbbad.mp3" || files[0] === "q2_fbok.mp3", files);

  // 10) Alt+2 يعيد السؤال من أي مكان
  await page.evaluate(() => document.body.focus());
  await page.keyboard.down("Alt");
  await page.keyboard.press("2");
  await page.keyboard.up("Alt");
  await sleep(250);
  files = (await played()).map(x => fileOf(x.src));
  check("Alt+2: إعادة السؤال", files[0] === "q2_qr.mp3", files);

  // 11) مستوى الصوت يُطبَّق على الصوت
  await page.evaluate(() => {
    const v = document.getElementById("a11y-vol");
    v.value = "40";
    v.dispatchEvent(new Event("input", { bubbles: true }));
    v.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await sleep(250);
  p = await played();
  check("مستوى الصوت 0.4 مطبّق", Math.abs(p[p.length - 1].volume - 0.4) < 1e-3, p[p.length - 1]);
  check("إعلان مستوى الصوت", fileOf(p[p.length - 1].src) === "vol_40.mp3", p[p.length - 1]);

  // 12) السرعة تُطبَّق كلاحقًا
  await page.evaluate(() => {
    const r = document.getElementById("a11y-rate");
    r.value = "130";
    r.dispatchEvent(new Event("input", { bubbles: true }));
    r.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await sleep(200);
  await page.evaluate(() => document.getElementById("a11y-fb").click());
  await sleep(250);
  p = await played();
  check("سرعة القراءة 1.3 مطبّقة", Math.abs(p[p.length - 1].rate - 1.3) < 1e-3, p[p.length - 1]);

  // 13) لا زر كتم: مستوى الصوت هو وسيلة خفض الصوت
  check("لا يوجد زر كتم في لوحة النشاط", (await page.$$("#a11y-mute")).length === 0);
  check("قائمة الاختصارات تذكر Alt+5 لطريقة الحل", (await page.content()).indexOf("Alt</kbd>+<kbd>5") > -1);

  // 14) إيقاف التلاوة
  await page.evaluate(() => document.getElementById("a11y-tts").click());
  await sleep(150);
  await played();
  await page.evaluate(() => document.getElementById("a11y-q").click());
  await sleep(200);
  check("إيقاف التلاوة: لا تشغيل", (await played()).length === 0);
  await page.evaluate(() => document.getElementById("a11y-tts").click());
  await sleep(250);
  check("تشغيل التلاوة: إعلان", fileOf((await played()).pop().src) === "msg_ttson.mp3");

  // 15) إعادة المحاولة
  await page.evaluate(() => document.getElementById("a11y-rate").dispatchEvent(new Event("change")));
  await page.evaluate(() => document.getElementById("reset").click());
  await sleep(450);
  files = (await played()).map(x => fileOf(x.src));
  check("إعادة المحاولة: إعلان المسح أولًا", files[0] === "msg_reset.mp3", files);
  check("إعادة المحاولة: العودة للسؤال الأول", files.indexOf("q1_num.mp3") > -1, files);
  const pos = await page.$eval("#a11y-pos", el => el.textContent);
  check("الموضع معروض نصيًا", pos === "السؤال الأول من 10", pos);

  // 16) Tab مباشرة إلى بديل: رقم السؤال + الموقف + نص السؤال ثم البديل
  await page.reload({ waitUntil: "load" });
  await sleep(250);
  await page.focus('#q5 input[value="2"]');
  await sleep(350);
  files = (await played()).map(x => fileOf(x.src));
  check("Tab مباشرة لبديل: الموقف والسؤال ثم البديل",
    files.length === 4 && files[0] === "q5_num.mp3" && files[1] === "q5_ctx.mp3" &&
    files[2] === "q5_q.mp3" && files[3] === "q5_o3.mp3", files);

  // 17) احتياطي: مفتاح بلا ملف يذهب إلى speechSynthesis
  await page.evaluate(() => {
    Object.keys(ACT_AUDIO).forEach(function (v) {
      if (ACT_AUDIO[v] && typeof ACT_AUDIO[v] === "object") { delete ACT_AUDIO[v]["q5.o3"]; }
    });
  });
  await page.evaluate(() => document.getElementById("a11y-opt").click());
  await sleep(300);
  const sp = await spoken();
  check("الاحتياطي: نطق عند غياب الملف", sp.length === 1 && /^البديل الثالث من ثلاثة/.test(sp[0] || ""), sp);

  // 18) حماية من التعليق: لو الصوت ما اشتغلش، ينتقل للنطق الاحتياطي
  const page2 = await browser.newPage();
  await page2.evaluateOnNewDocument(() => {
    window.__spoken = [];
    window.Audio = function (src) {
      this.src = src; this.volume = 1; this.playbackRate = 1;
      this.pause = function () {};
      this.play = function () { return Promise.resolve(); }; // لا ينتهي أبدًا
    };
    window.speechSynthesis.cancel = function () {};
    window.speechSynthesis.speak = function (u) { window.__spoken.push(u.text); };
  });
  await page2.goto(pageUrl, { waitUntil: "load" });
  await sleep(200);
  await page2.evaluate(() => document.getElementById("q1").focus());
  await sleep(3800);
  const watched = await page2.evaluate(() => window.__spoken.slice());
  check("الحماية: عند تعليق الصوت ينتقل للنطق الاحتياطي", /^السؤال الأول/.test(watched[0] || ""), watched);
  await page2.close();

  // 19) طريقة الحل: قسم مرئي + زر + Alt+5 + قراءة العنوان
  await page.reload({ waitUntil: "load" });
  await sleep(250);
  const howtoVisible = await page.evaluate(() => {
    const sec = document.getElementById("howto");
    if (!sec) return null;
    const h = document.getElementById("howto-title");
    return {
      exists: true,
      hidden: !!(sec.offsetWidth === 0 && sec.offsetHeight === 0),
      heading: h ? h.textContent.trim() : "",
      steps: sec.querySelectorAll("ol > li").length
    };
  });
  check("قسم «كيف تحل المواقف؟» ظاهر بأربع خطوات",
    howtoVisible && !howtoVisible.hidden && howtoVisible.steps === 4 && howtoVisible.heading.indexOf("كيف تحل المواقف") === 0,
    howtoVisible);

  await page.evaluate(() => document.getElementById("howto-title").focus());
  await sleep(300);
  check("التركيز على عنوان طريقة الحل يقرأ help.how",
    (await played()).map(x => fileOf(x.src)).indexOf("help_how.mp3") > -1, (await played()).map(x => fileOf(x.src)));

  await page.evaluate(() => document.getElementById("a11y-how").focus());
  await sleep(300);
  const howFocus = (await played()).map(x => fileOf(x.src));
  check("زر طريقة الحل يشرح نفسه عند التركيز", howFocus.lastIndexOf("help_how_btn.mp3") > -1, howFocus);

  await page.keyboard.down("Alt"); await page.keyboard.press("5"); await page.keyboard.up("Alt");
  await sleep(300);
  check("Alt+5 يقرأ طريقة الحل", (await played()).map(x => fileOf(x.src)).indexOf("help_how.mp3") > -1,
    (await played()).map(x => fileOf(x.src)));

  // 20) Enter يختار البديل (لا Space فقط)
  await page.reload({ waitUntil: "load" });
  await sleep(250);
  await page.focus('#q2 input[value="1"]');
  await sleep(200);
  await page.keyboard.press("Enter");
  await sleep(200);
  const enterChecked = await page.evaluate(() => {
    const r = document.querySelector('#q2 input[value="1"]');
    return { checked: r.checked, group: document.querySelector('#q2 input[value="0"]').checked };
  });
  check("Enter يختار البديل المركَّز عليه", enterChecked.checked === true && enterChecked.group === false, enterChecked);

  // 20) لا أخطاء JS
  check("لا أخطاء JavaScript", errors.length === 0, errors);

  // 19) ربط العناصر
  const labelOk = await page.evaluate(() => {
    const sec = document.getElementById("q1");
    return sec.getAttribute("role") === "group" &&
      !!document.getElementById(sec.getAttribute("aria-labelledby")) &&
      !!document.getElementById(sec.getAttribute("aria-describedby"));
  });
  check("كل سؤال: role=group + عنوان + وصف", labelOk);

  await browser.close();
  console.log(failures === 0 ? "ALL A11Y SPEECH TESTS PASSED" : failures + " TEST(S) FAILED");
  process.exit(failures === 0 ? 0 : 1);
})().catch(e => { console.error("FAIL", e.message); process.exit(2); });
