// اختبار مزامنة اختيار الصوت بين الصفحة الأم والإطارات (مؤنث/مذكر)
const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const ROOT = path.join(__dirname, "..");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let fails = 0;
const check = (name, ok, extra) => {
  if (!ok) fails++;
  console.log((ok ? "  PASS " : "  FAIL ") + name + (extra !== undefined ? "  -> " + JSON.stringify(extra) : ""));
};

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  const errs = [];
  page.on("pageerror", (e) => errs.push(e.message));
  await page.goto(pathToFileURL(path.join(ROOT, "الموقع.html")).href + "#lesson", { waitUntil: "load" });
  await sleep(1500);

  const frame = () => page.frames().find((f) => decodeURIComponent(f.url()).includes("course.html"));
  check("إطار الدرس محمّل", !!frame(), page.frames().map((f) => decodeURIComponent(f.url()).split("/").pop()));

  const srcsOf = async (fr) =>
    fr.evaluate(() => [...document.querySelectorAll("audio[data-a]")].map((a) => a.getAttribute("src")));
  let srcs = await srcsOf(frame());
  check("الدرس يبدأ بالصوت المؤنث", srcs.length > 0 && srcs.every((s) => s.includes("audio/f/")), srcs.slice(0, 2));

  /* تبديل الصوت من الصفحة الأم: Alt+G */
  await page.evaluate(() => document.getElementById("ctl-voice").focus());
  await page.keyboard.down("Alt");
  await page.keyboard.press("g");
  await page.keyboard.up("Alt");
  await sleep(700);

  const fr2 = frame();
  srcs = await srcsOf(fr2);
  check("بعد التبديل: الدرس يستخدم الصوت المذكر", srcs.length > 0 && srcs.every((s) => s.includes("audio/m/")), srcs.slice(0, 2));
  const heroSrc = await fr2.evaluate(() => {
    /* مشغّل الترحيب قد يكون في رأس الصفحة (عرض مباشر) أو منقولًا إلى المحتوى (وضع التضمين) */
    const a = document.querySelector("header .audio-wrap audio, main .audio-wrap audio");
    return a ? a.getAttribute("src") : null;
  });
  check("مشغّل الترحيب يتبع الصوت", heroSrc === "audio/m/s01.mp3", heroSrc);

  await page.evaluate(() => { location.hash = "#activity"; });
  await sleep(1500);
  const act = page.frames().find((f) => decodeURIComponent(f.url()).includes("index.html"));
  check("إطار النشاط محمّل", !!act);
  if (act) {
    const played = await act.evaluate(() => {
      const keys = Object.keys(ACT_AUDIO);
      return { voice: window.VOICE, sample: ACT_AUDIO[window.VOICE] ? ACT_AUDIO[window.VOICE]["fb.ok"] : null, keys };
    });
    check("النشاط تلقّى اختيار الصوت", played.voice === "m", played);
    check("مسارات النشاط في مجلد الصوت", /audio\/act\/m\//.test(played.sample || ""), played.sample);
  }

  check("لا أخطاء JavaScript", errs.length === 0, errs.slice(0, 3));
  console.log(fails === 0 ? "\nALL FRAME-VOICE CHECKS PASSED" : "\n" + fails + " CHECK(S) FAILED");
  await browser.close();
  process.exit(fails ? 1 : 0);
})();
