const path = require("path");
const os = require("os");
const fs = require("fs");
const { pathToFileURL } = require("url");
const nm = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(nm, "puppeteer-core"));

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const OUT = "D:\\projects\\instrucsal design\\media-work\\output\\_preview";
const pages = [
  ["course", "D:\\projects\\instrucsal design\\media-work\\storyline\\course.html"],
  ["activity", "D:\\projects\\instrucsal design\\media-work\\output\\النشاط_التفاعلي\\index.html"],
  ["lesson", "D:\\projects\\instrucsal design\\media-work\\output\\lesson.html"],
  ["companion", "D:\projects\instrucsal design\media-work\output\Storyline\دليل_المرافق.html"],
];

const { pathToFileURL: toUrl } = require("url");

(async () => {
  require("fs").mkdirSync("D:\\projects\\instrucsal design\\media-work\\output\\_preview", { recursive: true });
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1100, height: 1400, deviceScaleFactor: 1 });
  for (const [name, file] of [
    ["course", "D:\\projects\\instrucsal design\\media-work\\storyline\\course.html"],
    ["activity", "D:\\projects\\instrucsal design\\media-work\\output\\النشاط_التفاعلي\\index.html"],
    ["lesson", "D:\\projects\\instrucsal design\\media-work\\output\\lesson.html"],
    ["companion", "D:\projects\instrucsal design\media-work\output\Storyline\دليل_المرافق.html"],
  ]) {
    await page.goto(toUrl(file).href, { waitUntil: "networkidle0" }).catch(() => {});
    if (name === "course") {
      await page.evaluate(() => document.querySelectorAll(".slide").forEach((s, i) => (s.hidden = i !== 0)));
    }
    await new Promise(r => setTimeout(r, 400));
    const out = "D:\\projects\\instrucsal design\\media-work\\output\\_preview\\" + name + ".png";
    await page.screenshot({ path: out, fullPage: false });
    console.log("shot:", out);
  }
  await browser.close();
})().catch(e => { console.error("FAIL", e.message); process.exit(1); });
