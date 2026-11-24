/* اختبار التدريب اللحظي على لوحة المفاتيح في الموقع الرئيسي:
   يتحقق أن الضغط الصحيح يصحّح ويقدّم، والخطأ يعطي تنبيهًا ويكرر المطلوب،
   وأن Escape يخرج من التدريب. */
const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const pageUrl = pathToFileURL(path.join(__dirname, "..", "الموقع.html")).href;

let pass = 0;
let fail = 0;
function check(name, cond, extra) {
  if (cond) {
    pass++;
    console.log("  PASS", name);
  } else {
    fail++;
    console.log("  FAIL", name, extra === undefined ? "" : "->", extra);
  }
}

function plays(page, since) {
  return page.evaluate(
    (t) => window.__played.filter((p) => p.at >= t).map((p) => p.src),
    since
  );
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EDGE,
    headless: "new",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage();
  await page.evaluateOnNewDocument(() => {
    window.__played = [];
    const proto = HTMLMediaElement.prototype;
    proto.play = function () {
      window.__played.push({ src: this.getAttribute("src") || this.src, at: Date.now() });
      return Promise.resolve();
    };
    proto.pause = function () {};
  });
  await page.goto(pageUrl, { waitUntil: "load" });
  await page.evaluate(() => {
    try {
      localStorage.clear();
    } catch (e) {
      /* تجاهل */
    }
  });

  const base = await page.evaluate(() => {
    const p = document.getElementById("live-practice");
    const s = document.getElementById("live-start");
    const t = document.getElementById("live-stop");
    return {
      panel: !!p,
      startVisible: !!s && !s.hidden,
      stopHidden: !!t && t.hidden,
    };
  });
  check("لوحة التدريب اللحظي موجودة", base.panel);
  check("زر البدء ظاهر وزر الإيقاف مخفي", base.startVisible && base.stopHidden);

  await page.click("#live-start");
  const started = await page.evaluate(() => ({
    live: document.getElementById("live-practice").dataset.live,
    startHidden: document.getElementById("live-start").hidden,
    stopShown: !document.getElementById("live-stop").hidden,
    stageShown: !document.getElementById("live-stage").hidden,
    status: document.getElementById("live-status").textContent,
    focusId: document.activeElement && document.activeElement.id,
  }));
  check("الوضع اللحظي بدأ", started.live === "on" && started.startHidden && started.stopShown);
  check("ساحة التدريب ظهرت", started.stageShown, started.status);
  check("التركيز انتقل إلى ساحة التدريب", started.focusId === "live-stage", started.focusId);
  check("المطلوب الأول مكتوب: Tab", started.status.indexOf("Tab") > -1, started.status);

  let t0 = Date.now();
  await page.keyboard.press("ArrowRight"); // مفتاح غير مطلوب الآن
  await new Promise((r) => setTimeout(r, 120));
  const wrong = await page.evaluate(() => ({
    status: document.getElementById("live-status").textContent,
  }));
  const wrongPlays = await plays(page, t0);
  check("الضغط الخطأ يشغّل صوت التنبيه", wrongPlays.some((s) => /buzz\.mp3/.test(s)), wrongPlays.join(", "));
  check("الضغط الخطأ يكرر المطلوب نفسه", wrong.status.indexOf("Tab") > -1, wrong.status);

  t0 = Date.now();
  await page.keyboard.press("Tab");
  await new Promise((r) => setTimeout(r, 120));
  const right = await page.evaluate(() => ({
    status: document.getElementById("live-status").textContent,
  }));
  const rightPlays = await plays(page, t0);
  check("الضغط الصحيح يشغّل التصفيق", rightPlays.some((s) => /clap\.mp3/.test(s)), rightPlays.join(", "));
  check("الضغط الصحيح ينتقل للمطلوب الثاني (Shift+Tab)", right.status.indexOf("Shift") > -1 || right.status.indexOf("تاب") > -1, right.status);

  /* إكمال بقية الخطوات: Shift+Tab، أسفل، أعلى، Enter */
  await page.keyboard.down("Shift");
  await page.keyboard.press("Tab");
  await page.keyboard.up("Shift");
  await new Promise((r) => setTimeout(r, 80));
  await page.keyboard.press("ArrowDown");
  await new Promise((r) => setTimeout(r, 80));
  await page.keyboard.press("ArrowUp");
  await new Promise((r) => setTimeout(r, 80));
  await page.keyboard.press("Enter");
  await new Promise((r) => setTimeout(r, 200));

  const done = await page.evaluate(() => ({
    live: document.getElementById("live-practice").dataset.live,
    startShown: !document.getElementById("live-start").hidden,
    status: document.getElementById("live-status").textContent,
  }));
  check("التدريب ينتهي بعد آخر مفتاح", done.startShown && done.status.indexOf("خلصت") > -1, done.status);

  /* إعادة الدخول ثم الخروج بـ Escape */
  await page.click("#live-start");
  await new Promise((r) => setTimeout(r, 100));
  const reentered = await page.evaluate(() => document.getElementById("live-practice").dataset.live);
  await page.keyboard.press("Escape");
  await new Promise((r) => setTimeout(r, 100));
  const exited = await page.evaluate(() => ({
    live: document.getElementById("live-practice").dataset.live,
    startShown: !document.getElementById("live-start").hidden,
    stopHidden: document.getElementById("live-stop").hidden,
  }));
  check("إعادة الدخول تعمل", reentered === "on");
  check("Escape يخرج من التدريب", exited.live === "off" && exited.startShown && exited.stopHidden);

  const errors = await page.evaluate(() => window.__errors || []);
  check("لا أخطاء جافاسكربت", errors.length === 0, errors.join(" | "));

  console.log(`\nالنتيجة: ${pass} ناجح، ${fail} فاشل`);
  await browser.close();
  process.exit(fail === 0 ? 0 : 1);
})().catch((e) => {
  console.error("FAIL", e.message);
  process.exit(1);
});
