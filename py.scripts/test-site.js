const path = require("path");
const os = require("os");
const { pathToFileURL } = require("url");
const npmModules = path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules");
const puppeteer = require(path.join(npmModules, "puppeteer-core"));

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const ROOT = path.join(__dirname, "..");
const siteUrl = pathToFileURL(path.join(ROOT, "الموقع.html")).href;

let pass = 0, fail = 0;
function check(name, ok, extra) {
  if (ok) { pass++; console.log("  PASS " + name); }
  else { fail++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({ executablePath: EDGE, headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/err_blocked|net::/.test(m.text())) errors.push("console: " + m.text()); });

  const responses = new Map();
  page.on("response", r => { responses.set(r.url(), r.status()); });

  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(siteUrl, { waitUntil: "load" });
  await sleep(400);

  console.log("\n== initial state (home) ==");
  check("home view visible", await page.$eval("#view-home", el => !el.hidden));
  check("section views hidden", await page.$$eval(".view", els => els.filter(e => e.id !== "view-home").every(e => e.hidden)));
  check("nav home aria-current", await page.$eval('[data-nav="home"]', el => el.getAttribute("aria-current") === "page"));
  check("hero heading present", (await page.$eval("#home-title", el => el.textContent.trim())) === "التهديدات السيبرانية المتقدمة");
  check("2 section cards", (await page.$$(".cards .card")).length === 2);
  check("skip link present", await page.$eval("a.skip", el => !!el));

  console.log("\n== keyboard: Tab order reaches nav ==");
  const order = [];
  for (let i = 0; i < 16; i++) {
    await page.keyboard.press("Tab");
    order.push(await page.evaluate(() => {
      const a = document.activeElement;
      if (!a) { return "none"; }
      if (a.id) { return a.id; }
      return a.dataset.nav || a.className || a.tagName;
    }));
  }
  check("first tab stop is skip link", order[0] === "skip", order[0]);
  check("audio controls follow the skip link", order[1] === "ctl-tts" && order[2] === "ctl-vol", order.slice(0, 3).join(","));
  check("nav links reachable by Tab", order.includes("lesson") && order.includes("activity"), order.join(","));
  check("no guide nav link", !order.includes("guide"), order.join(","));

  console.log("\n== navigate to lesson ==");
  await page.click('[data-nav="lesson"]');
  await sleep(700);
  check("hash is #lesson", (await page.evaluate(() => location.hash)) === "#lesson");
  check("lesson view visible", await page.$eval("#view-lesson", el => !el.hidden));
  check("home hidden", await page.$eval("#view-home", el => el.hidden));
  check("lesson nav marked current", await page.$eval('[data-nav="lesson"]', el => el.getAttribute("aria-current") === "page"));
  check("focus moved to lesson heading", await page.evaluate(() => document.activeElement && document.activeElement.id === "lesson-title"));
  check("live region announced", /الدرس التفاعلي/.test(await page.$eval("#announce", el => el.textContent)));
  check("document title updated", (await page.title()).includes("الدرس التفاعلي"));
  const frameSrc = await page.$eval("#frame-lesson", f => f.getAttribute("src"));
  check("lesson frame got src", /^course\.html\?embed=1&voice=[mf]$/.test(frameSrc), frameSrc);
  const loaded = [...responses.entries()].filter(([u, s]) => u.includes("course.html") && s === 200);
  check("course.html responded 200", loaded.length > 0, JSON.stringify([...responses.keys()].filter(u => u.endsWith(".html"))));

  const frames = page.frames().map(f => f.url());
  check("course.html frame attached", frames.some(u => decodeURIComponent(u).includes("course.html")), frames.join(" | "));

  console.log("\n== embed mode inside frame ==");
  const lessonFrame = page.frames().find(fr => decodeURIComponent(fr.url()).includes("course.html"));
  const child = await lessonFrame.evaluate(() => {
    const hero = document.querySelector("header");
    return {
      embed: document.documentElement.classList.contains("embed"),
      heroShown: hero ? getComputedStyle(hero).display !== "none" : false,
      srH1: (document.querySelector(".sr-embed") || {}).textContent || null,
      scrollY: Math.round(scrollY),
      toolbarTop: Math.round(document.querySelector(".toolbar").getBoundingClientRect().top)
    };
  });
  check("child runs in embed mode", child.embed);
  check("child hero hidden", !child.heroShown);
  check("child has sr-only h1", !!child.srH1 && child.srH1.indexOf("التهديدات") > -1, child.srH1);
  check("child starts at scroll 0", child.scrollY === 0, String(child.scrollY));
  check("child toolbar visible at top", child.toolbarTop >= 0 && child.toolbarTop < 200, String(child.toolbarTop));

  // Tab order: the frame sits between the section heading + open button and the pager.
  await page.focus("#view-lesson .view-title .btn");
  await page.keyboard.press("Tab");
  const inFrame = await page.evaluate(() => document.activeElement && document.activeElement.tagName);
  check("Tab moves into the frame", inFrame === "IFRAME", inFrame);
  const childFocus = await lessonFrame.evaluate(() => {
    const a = document.activeElement;
    return a ? (a.id || a.tagName + "." + (a.className || "")) : "none";
  });
  check("focus lands inside lesson content", childFocus !== "none" && childFocus !== "BODY", childFocus);

  console.log("\n== geometry: single scrollbar, frame fills viewport ==");
  const geo = await page.evaluate(() => {
    const fc = document.querySelector("#view-lesson .frame-card").getBoundingClientRect();
    const ifr = document.querySelector("#frame-lesson").getBoundingClientRect();
    return {
      docH: document.documentElement.scrollHeight,
      winH: window.innerHeight,
      frameCardH: Math.round(fc.height),
      iframeH: Math.round(ifr.height),
      overflowX: document.documentElement.scrollWidth > window.innerWidth + 1
    };
  });
  check("no vertical page scroll in lesson view", geo.docH <= geo.winH + 2, JSON.stringify(geo));
  check("iframe taller than 400px", geo.iframeH > 400, String(geo.iframeH));
  check("no horizontal overflow", !geo.overflowX);

  await page.screenshot({ path: path.join(ROOT, "_preview", "hub-lesson.png") });

  console.log("\n== navigate activity ==");
  await page.click('[data-nav="activity"]');
  await sleep(900);
  check("activity frame src", /^index\.html\?embed=1&voice=[mf]$/.test(await page.$eval("#frame-activity", f => f.getAttribute("src"))));
  check("activity frame attached", page.frames().some(f => decodeURIComponent(f.url()).includes("index.html")));
  await page.screenshot({ path: path.join(ROOT, "_preview", "hub-activity.png") });

  check("guide section removed", (await page.$$("#view-guide")).length === 0);
  check("guide frame removed", page.frames().every(f => !decodeURIComponent(f.url()).includes("دليل_المرافق.html")));

  console.log("\n== Alt+1..3 shortcuts ==");
  await page.keyboard.down("Alt"); await page.keyboard.press("1"); await page.keyboard.up("Alt");
  await sleep(350);
  check("Alt+1 goes home", (await page.evaluate(() => location.hash)) === "#home");
  await page.keyboard.down("Alt"); await page.keyboard.press("3"); await page.keyboard.up("Alt");
  await sleep(350);
  check("Alt+3 goes activity", (await page.evaluate(() => location.hash)) === "#activity");
  await page.keyboard.down("Alt"); await page.keyboard.press("4"); await page.keyboard.up("Alt");
  await sleep(350);
  check("Alt+4 stays on activity (no fourth section)", (await page.evaluate(() => location.hash)) === "#activity",
    await page.evaluate(() => location.hash));

  console.log("\n== hash routing / back button ==");
  await page.evaluate(() => { location.hash = "#lesson"; });
  await sleep(350);
  check("hash #lesson shows lesson", await page.$eval("#view-lesson", el => !el.hidden));
  await page.goBack();
  await sleep(700);
  check("browser back returns to activity", await page.$eval("#view-activity", el => !el.hidden));
  await page.goForward();
  await sleep(700);
  check("browser forward returns to lesson", await page.$eval("#view-lesson", el => !el.hidden));

  console.log("\n== direct deep link ==");
  const page2 = await browser.newPage();
  await page2.setViewport({ width: 1280, height: 900 });
  await page2.goto(siteUrl + "#activity", { waitUntil: "load" });
  await sleep(800);
  check("deep link opens activity", await page2.$eval("#view-activity", el => !el.hidden));
  check("deep link lazy-loads frame", /^index\.html\?embed=1&voice=[mf]$/.test(await page2.$eval("#frame-activity", f => f.getAttribute("src"))));
  // legacy anchors still work
  const page3 = await browser.newPage();
  await page3.goto(siteUrl + "#panel-guide", { waitUntil: "load" });
  await sleep(600);
  check("legacy #panel-guide falls back to home", await page3.$eval("#view-home", el => !el.hidden));
  await page3.close();
  await page2.close();

  console.log("\n== responsive ==");
  for (const w of [1280, 900, 768, 400]) {
    await page.setViewport({ width: w, height: 900 });
    await page.evaluate(() => { location.hash = "#home"; });
    await sleep(350);
    const r = await page.evaluate(() => ({
      overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
      navVisible: document.querySelector(".nav").getBoundingClientRect().width > 0,
      cardW: Math.round(document.querySelector(".cards .card").getBoundingClientRect().width),
      btnH: Math.round(document.querySelector(".start-list .btn").getBoundingClientRect().height)
    }));
    check(`home ${w}px: no horizontal overflow`, !r.overflowX, JSON.stringify(r));
    check(`home ${w}px: CTA >= 44px tall`, r.btnH >= 44, String(r.btnH));
    if (w === 1280) await page.screenshot({ path: path.join(ROOT, "_preview", "hub-home-1280.png") });
    if (w === 400) await page.screenshot({ path: path.join(ROOT, "_preview", "hub-home-400.png"), fullPage: true });
  }

  await page.setViewport({ width: 1280, height: 900 });
  await page.evaluate(() => { location.hash = "#home"; });
  await sleep(300);
  await page.screenshot({ path: path.join(ROOT, "_preview", "hub-home.png"), fullPage: true });

  console.log("\n== JS errors ==");
  check("no page errors", errors.length === 0, errors.join(" | "));

  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error("FAIL", e); process.exit(2); });


