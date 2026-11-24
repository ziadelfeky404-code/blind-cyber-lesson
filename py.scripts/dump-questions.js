/**
 * يستخرج QUESTIONS من index.html إلى audio/act/questions.json
 * حتى يبقى نص الصوت مطابقًا تمامًا لنص الصفحة (مصدر واحد).
 */
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const page = path.join(root, "index.html");
const outDir = path.join(root, "audio", "act");

const s = fs.readFileSync(page, "utf8");
const marker = "const QUESTIONS = [";
const start = s.indexOf(marker);
if (start < 0) throw new Error("QUESTIONS not found in index.html");
const end = s.indexOf("\n];", start);
if (end < 0) throw new Error("QUESTIONS array end not found");
const src = s.slice(start + marker.length - 1, end + 2);
const QUESTIONS = eval(src);

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "questions.json"), JSON.stringify(QUESTIONS, null, 1), "utf8");
console.log("questions:", QUESTIONS.length, "options:", QUESTIONS.reduce((a, q) => a + q.options.length, 0));
