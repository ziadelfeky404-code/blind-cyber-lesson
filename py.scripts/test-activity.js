const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));
const axeSource = require(path.join(npmModules, "axe-core")).source;

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const pageUrl = pathToFileURL(
  path.join(__dirname, "..", "index.html")
).href;

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.goto(pageUrl, { waitUntil: "load" });

  await page.evaluate(axeSource);
  const axe = await page.evaluate(async () => await window.axe.run());
  console.log("AXE violations:", axe.violations.length);
  axe.violations.forEach(v => console.log("  -", v.id, "|", v.impact, "|", v.nodes.length, "nodes"));

  const total = await page.$$eval('input[type="radio"]', els => els.length);
  console.log("radio inputs:", total);

  /* الإجابات الصحيحة تُقرأ من الصفحة نفسها، حتى لا يتعطل الاختبار عند تغيير ترتيب الأسئلة */
  const correctIdx = await page.evaluate(() => eval("QUESTIONS").map(q => q.correct));

  const results = await page.$$eval("section.scenario", (secs, answers) => {
    return secs.map((sec, i) => {
      sec.querySelectorAll('input[type="radio"]')[answers[i]].click();
      sec.querySelector("button").click();
      const fb = sec.querySelector(".feedback");
      return { i: i + 1, cls: fb.className, text: fb.textContent.slice(0, 30) };
    });
  }, correctIdx);

  const okCount = results.filter(r => r.cls.includes("ok")).length;
  console.log("correct selections accepted:", okCount, "/", results.length);
  console.log("summary:", await page.$eval("#summary-text", el => el.textContent));

  await page.focus('#q1 input[type="radio"]');
  await page.keyboard.press("ArrowDown");
  const kbChecked = await page.$eval('input[name="q1"]:checked', el => el.value);
  console.log("keyboard ArrowDown selected value:", kbChecked);

  const firstBtnFocus = await page.evaluate(() => {
    const b = document.querySelector("#q1 button");
    b.focus();
    return document.activeElement === b;
  });
  console.log("check button focusable:", firstBtnFocus);

  await page.click("#reset");
  const emptyCheck = await page.evaluate(() => {
    const sec = document.querySelector("#q2");
    sec.querySelector("button").click();
    const fb = sec.querySelector(".feedback");
    return { cls: fb.className, text: fb.textContent.slice(0, 40) };
  });
  console.log("no-selection feedback:", emptyCheck.cls, "|", emptyCheck.text);

  const wrongCheck = await page.evaluate(() => {
    const answers = eval("QUESTIONS").map(q => q.correct);
    const sec = document.querySelector("#q5");
    const radios = sec.querySelectorAll('input[type="radio"]');
    const wrong = answers[4] === 0 ? 1 : 0;
    radios[wrong].click();
    sec.querySelector("button").click();
    const fb = sec.querySelector(".feedback");
    return { cls: fb.className, text: fb.textContent.slice(0, 40) };
  });
  console.log("wrong-answer feedback:", wrongCheck.cls, "|", wrongCheck.text);

  await page.click("#reset");
  console.log("after reset summary:", await page.$eval("#summary-text", el => el.textContent));
  console.log("after reset feedback hidden:", await page.$eval("#q1 .feedback", el => !el.classList.contains("show")));

  /* أزرار الإجراءات الثلاثة بعد التحقق: التالي / إعادة / اسمع الإجابة الصحيحة */
  await page.evaluate(() => {
    const sec = document.querySelector("#q3");
    const answers = eval("QUESTIONS").map(q => q.correct);
    sec.querySelectorAll('input[type="radio"]')[answers[2]].click();
    sec.querySelector("button").click();
  });
  const actions = await page.evaluate(() => {
    const sec = document.querySelector("#q3");
    const btns = Array.prototype.map.call(sec.querySelectorAll(".action-btn"), b => b.textContent.trim());
    return { count: btns.length, labels: btns };
  });
  console.log("action buttons:", actions.count, "|", actions.labels.join(" / "));

  const revealed = await page.evaluate(() => {
    const sec = document.querySelector("#q3");
    sec.querySelector(".action-btn.reveal").click();
    const ex = sec.querySelector(".explain");
    return ex ? ex.textContent.slice(0, 60) : null;
  });
  console.log("reveal shows explanation:", revealed);

  await browser.close();
})().catch(e => { console.error("FAIL", e.message); process.exit(1); });
