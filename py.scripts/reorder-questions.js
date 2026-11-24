/* Reorder the activity questions so they follow the lesson sequence:
   ransomware -> social engineering (phishing, pretexting, baiting) -> DDoS -> safe behaviour.
   Content is unchanged; only the order changes. */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "index.html");
let html = fs.readFileSync(PAGE, "utf8");

const start = html.indexOf("const QUESTIONS = [");
if (start < 0) throw new Error("QUESTIONS not found");
const end = html.indexOf("\n];", start);
if (end < 0) throw new Error("QUESTIONS end not found");

const literal = html.slice(start + "const QUESTIONS = ".length, end + "\n];".length - 1);
const QUESTIONS = eval(literal);
if (!Array.isArray(QUESTIONS) || QUESTIONS.length !== 10) {
  throw new Error("unexpected questions length: " + (QUESTIONS && QUESTIONS.length));
}

/* 1-based positions in the current array, in the new logical order */
const NEW_ORDER = [4, 1, 7, 8, 2, 3, 5, 6, 9, 10];
const next = NEW_ORDER.map((n) => QUESTIONS[n - 1]);

function q(s) {
  return JSON.stringify(s);
}

const body = next
  .map(
    (item) =>
      "  {\n" +
      "    context: " + q(item.context) + ",\n" +
      "    question: " + q(item.question) + ",\n" +
      "    options: [\n" +
      item.options.map((o) => "      " + q(o)).join(",\n") + "\n" +
      "    ],\n" +
      "    correct: " + item.correct + ",\n" +
      "    feedback: " + q(item.feedback) + "\n" +
      "  }"
  )
  .join(",\n");

const block = "const QUESTIONS = [\n" + body + "\n];";
html = html.slice(0, start) + block + html.slice(end + "\n];".length);
fs.writeFileSync(PAGE, html, "utf8");
console.log("reordered questions ->", NEW_ORDER.join(", "));
