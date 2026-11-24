const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const puppeteer = require(path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules", "puppeteer-core"));

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const ROOT = path.join(__dirname, "..");
const OUT = path.join(ROOT, "_preview");

const jobs = [
  ["course.html", "card-lesson.png"],
  ["index.html", "card-activity.png"],
  ["دليل_المرافق.html", "card-guide.png"]
];

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  for (const [file, out] of jobs) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 750, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(path.join(ROOT, file)).href, { waitUntil: "load" });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise(r => setTimeout(r, 250));
    await page.screenshot({ path: path.join(OUT, out), clip: { x: 0, y: 0, width: 1200, height: 750 } });
    console.log("shot:", out);
    await page.close();
  }
  await browser.close();
})();
