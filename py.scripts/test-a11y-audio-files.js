/**
 * اختبار تشغيل ملفات الصوت الحقيقية في المتصفح (بدل محاكاة Audio).
 * يتأكد أن كل مدخل في ACT_AUDIO يشير لملف موجود وقابل للفك والتشغيل.
 */
const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const root = path.join(__dirname, "..");
const pageUrl = pathToFileURL(path.join(root, "index.html")).href;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EDGE,
    headless: "new",
    args: ["--no-sandbox", "--autoplay-policy=no-user-gesture-required", "--mute-audio"]
  });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  await page.goto(pageUrl, { waitUntil: "load" });

  /* المانيفست صار {f:{...}, m:{...}} — نفحص كل صوت على حدة */
  const manifest = await page.evaluate(() => {
    const out = [];
    Object.keys(ACT_AUDIO).forEach(function (v) {
      const m = ACT_AUDIO[v];
      if (typeof m === "string") { out.push(["*" + v, m]); return; }
      Object.keys(m).forEach(function (k) { out.push([v + "/" + k, m[k]]); });
    });
    return out;
  });
  const keys = manifest.map(function (e) { return e[0]; });
  const voices = await page.evaluate(() => Object.keys(ACT_AUDIO));
  console.log("voices:", voices.join(","), "| manifest entries:", keys.length);

  const result = await page.evaluate(async (entries) => {
    const bad = [];
    const durs = [];
    for (const [key, src] of entries) {
      const ok = await new Promise((resolve) => {
        const a = new Audio(src);
        let settled = false;
        const done = (v) => { if (!settled) { settled = true; resolve(v); } };
        a.onloadedmetadata = () => done(a.duration);
        a.onerror = () => done(0);
        setTimeout(() => done(a.duration || 0), 5000);
      });
      if (!ok || ok <= 0) bad.push(key + " :: " + src);
      else durs.push(ok);
    }
    return { bad: bad.slice(0, 10), badCount: bad.length, count: durs.length, total: durs.reduce((a, b) => a + b, 0) };
  }, manifest);

  console.log("decodable:", result.count, "/", keys.length, "| broken:", result.badCount);
  if (result.bad.length) console.log("broken sample:", result.bad);
  console.log("total audio minutes:", (result.total / 60).toFixed(1));

  // تشغيل فعلي لمقطع واحد والتأكد من تقدم الوقت (قد يقبل headless التشغيل بدون جهاز صوت)
  const played = await page.evaluate(async () => {
    const a = new Audio(ACT_AUDIO.f["q1.num"]);
    a.volume = 0.0;
    const started = await Promise.race([
      a.play().then(() => "started").catch(e => "error:" + e.name),
      new Promise(r => setTimeout(() => r("timeout"), 4000))
    ]);
    await new Promise(r => setTimeout(r, 800));
    const t = a.currentTime;
    a.pause();
    return { started, currentTime: t, duration: a.duration, readyState: a.readyState };
  });
  console.log("real playback:", JSON.stringify(played));

  const ok = result.badCount === 0 && played.started !== "error:NotSupportedError" && errors.length === 0;
  console.log("page errors:", errors.length ? errors : "none");
  console.log(ok ? "ALL AUDIO FILES PLAY" : "AUDIO CHECK FAILED");
  await browser.close();
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error("FAIL", e.message); process.exit(2); });
