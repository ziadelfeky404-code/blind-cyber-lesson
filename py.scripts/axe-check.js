const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));
const axeSource = require(path.join(npmModules, "axe-core")).source;

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const target = process.argv[2];
if (!target) { console.error("usage: node axe-check.js <file.html>"); process.exit(1); }
const pageUrl = pathToFileURL(path.resolve(target)).href;

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.goto(pageUrl, { waitUntil: "load" });
  await page.evaluate(axeSource);
  const axe = await page.evaluate(async () => await window.axe.run());
  console.log("file:", path.basename(target));
  console.log("AXE violations:", axe.violations.length);
  axe.violations.forEach(v => {
    console.log("  -", v.id, "|", v.impact, "|", v.nodes.length, "nodes");
    v.nodes.slice(0, 3).forEach(n => {
      console.log("      ", n.target.join(", "));
      console.log("        HTML:", n.html.slice(0, 200));
      console.log("        WHY:", (n.failureSummary || "").split("\n").join(" | "));
    });
  });
  await browser.close();
  process.exit(axe.violations.length ? 1 : 0);
})().catch(e => { console.error("FAIL", e.message); process.exit(2); });
