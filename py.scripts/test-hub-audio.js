/**
 * اختبار طبقة التلاوة في الموقع.html
 * نستبدل HTMLMediaElement.play بمُسجِّل، لأن الصوت الحقيقي لا يمكن سماعه في وضع headless.
 */
const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");

const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));
const axePath = path.join(npmModules, "axe-core", "axe.min.js");

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const ROOT = path.join(__dirname, "..");
const siteUrl = pathToFileURL(path.join(ROOT, "الموقع.html")).href;

let pass = 0;
let fail = 0;
function check(name, ok, extra) {
  if (ok) { pass++; console.log("  PASS " + name); }
  else { fail++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

const HOME_ORDER = [
  "e.skip", "e.brand", "n.home.cur", "n.lesson", "n.activity",
  "h.hero", "tour.title", "tour.start", "e.cta.train", "e.cta.lesson", "e.cta.activity",
  "sc.title", "sc.R", "sc.N", "sc.S", "sc.B", "sc.G", "sc.T", "sc.E", "sc.W", "sc.C",
  "sc.K", "sc.D", "sc.A", "sc.H", "sc.J", "sc.Esc", "sc.replay",
  "kt.title", "kt.tab", "kt.shifttab", "kt.enter", "kt.arrows", "kt.alt1234", "kt.alt6", "kt.escape", "kt.shift-tab-frame",
  "lp.title", "lp.start", "kt.done",
  "h.parts", "c.lesson", "c.activity", "h.steps", "t.step1", "t.step2",
  "h.features", "f.1", "f.2", "f.3", "f.4", "t.note"
];

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push("pageerror: " + e.message));
  page.on("console", m => {
    const t = m.text();
    if (m.type() === "error" && !/err_blocked|net::|favicon|Autoplay|NotAllowedError/.test(t)) {
      errors.push("console: " + t);
    }
  });

  await page.evaluateOnNewDocument(() => {
    window.__played = [];
    const proto = HTMLMediaElement.prototype;
    proto.play = function () {
      window.__lastAudio = this;
      window.__played.push({
        src: this.getAttribute("src") || this.src,
        vol: this.volume,
        rate: this.playbackRate,
        at: Date.now()
      });
      return Promise.resolve();
    };
    proto.pause = function () {};
    proto.load = function () {};
  });

  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(siteUrl, { waitUntil: "load" });
  await sleep(300);

  const clip = () => page.evaluate(() => {
    const a = window.__played;
    if (!a || !a.length) return null;
    return String(a[a.length - 1].src).split("/").pop();
  });
  const clipCount = () => page.evaluate(() => (window.__played || []).length);
  const active = () => page.evaluate(() => {
    const el = document.activeElement;
    if (!el) return "none";
    return el.getAttribute("data-speak") || el.id || el.tagName;
  });

  console.log("\n== 1) المانيفست والملفات ==");
  const manifest = await page.evaluate(() => {
    const m = (typeof HUB_AUDIO === "undefined") ? null : HUB_AUDIO;
    if (!m) return { voices: [], counts: {}, shape: "none" };
    const voices = Object.keys(m);
    const nested = voices.length === 2 && typeof m.f === "object" && typeof m.m === "object";
    const counts = {};
    if (nested) { voices.forEach(v => { counts[v] = Object.keys(m[v]).length; }); }
    else { counts.flat = voices.length; }
    return { voices: voices, counts: counts, shape: nested ? "nested" : "flat" };
  });
  check("المانيفست بصوتين (مذكر ومؤنث)", manifest.shape === "nested" && manifest.voices.join(",") === "m,f",
    JSON.stringify(manifest));
  check("كل صوت 168 مقطعًا (166 نصًا + مؤثران)", manifest.counts.f === 168 && manifest.counts.m === 168, JSON.stringify(manifest.counts));
  const missingKeys = await page.evaluate(() => {
    const used = new Set();
    document.querySelectorAll("[data-speak]").forEach(el => {
      el.getAttribute("data-speak").split(/\s+/).forEach(k => used.add(k));
    });
    return ["f", "m"].flatMap(function (v) {
      return [...used].filter(k => !(HUB_AUDIO[v] && HUB_AUDIO[v][k])).map(k => v + ":" + k);
    });
  });
  check("كل مفتاح في الصفحة موجود في الصوتين", missingKeys.length === 0, missingKeys.slice(0, 6).join(","));
  const sameKeys = await page.evaluate(() => {
    const a = Object.keys(HUB_AUDIO.f).sort().join("|");
    const b = Object.keys(HUB_AUDIO.m).sort().join("|");
    return a === b;
  });
  check("مفاتيح الصوتين متطابقة", sameKeys);
  const pathsPerVoice = await page.evaluate(() => {
    const bad = [];
    Object.keys(HUB_AUDIO.f).forEach(function (k) {
      const f = HUB_AUDIO.f[k], m = HUB_AUDIO.m[k];
      if (/^sfx\.(clap|buzz)$/.test(k)) { if (f !== m) bad.push(k); return; }
      if (!f.includes("/f/") || !m.includes("/m/")) bad.push(k);
    });
    return bad;
  });
  check("ملفات كل صوت في مجلده والمؤثرات مشتركة", pathsPerVoice.length === 0, pathsPerVoice.slice(0, 5).join(","));

  console.log("\n== 2) شريط التحكم الصوتي ==");
  check("شريط الصوت موجود", !!(await page.$("#audiobar")));
  const ctlCount = await page.$$eval("#audiobar button", els => els.length);
  check("سلسلة أزرار التحكم (7) بلا زر كتم", ctlCount === 7, String(ctlCount));
  check("لا يوجد زر كتم في الشريط", (await page.$$("#ctl-mute")).length === 0);
  check("زر الصوت يعلن اختصاره", (await page.$eval("#ctl-voice", el => el.getAttribute("aria-keyshortcuts"))) === "G Alt+G");
  check("الصوت الافتراضي مؤنث", (await page.$eval("#ctl-voice-lbl", el => el.textContent)) === "مؤنث");
  check("زر التلاوة مضغوط افتراضيًا", (await page.$eval("#ctl-tts", el => el.getAttribute("aria-pressed"))) === "true");
  check("مستوى الصوت 90 افتراضيًا", (await page.$eval("#ctl-vol", el => el.value)) === "90");
  check("زر المساعدة يعلن اختصاره", (await page.$eval("#ctl-help", el => el.getAttribute("aria-keyshortcuts"))) === "H Alt+H");

  console.log("\n== 2b) اختيار الصوت: مؤنث / مذكر ==");
  const lastSrc = () => page.evaluate(() => {
    const a = window.__played;
    if (!a || !a.length) return "";
    return String(a[a.length - 1].src).replace(/\\/g, "/");
  });
  await page.evaluate(() => document.querySelector("#view-home h1").focus());
  await sleep(120);
  check("ملفات المؤنث في مجلد f", /audio\/hub\/f\//.test(await lastSrc()), await lastSrc());
  await page.keyboard.down("Alt"); await page.keyboard.press("g"); await page.keyboard.up("Alt");
  await sleep(200);
  check("Alt+G يبدّل إلى المذكر", (await page.$eval("#ctl-voice-lbl", el => el.textContent)) === "مذكر");
  check("بعد التبديل تُشغَّل ملفات m", /audio\/hub\/m\//.test(await lastSrc()), await lastSrc());
  check("يعلن الصوت الجديد", (await clip()) === "ctl_voice_m.mp3", await clip());
  const savedVoice = await page.evaluate(() => JSON.parse(localStorage.getItem("hub.sp") || "{}").voice);
  check("اختيار الصوت محفوظ", savedVoice === "m", String(savedVoice));

  await page.keyboard.down("Alt"); await page.keyboard.press("g"); await page.keyboard.up("Alt");
  await sleep(200);
  check("Alt+G يعود إلى المؤنث", (await page.$eval("#ctl-voice-lbl", el => el.textContent)) === "مؤنث");
  check("يعلن المؤنث", (await clip()) === "ctl_voice_f.mp3", await clip());
  check("المقطع المسموع مؤنث", /audio\/hub\/f\//.test(await lastSrc()), await lastSrc());
  /* إعادة تحميل الصفحة حتى يبدأ قسم Tab من أول عنصر كما كان قبل إضافة القسم 2b */
  await page.reload({ waitUntil: "load" });
  await sleep(300);

  console.log("\n== 3) القراءة عند الوقوف على العنصر ==");
  await page.keyboard.press("Tab");
  await sleep(120);
  check("أول توقف: رابط التخطي", (await active()) === "e.skip", await active());
  check("مقطع التخطي يعمل", (await clip()) === "e_skip.mp3", await clip());

  await page.keyboard.press("Tab");
  await sleep(80);
  check("التالي: زر التلاوة", (await active()) === "ctl.tts", await active());
  check("مقطع زر التلاوة", (await clip()) === "ctl_tts.mp3", await clip());

  const barKeys = [];
  const arrows = ["ArrowLeft", "ArrowLeft", "ArrowLeft", "ArrowLeft", "ArrowLeft", "ArrowLeft"];
  for (const key of arrows) {
    await page.keyboard.press(key);
    await sleep(40);
    barKeys.push(await active());
  }
  check("الأسهم تتنقل بين أزرار الشريط", JSON.stringify(barKeys) === JSON.stringify([
    "ctl.voice", "ctl.repeat", "ctl.stop", "ctl.slower", "ctl.faster", "ctl.help"
  ]), barKeys.join(","));
  check("كل أزرار الشريط تُقرأ", (await clip()) === "ctl_help.mp3", await clip());

  await page.keyboard.press("Tab");
  await sleep(80);
  check("Tab التالية: شريط الصوت", (await active()) === "ctl.volume", await active());

  await page.keyboard.press("Tab");
  await sleep(80);
  check("بعد الشريط: الشعار", (await active()) === "e.brand", await active());
  check("مقطع الشعار", (await clip()) === "e_brand.mp3", await clip());

  await page.keyboard.press("Tab");
  await sleep(80);
  check("رابط الرئيسية يقرأ حالته الحالية", (await active()) === "n.home.cur", await active());
  check("مقطع الصفحة الحالية", (await clip()) === "n_home_cur.mp3", await clip());
  await page.keyboard.press("Tab");
  await sleep(80);
  check("رابط الدرس يشرح ماذا يفعل", (await active()) === "n.lesson" && (await clip()) === "n_lesson.mp3", await active() + "/" + await clip());

  console.log("\n== 4) التنقل بالقراءة Alt+↓ ==");
  await page.reload({ waitUntil: "load" });
  await sleep(250);
  const seq = [];
  for (let i = 0; i < HOME_ORDER.length + 1; i++) {
    await page.keyboard.down("Alt");
    await page.keyboard.press("ArrowDown");
    await page.keyboard.up("Alt");
    await sleep(60);
    seq.push(await active());
  }
  check("ترتيب القراءة يغطي كل عناصر الرئيسية", JSON.stringify(seq.slice(0, HOME_ORDER.length)) === JSON.stringify(HOME_ORDER), seq.join(" | "));
  check("ما بعد آخر عنصر: نهاية المحتوى", (await clip()) === "msg_end.mp3", await clip());

  await page.keyboard.down("Alt");
  await page.keyboard.press("ArrowUp");
  await page.keyboard.up("Alt");
  await sleep(80);
  check("Alt+↑ يعود للعنصر السابق", (await active()) === "f.4", await active());

  console.log("\n== 5) الدخول إلى الأقسام ==");
  await page.keyboard.down("Alt");
  await page.keyboard.press("3");
  await page.keyboard.up("Alt");
  await sleep(1100);
  check("Alt+3 يفتح قسم النشاط", (await page.$eval("#view-activity", el => !el.hidden)));
  const afterAlt3 = await page.evaluate(() => window.__played.map(p => String(p.src).split("/").pop()));
  check("يُعلَن عنوان قسم النشاط", afterAlt3.includes("h_activity.mp3"), afterAlt3.slice(-3).join(","));

  const sectionOrder = await page.evaluate(() => {
    const list = [];
    document.querySelectorAll("#view-activity [data-read]").forEach(el => list.push(el.getAttribute("data-speak")));
    return list;
  });
  check("عناصر قراءة قسم النشاط بترتيب منطقي", JSON.stringify(sectionOrder) === JSON.stringify([
    "p.lesson.home", "h.activity", "e.openfull.activity", "v.activity", "e.frame.activity",
    "p.activity.prev", "p.activity.next"
  ]), sectionOrder.join(" | "));

  await page.evaluate(() => document.getElementById("frame-activity").focus());
  await sleep(120);
  check("الإطار يشرح كيف يدخل Learner", (await clip()) === "e_frame_activity.mp3", await clip());

  console.log("\n== 6) التحكم: تلاوة، إعادة، مساعدة، سرعة، إيقاف، Esc ==");
  // ملاحظة: إذا كان التركيز داخل الإطار فالمفاتيح تذهب إلى الصفحة الداخلية،
  // لذلك نعيد التركيز إلى عنصر في الصفحة الأم قبل كل اختصار.
  const focusParent = async () => {
    await page.evaluate(() => document.querySelector("#view-activity h1").focus());
    await sleep(120);
  };
  await focusParent();

  await page.keyboard.down("Alt"); await page.keyboard.press("6"); await page.keyboard.up("Alt");
  await sleep(80);
  check("Alt+6 يوقف التلاوة", (await page.$eval("#ctl-tts", el => el.getAttribute("aria-pressed"))) === "false");
  check("نص الزر يتغير", (await page.$eval("#ctl-tts-lbl", el => el.textContent)) === "متوقفة");
  const beforeOff = await clipCount();
  await page.evaluate(() => document.querySelector("#view-activity h1").focus());
  await sleep(120);
  check("لا صوت والتلاوة متوقفة", (await clipCount()) === beforeOff);

  await page.evaluate(() => document.querySelector("#view-activity h1").focus());
  await page.keyboard.down("Alt"); await page.keyboard.press("6"); await page.keyboard.up("Alt");
  await sleep(120);
  check("Alt+6 يعيد التلاوة", (await page.$eval("#ctl-tts", el => el.getAttribute("aria-pressed"))) === "true");
  check("يعلن عودة التلاوة", (await clip()) === "msg_on.mp3", await clip());

  await focusParent();
  await page.keyboard.down("Alt"); await page.keyboard.press("5"); await page.keyboard.up("Alt");
  await sleep(80);
  check("Alt+5 لم يعد اختصارًا للكتم", (await page.$eval("#ctl-tts", el => el.getAttribute("aria-pressed"))) === "true");

  /* Esc: إيقاف أي صوت + تأكيد قصير مسموع */
  await page.evaluate(() => document.getElementById("ctl-slower").focus());
  await sleep(120);
  const escBefore = await clipCount();
  await page.keyboard.press("Escape");
  await sleep(120);
  check("Esc يوقف الصوت ويؤكد", (await clip()) === "msg_stop.mp3" && (await clipCount()) > escBefore, await clip());
  check("Esc يعلن الإيقاف نصيًا", (await page.$eval("#announce", el => el.textContent)).indexOf("إيقاف") >= 0,
    await page.$eval("#announce", el => el.textContent));

  /* الضغط على زر «أسرع» لا يقطع شرحه: التأكيد يُضاف بعده فيُسمع الاثنان */
  await page.evaluate(() => {
    window.__lastAudio = null;
  });
  await page.evaluate(() => document.getElementById("ctl-faster").focus());
  await sleep(150);
  const seqBefore = await clipCount();
  await page.keyboard.press("Enter");
  await sleep(300);
  const duringExplain = await page.evaluate((n) => window.__played.slice(n).map(p => String(p.src).split("/").pop()), seqBefore);
  check("الضغط على «أسرع» لا يقطع الشرح الجاري", duringExplain.length === 0, duringExplain.join(","));
  const firstAfterClick = await clip();
  await page.evaluate(() => { if (window.__lastAudio) window.__lastAudio.dispatchEvent(new Event("ended")); });
  await sleep(150);
  check("بعد انتهاء الشرح يُسمع تأكيد الإسراع", (await clip()) === "msg_faster.mp3", firstAfterClick + " -> " + await clip());
  await page.evaluate(() => { if (window.__lastAudio) window.__lastAudio.dispatchEvent(new Event("ended")); });
  await sleep(150);
  check("ثم يُعلَن مقدار السرعة بالكلمات", /^rate_11\.mp3$/.test(await clip()), await clip());
  check("السرعة تغيّرت فعلًا إلى 1.1", (await page.$eval("#ctl-rate", el => el.textContent)) === "1.1×");
  await page.keyboard.down("Alt"); await page.keyboard.press(","); await page.keyboard.up("Alt");
  await sleep(120);

  await page.evaluate(() => document.querySelector("#view-activity h1").focus());
  await sleep(120);
  const lastBefore = await clip();
  await page.keyboard.down("Alt"); await page.keyboard.press("r"); await page.keyboard.up("Alt");
  await sleep(120);
  check("Alt+R يعيد آخر مقطع", (await clip()) === lastBefore, await clip());

  await page.keyboard.down("Alt"); await page.keyboard.press("h"); await page.keyboard.up("Alt");
  await sleep(120);
  check("Alt+H يشرح الموقع كاملًا", (await clip()) === "v_help.mp3", await clip());

  const rate0 = await page.$eval("#ctl-rate", el => el.textContent);
  await page.keyboard.down("Alt"); await page.keyboard.press(","); await page.keyboard.up("Alt");
  await sleep(140);
  check("Alt+, يبطئ", (await page.$eval("#ctl-rate", el => el.textContent)) === "0.9×", rate0);
  await page.keyboard.down("Alt"); await page.keyboard.press("."); await page.keyboard.up("Alt");
  await page.keyboard.down("Alt"); await page.keyboard.press("."); await page.keyboard.up("Alt");
  await sleep(140);
  check("Alt+. يسرع", (await page.$eval("#ctl-rate", el => el.textContent)) === "1.1×");
  const rateApplied = await page.evaluate(() => window.__lastAudio ? window.__lastAudio.playbackRate : -1);
  check("السرعة تطبق على المشغل", Math.abs(rateApplied - 1.1) < 0.01, String(rateApplied));

  console.log("\n== 6b) الجولة الصوتية المتسلسلة ==");
  await page.goto(siteUrl, { waitUntil: "load" });
  await sleep(300);
  await page.keyboard.down("Alt"); await page.keyboard.press("t"); await page.keyboard.up("Alt");
  await sleep(250);
  check("Alt+T يبدأ الجولة من الخطوة الأولى", (await clip()) === "tour_1.mp3", await clip());
  check("لوحة الجولة تُعلن أنها تعمل", (await page.$eval("#tour", el => el.getAttribute("data-on"))) === "true");
  const prog1 = await page.$eval("#tour-progress", el => el.textContent);
  check("شريط التقدم يعرض الخطوة ١ من ١٠", /1/.test(prog1) && prog1.indexOf("10") > -1, prog1);
  check("وسم بصري على القسم المشروح", (await page.$$(".tour-hot")).length === 1);

  await page.evaluate(() => { if (window.__lastAudio) window.__lastAudio.dispatchEvent(new Event("ended")); });
  await sleep(200);
  check("ينتقل وحده إلى الخطوة الثانية", (await clip()) === "tour_2.mp3", await clip());
  check("التقدم يتحدث تلقائيًا", (await page.$eval("#tour-progress", el => el.textContent)).indexOf("2") > -1);

  await page.keyboard.down("Alt"); await page.keyboard.press("ArrowRight"); await page.keyboard.up("Alt");
  await sleep(200);
  check("Alt+→ الخطوة التالية", (await clip()) === "tour_3.mp3", await clip());
  await page.keyboard.down("Alt"); await page.keyboard.press("ArrowLeft"); await page.keyboard.up("Alt");
  await sleep(200);
  check("Alt+← الخطوة السابقة", (await clip()) === "tour_2.mp3", await clip());

  await page.keyboard.press("Escape");
  await sleep(200);
  check("Esc يوقف الجولة", (await page.$eval("#tour", el => el.getAttribute("data-on"))) === "false");
  check("أُزيل الوسم البصري", (await page.$$(".tour-hot")).length === 0);
  check("التأكيد الصوتي بعد الإيقاف", (await clip()) === "msg_stop.mp3", await clip());

  /* المتابعة من نفس الخطوة بدل الإعادة من الأولى */
  const resumeLabel = await page.$eval("#tour-play", el => el.textContent);
  check("الزر صار «تابع الجولة» ويذكر رقم الخطوة", resumeLabel.indexOf("تابع") > -1 && resumeLabel.indexOf("2") > -1, resumeLabel);
  check("شرح الزر يتغير إلى شرح المتابعة", (await page.$eval("#tour-play", el => el.getAttribute("data-speak"))) === "tour.resume");
  await page.evaluate(() => document.getElementById("tour-play").focus());
  await sleep(120);
  check("التركيز يقرأ شرح المتابعة", (await clip()) === "tour_resume.mp3", await clip());
  await page.keyboard.press("Enter");
  await sleep(200);
  check("المتابعة تكمل من الخطوة الثانية", (await clip()) === "tour_2.mp3", await clip());
  check("الجولة عادت للعمل", (await page.$eval("#tour", el => el.getAttribute("data-on"))) === "true");
  check("التقدم يبيّن الخطوة 2", (await page.$eval("#tour-progress", el => el.textContent)).indexOf("2") > -1);
  await page.keyboard.press("Escape");
  await sleep(200);

  await page.evaluate(() => document.querySelector(".skip").focus());
  await sleep(120);
  await page.keyboard.down("Alt"); await page.keyboard.press("ArrowDown"); await page.keyboard.up("Alt");
  await sleep(150);
  check("بعد الإيقاف يعمل التنقل بالقراءة عاديًا", (await active()) === "e.brand", await active());

  /* أي تنقّل أثناء الجولة يوقفها (لا يتركها تعمل في الخلفية) */
  await page.keyboard.down("Alt"); await page.keyboard.press("t"); await page.keyboard.up("Alt");
  await sleep(200);
  await page.keyboard.down("Alt"); await page.keyboard.press("ArrowDown"); await page.keyboard.up("Alt");
  await sleep(150);
  check("التنقل أثناء الجولة يوقفها", (await page.$eval("#tour", el => el.getAttribute("data-on"))) === "false");

  console.log("\n== 7) الحفظ والاستعادة ==");
  await page.evaluate(() => {
    const v = document.getElementById("ctl-vol");
    v.value = "60";
    v.dispatchEvent(new Event("input", { bubbles: true }));
    v.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await sleep(100);
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("hub.sp")));
  check("مستوى الصوت محفوظ", Math.round(saved.volume * 100) === 60, JSON.stringify(saved));
  check("السرعة محفوظة", Math.abs(saved.rate - 1.1) < 0.01);

  await page.goto(siteUrl + "?restore=1#home", { waitUntil: "load" });
  await sleep(300);
  check("استعادة مستوى الصوت بعد إعادة التحميل", (await page.$eval("#ctl-vol", el => el.value)) === "60");
  check("استعادة السرعة", (await page.$eval("#ctl-rate", el => el.textContent)) === "1.1×");
  const volApplied = await page.evaluate(async () => {
    document.querySelector(".card").focus();
    await new Promise(r => setTimeout(r, 60));
    const a = window.__played;
    return a[a.length - 1].vol;
  });
  check("المشغل يستخدم المستوى المحفوظ", Math.abs(volApplied - 0.6) < 0.01, String(volApplied));

  console.log("\n== 8) السلامة وإمكانية الوصول ==");
  await page.evaluate(() => localStorage.removeItem("hub.sp"));
  await page.goto(siteUrl, { waitUntil: "load" });
  await sleep(300);
  await page.addScriptTag({ path: axePath });
  const axeHome = await page.evaluate(async () => {
    const r = await window.axe.run(document, { resultTypes: ["violations"] });
    return r.violations.map(v => v.id + ":" + v.nodes.length);
  });
  check("axe: لا مخالفات في الرئيسية", axeHome.length === 0, axeHome.join(","));

  await page.evaluate(() => { location.hash = "#lesson"; });
  await sleep(900);
  const axeLesson = await page.evaluate(async () => {
    const r = await window.axe.run(document, { resultTypes: ["violations"] });
    return r.violations.map(v => v.id + ":" + v.nodes.length);
  });
  check("axe: لا مخالفات في قسم الدرس", axeLesson.length === 0, axeLesson.join(","));

  console.log("\n== 9) جسر الإطارات: الدخول والمرور ومنع التداخل ==");
  await page.evaluate(() => localStorage.removeItem("hub.sp"));
  await page.goto(siteUrl + "#activity", { waitUntil: "load" });
  await sleep(1200);

  // الوصول إلى الإطار بالتبويب
  let reached = false;
  for (let i = 0; i < 40; i++) {
    await page.keyboard.press("Tab");
    const id = await page.evaluate(() => (document.activeElement && document.activeElement.id) || "");
    if (id.startsWith("frame-")) { reached = true; break; }
  }
  check("الوصول إلى إطار النشاط بالتبويب", reached);

  const activityFrame = () => page.frames().find(f => f.url().includes("index.html"));
  check("إطار النشاط محمّل", !!activityFrame());
  const frameVoice = await page.evaluate(() => {
    const f = document.querySelector("#frame-activity");
    return f ? String(f.getAttribute("src") || "") : "";
  });
  check("رابط الإطار يحمل اختيار الصوت", /(?:\?|&)voice=[mf](?:&|$)/.test(frameVoice), frameVoice);

  // Alt+↓ على الإطار يجب أن يمر على المحتوى الداخلي (لا يقفز فوقه)
  await page.keyboard.down("Alt");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.up("Alt");
  await sleep(900);
  const inner = await activityFrame().evaluate(() => ({
    current, queue: Player.queue.length,
    playing: Player.audio ? String(Player.audio.src).split("/").pop() : null
  }));
  check("Alt+↓ على الإطار يقرأ داخل النشاط", /q\d+_num\.mp3/.test(inner.playing || ""), JSON.stringify(inner));
  const hubPlaying = await page.evaluate(() => {
    const a = document.querySelector("#announce");
    return window.__played.length ? String(window.__played[window.__played.length - 1].src).split("/").pop() : null;
  });
  check("صوت الصفحة توقف عند بدء صوت النشاط", !/^(e_frame_|v_activity)/.test(hubPlaying || ""), String(hubPlaying));

  // إيقاف متبادل: رسالة "speaking" من الإطار توقف مشغل الصفحة
  await page.evaluate(() => window.HubSpeech.say("v.home"));
  await sleep(120);
  const playingBefore = await page.evaluate(() => {
    const st = window.HubSpeech;
    return !!st && typeof st.stop === "function";
  });
  await activityFrame().evaluate(() => { window.parent.postMessage({ hub: "speaking" }, "*"); });
  await sleep(300);
  const afterMsgs = await page.evaluate(() => {
    // بعد رسالة speaking يجب ألّا يستمر المقطع: إعادة التشغيل تبدأ من جديد بلا تراكم
    const before = (window.__played || []).length;
    window.HubSpeech.say("v.home");
    return { before, after: (window.__played || []).length };
  });
  check("رسالة speaking من الإطار توقف مشغل الصفحة", playingBefore && afterMsgs.after === afterMsgs.before + 1,
    JSON.stringify(afterMsgs));

  // الحد: عند آخر سؤال، Alt+↓ يعيد المرور إلى الصفحة الأم
  await activityFrame().evaluate(() => { goTo(QUESTIONS.length - 1); });
  await sleep(400);
  await activityFrame().evaluate(() => {
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", altKey: true, bubbles: true }));
  });
  await sleep(500);
  const backInHub = await page.evaluate(() => {
    const el = document.activeElement;
    return !el || el.tagName !== "IFRAME";
  });
  check("عند نهاية المحتوى يعود المرور إلى الصفحة الأم", backInHub);

  // الدخول بـEnter من الإطار: التركيز يدخل المستند الداخلي فعلًا (يستقر على سؤال)
  await page.evaluate(() => {
    const f = document.querySelector("#frame-activity");
    if (f) { f.focus(); }
  });
  await sleep(120);
  await activityFrame().evaluate(() => { if (typeof goTo === "function") { current = 0; } });
  await page.keyboard.press("Enter");
  await sleep(900);
  const childFocus = await activityFrame().evaluate(() => {
    const el = document.activeElement;
    return el ? (el.id || el.tagName) : "none";
  });
  check("Enter على الإطار ينقل التركيز إلى سؤال داخل النشاط", /^q\d+$/.test(childFocus), String(childFocus));

  console.log("\n== 10) الحروف المفردة والتشغيل التلقائي ==");
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) { /* تجاهل */ } });
  await page.goto(siteUrl, { waitUntil: "load" });
  await sleep(800);
  const firstClip = await page.evaluate(() => {
    const a = window.__played || [];
    return a.length ? String(a[0].src).split("/").pop() : "";
  });
  check("أول ما يفتح الموقع: شرح الحروف تلقائيًا", firstClip === "sc_intro.mp3", firstClip);
  check("لوحة الحروف فيها 15 حرفًا", (await page.$$eval(".sc-item", els => els.length)) === 15);
  const scAllVoiced = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll(".sc-item").forEach(el => {
      const k = el.getAttribute("data-speak");
      if (!k || !HUB_AUDIO.f[k] || !HUB_AUDIO.m[k]) bad.push(k || "?");
    });
    return bad;
  });
  check("كل حرف في اللوحة له صوت في الصوتين", scAllVoiced.length === 0, scAllVoiced.join(","));
  check("زرار إعادة شرح الحروف موجود", !!(await page.$("#sc-replay")));
  const scStatus0 = await page.$eval("#sc-status", el => el.textContent);
  check("حالة اللوحة تعلن بدء الشرح", scStatus0.indexOf("شرح الحروف") > -1, scStatus0);

  await page.evaluate(() => { if (window.__lastAudio) window.__lastAudio.dispatchEvent(new Event("ended")); });
  await sleep(300);
  check("بعد الشرح يبدأ التدريب اللحظي تلقائيًا",
    (await page.$eval("#live-practice", el => el.dataset.live)) === "on");
  check("ويطلب أول مفتاح (Tab)",
    (await page.$eval("#live-status", el => el.textContent)).indexOf("Tab") > -1);
  await page.keyboard.press("Escape");
  await sleep(200);
  check("Escape يخرج من التدريب التلقائي",
    (await page.$eval("#live-practice", el => el.dataset.live)) === "off");

  const volBefore = await page.$eval("#ctl-vol", el => Number(el.value));
  await page.keyboard.press("r");
  await sleep(150);
  check("حرف R يعلّي الصوت",
    (await page.$eval("#ctl-vol", el => Number(el.value))) === Math.min(100, volBefore + 10),
    String(volBefore));
  await page.keyboard.press("n");
  await sleep(150);
  check("حرف N يوطّي الصوت",
    (await page.$eval("#ctl-vol", el => Number(el.value))) === volBefore, String(volBefore));
  check("اللوحة تعلن مستوى الصوت",
    (await page.$eval("#sc-status", el => el.textContent)).indexOf("مستوى الصوت") > -1);

  await page.keyboard.press("s");
  await sleep(150);
  check("حرف S يسرّع", (await page.$eval("#ctl-rate", el => el.textContent)) === "1.1×");
  await page.keyboard.press("b");
  await sleep(150);
  check("حرف B يبطّئ", (await page.$eval("#ctl-rate", el => el.textContent)) === "1.0×");

  await page.keyboard.press("g");
  await sleep(150);
  check("حرف G يبدّل الصوت إلى المذكر",
    (await page.$eval("#ctl-voice-lbl", el => el.textContent)) === "مذكر");
  await page.keyboard.press("g");
  await sleep(150);
  check("حرف G يعيد الصوت المؤنث",
    (await page.$eval("#ctl-voice-lbl", el => el.textContent)) === "مؤنث");

  const beforeE = await clipCount();
  await page.keyboard.press("e");
  await sleep(150);
  check("حرف E يعيد آخر مقطع", (await clipCount()) > beforeE);

  await page.keyboard.press("w");
  await sleep(150);
  check("حرف W يوقف ويؤكد", (await clip()) === "msg_stop.mp3", await clip());
  check("حرف W يعلن الإيقاف نصيًا",
    (await page.$eval("#announce", el => el.textContent)).indexOf("إيقاف") > -1);

  await page.keyboard.press("c");
  await sleep(150);
  check("حرف C يعيد شرح الحروف", (await clip()) === "sc_intro.mp3", await clip());
  check("ومعه زر إعادة الحروف يعمل", await page.evaluate(() => {
    document.getElementById("sc-replay").click();
    return document.getElementById("sc-status").textContent.indexOf("بتسمع شرح الحروف") > -1;
  }));

  await page.keyboard.press("h");
  await sleep(150);
  check("حرف H يشرح الموقع", (await clip()) === "v_help.mp3", await clip());

  await page.keyboard.press("j");
  await sleep(200);
  check("حرف J يبدأ الجولة", (await page.$eval("#tour", el => el.dataset.on)) === "true");
  await page.keyboard.press("Escape");
  await sleep(200);
  check("Esc يوقف الجولة", (await page.$eval("#tour", el => el.dataset.on)) === "false");

  await page.keyboard.press("k");
  await sleep(200);
  check("حرف K يبدأ التدريب اللحظي",
    (await page.$eval("#live-practice", el => el.dataset.live)) === "on");
  await page.keyboard.press("Escape");
  await sleep(150);

  await page.keyboard.press("d");
  await sleep(1200);
  check("حرف D يفتح الدرس", (await page.evaluate(() => location.hash)) === "#lesson" &&
    (await page.$eval("#view-lesson", el => !el.hidden)));
  await page.keyboard.press("a");
  await sleep(1200);
  check("حرف A يفتح النشاط", (await page.evaluate(() => location.hash)) === "#activity" &&
    (await page.$eval("#view-activity", el => !el.hidden)));

  await page.evaluate(() => document.getElementById("ctl-vol").focus());
  await sleep(100);
  const hashBefore = await page.evaluate(() => location.hash);
  await page.keyboard.press("d");
  await sleep(150);
  check("الحروف لا تعمل أثناء الكتابة في حقل",
    (await page.evaluate(() => location.hash)) === hashBefore);

  console.log("\n== 11) صدى الحروف وجسر الإطارات ==");
  await page.goto(siteUrl + "#home", { waitUntil: "load" });
  await sleep(700);
  await page.keyboard.press("r");
  await sleep(200);
  const echo = await page.evaluate(() => {
    const el = document.getElementById("key-echo");
    return { hidden: el.hidden, text: el.textContent };
  });
  check("كل حرف يظهر صدى مرئي أسفل الشاشة", echo.hidden === false && /آخر حرف: R/.test(echo.text), JSON.stringify(echo));
  await page.waitForFunction(() => document.getElementById("key-echo").hidden === true, { timeout: 6000 });
  check("الصدى يختفي وحده بعد ثوانٍ", true);

  const volNow = await page.$eval("#ctl-vol", el => Number(el.value));
  await page.keyboard.press("n");
  await sleep(200);
  check("الصدى يتغير مع الحرف الجديد",
    /آخر حرف: N/.test(await page.$eval("#key-echo", el => el.textContent)) &&
    (await page.$eval("#ctl-vol", el => Number(el.value))) === Math.max(0, volNow - 10));

  /* أثناء التدريب اللحظي: الحروف تمرّ ولا تُحسب إجابة خاطئة ولا توقف التدريب */
  await page.keyboard.press("k");
  await sleep(300);
  await page.keyboard.press("s");
  await sleep(250);
  const drillState = await page.evaluate(() => ({
    live: document.getElementById("live-practice").dataset.live,
    status: document.getElementById("live-status").textContent,
    echo: document.getElementById("key-echo").textContent
  }));
  check("الحروف شغالة جوه التدريب اللحظي", drillState.live === "on" && /آخر حرف: S/.test(drillState.echo),
    JSON.stringify(drillState));
  check("ولا تُحسب إجابة خاطئة ولا تُقدّم الخطوة", /Tab/.test(drillState.status), drillState.status);
  await page.keyboard.press("d");
  await sleep(1200);
  check("الخروج من الرئيسية بحرف ينهي التدريب اللحظي",
    (await page.$eval("#live-practice", el => el.dataset.live)) === "off" &&
    (await page.evaluate(() => location.hash)) === "#lesson");

  /* الحروف من داخل إطار الدرس تصل إلى الرئيسية عبر الجسر */
  const lessonFrame = () => page.frames().find(f => f.url().includes("course.html"));
  await page.waitForFunction(() => !!document.getElementById("frame-lesson").getAttribute("src"), { timeout: 8000 });
  await sleep(900);
  check("إطار الدرس محمّل", !!lessonFrame());
  const volBeforeBridge = await page.$eval("#ctl-vol", el => Number(el.value));
  await lessonFrame().evaluate(() => {
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "r", code: "KeyR", bubbles: true, cancelable: true }));
  });
  await sleep(400);
  const bridged = await page.evaluate(() => ({
    vol: Number(document.getElementById("ctl-vol").value),
    echo: document.getElementById("key-echo").textContent
  }));
  check("حرف من داخل إطار الدرس يوصّل للرئيسية",
    bridged.vol === Math.min(100, volBeforeBridge + 10) && /آخر حرف: R/.test(bridged.echo),
    JSON.stringify({ before: volBeforeBridge, after: bridged }));

  check("لا أخطاء JavaScript", errors.length === 0, errors.slice(0, 4).join(" | "));

  console.log(`\nالنتيجة: ${pass} ناجح، ${fail} فاشل`);
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(err => {
  console.error("خطأ في الاختبار:", err);
  process.exit(1);
});
