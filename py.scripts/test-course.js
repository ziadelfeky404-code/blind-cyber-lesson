const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));
const axeSource = require(path.join(npmModules, "axe-core")).source;

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const pageUrl = pathToFileURL(path.join(__dirname, "..", "course.html")).href;

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.goto(pageUrl, { waitUntil: "load" });

  // Reveal all slides so axe scans the entire course (incl. quiz).
  await page.evaluate(() => document.querySelectorAll(".slide").forEach(s => (s.hidden = false)));
  await page.evaluate(axeSource);
  const axe = await page.evaluate(async () => await window.axe.run());
  console.log("AXE violations:", axe.violations.length);
  axe.violations.forEach(v => console.log("  -", v.id, "|", v.impact, "|", v.nodes.length, "nodes"));
  await page.evaluate(() => { const s = document.querySelectorAll(".slide"); s.forEach((x, k) => (x.hidden = k !== 0)); });

  const slideCount = await page.$$eval(".slide", els => els.length);
  const quizCount = await page.$$eval(".quiz-item", els => els.length);
  const radioCount = await page.$$eval('input[type="radio"]', els => els.length);
  console.log("slides:", slideCount, "quiz items:", quizCount, "radios:", radioCount);

  // Answer all quiz questions correctly.
  const okResults = await page.$$eval(".quiz-item", items => {
    return items.map(fs => {
      const correct = parseInt(fs.getAttribute("data-correct"), 10);
      const radios = fs.querySelectorAll('input[type="radio"]');
      radios[correct].click();
      fs.querySelector(".check").click();
      const fb = fs.querySelector(".feedback");
      return { cls: fb.className, text: fb.textContent.slice(0, 25) };
    });
  });
  console.log("correct answered & ok:", okResults.filter(r => r.cls.includes("ok")).length, "/", okResults.length);

  // Wrong answer on first question.
  const wrong = await page.evaluate(() => {
    const fs = document.querySelector(".quiz-item");
    fs.querySelector(".reset").click();
    const correct = parseInt(fs.getAttribute("data-correct"), 10);
    const radios = fs.querySelectorAll('input[type="radio"]');
    const wrongIdx = correct === 0 ? 1 : 0;
    radios[wrongIdx].click();
    fs.querySelector(".check").click();
    const fb = fs.querySelector(".feedback");
    return { cls: fb.className, text: fb.textContent.slice(0, 25) };
  });
  console.log("wrong answer:", wrong.cls, "|", wrong.text);

  // No-selection path.
  const noSel = await page.evaluate(() => {
    const fs = document.querySelector(".quiz-item");
    fs.querySelector(".reset").click();
    fs.querySelector(".check").click();
    const fb = fs.querySelector(".feedback");
    return { cls: fb.className, text: fb.textContent.slice(0, 30) };
  });
  console.log("no-selection:", noSel.cls, "|", noSel.text);

  // Reset restores state.
  const afterReset = await page.evaluate(() => {
    const fs = document.querySelector(".quiz-item");
    fs.querySelector(".reset").click();
    return { checkDisabled: fs.querySelector(".check").disabled, resetHidden: fs.querySelector(".reset").hidden, fb: fs.querySelector(".feedback").textContent };
  });
  console.log("after reset:", JSON.stringify(afterReset));

  // Keyboard navigation on toolbar.
  await page.focus("#next");
  await page.keyboard.press("Enter");
  const nav = await page.evaluate(() => ({
    count: document.getElementById("count").textContent,
    visible: Array.from(document.querySelectorAll(".slide")).findIndex(s => !s.hidden),
  }));
  console.log("after Next:", nav.count, "visibleIndex:", nav.visible);

  // Arrow-key navigation.
  await page.keyboard.press("ArrowLeft");
  console.log("after ArrowLeft count:", await page.$eval("#count", el => el.textContent));

  // Feedback must not rely on color: check ::before content exists.
  const beforeContent = await page.evaluate(() => {
    const el = document.querySelector(".feedback.ok");
    return el ? getComputedStyle(el, "::before").content : "none";
  });
  console.log("ok ::before content:", beforeContent);

  await browser.close();
})().catch(e => { console.error("FAIL", e.message); process.exit(1); });
