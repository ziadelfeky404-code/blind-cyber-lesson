# -*- coding: utf-8 -*-
"""Build a real Articulate Storyline 3 project (.story) from course.json.

Method: open the official Storyline 3 template (Velocity 16x9.storytemplate),
write the course content into its existing slides, then drop the unused slides
(trim-story.py keeps the first 22).

Key detail: inside <text>...</text> the document is HTML-escaped, so markup
appears as &lt;Span Text="..."&gt;. Quotes that belong to the text itself are
stored as &quot;, therefore matching on the ESCAPED payload is unambiguous.
Matching after html.unescape() breaks as soon as a template string contains a
quote, which is what left English template text behind.
"""
import zipfile
import re
import json
import os

TPL = r"C:\Program Files (x86)\Articulate\Storyline 3\Content\Templates\Velocity 16x9.storytemplate"
HERE = os.path.dirname(os.path.abspath(__file__))
STORY_DIR = os.path.abspath(os.path.join(HERE, ".."))
COURSE = os.path.join(STORY_DIR, "course.json")
OUT = os.path.join(STORY_DIR, "التهديدات_السيبرانية_المتقدمة.story")

with open(COURSE, encoding="utf-8") as f:
    data = json.load(f)

items = []
for s in data["slides"]:
    lines = []
    if s.get("subtitle"):
        lines.append(s["subtitle"])
    if s.get("meta"):
        lines.append(s["meta"])
    if s.get("intro"):
        lines.append(s["intro"])
    for b in s.get("bullets", []):
        lines.append("• " + b)
    if s.get("email"):
        e = s["email"]
        lines.append("من: " + e["from"])
        lines.append("الموضوع: " + e["subject"])
        lines.append(e["body"])
    if s.get("question"):
        lines.append(s["question"])
    if s.get("answer"):
        lines.append("التصرف الآمن: " + s["answer"])
    items.append((s.get("title", ""), lines))

for q in data["quiz"]:
    lines = [q["question"]]
    letters = ["أ", "ب", "ج", "د"]
    for i, o in enumerate(q["options"]):
        lines.append(f"{letters[i]}) {o}")
    lines.append("الإجابة الصحيحة: " + letters[q["correct"]] + " — " + q["options"][q["correct"]])
    items.append(("سؤال تقويمي: " + q["objective"], lines))

print("content items:", len(items))


def esc_text(t):
    """Escape a value for insertion into the escaped <text> payload."""
    t = t.replace("&", "&amp;")
    t = t.replace('"', "&quot;")
    t = t.replace("<", "&lt;").replace(">", "&gt;")
    return t


SPAN_RE = r'(&lt;Span Text=")([^"]*)(")'


WRAP_RE = r"<(text|fmtText)>(.*?)</\1>"


def analyze_block(payload):
    """Return [(index, fontsize, bold, text)] for spans inside one escaped document."""
    spans = []
    idx = 0
    for sm in re.finditer(r'&lt;Span Text="([^"]*)"', payload):
        tail = payload[sm.end():sm.end() + 400]
        fs = re.search(r'FontSize="([^"]+)"', tail)
        fb = re.search(r'FontIsBold="([^"]+)"', tail)
        try:
            size = float(fs.group(1)) if fs else 0.0
        except ValueError:
            size = 0.0
        bold = (fb.group(1).lower() == "true") if fb else False
        spans.append((idx, size, bold, sm.group(1)))
        idx += 1
    return spans


def is_label(text):
    """Template decoration: pure numbers, ALL-CAPS labels, empty strings."""
    t = text.strip()
    if not t:
        return True
    if re.fullmatch(r"[0-9]{1,3}", t):
        return True
    if re.fullmatch(r"[A-Z0-9 &'’\-\.,!/]{2,60}", t):
        return True
    return False


def decide(spans):
    """Pick the title span (biggest real heading) and body span (longest text)."""
    if not spans:
        return None, None
    real = [s for s in spans if not is_label(s[3])]
    if not real:
        real = spans
    title = max(real, key=lambda s: (s[1], 1 if s[2] else 0))
    rest = [s for s in spans if s[0] != title[0]]
    rest_real = [s for s in rest if not is_label(s[3])] or rest
    body = max(rest_real, key=lambda s: len(s[3])) if rest_real else None
    return title[0], (body[0] if body else None)


def rewrite(raw, title, lines, do_fill=True):
    title_esc = esc_text(title)
    body_esc = "&#xA;".join(esc_text(l) for l in lines)

    def block_repl(wm):
        tag, payload = wm.group(1), wm.group(2)
        spans = analyze_block(payload)
        title_i, body_i = decide(spans) if do_fill else (None, None)
        t_val = title_esc
        if do_fill and body_i is None:
            t_val = title_esc + "&#xA;" + body_esc
        counter = [0]

        def span_repl(m):
            g = counter[0]
            counter[0] += 1
            if g == title_i:
                nv = t_val
            elif body_i is not None and g == body_i:
                nv = body_esc
            else:
                nv = ""
            return m.group(1) + nv + m.group(3)

        s = re.sub(SPAN_RE, span_repl, payload)
        s = s.replace('Justification="Left"', 'Justification="Right"')
        s = s.replace('FlowDirection="LeftToRight"', 'FlowDirection="RightToLeft"')
        return "<" + tag + ">" + s + "</" + tag + ">"

    return re.sub(WRAP_RE, block_repl, raw, flags=re.S)


def make_rtl(raw):
    raw = raw.replace('rtl="false"', 'rtl="true"')
    raw = raw.replace('defHorzAlign="l"', 'defHorzAlign="r"')
    raw = raw.replace('Justification="Left"', 'Justification="Right"')
    return raw


zin = zipfile.ZipFile(TPL)
rels = zin.read("story/_rels/story.xml.rels").decode("utf-8-sig")
id2target = {}
for typ, tgt, rid in re.findall(r'<Relationship Type="([^"]+)" Target="([^"]+)" Id="([^"]+)"', rels):
    if typ == "slide":
        id2target[rid] = tgt
story = zin.read("story/story.xml").decode("utf-8-sig")
sldids = re.findall(r"<sldId>([^<]+)</sldId>", story)
print("sldId count:", len(sldids))

ordered = []
for sid in sldids:
    tgt = id2target.get(sid)
    if tgt:
        ordered.append(tgt.lstrip("/"))
print("ordered slide files:", len(ordered))

new_slides = {}
for i, f in enumerate(ordered):
    raw = zin.read(f).decode("utf-8-sig")
    if i < len(items):
        title, lines = items[i]
        new_slides[f] = make_rtl(rewrite(raw, title, lines, True))
    else:
        new_slides[f] = make_rtl(rewrite(raw, "", [], False))

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename in new_slides:
            zout.writestr(item, new_slides[item.filename].encode("utf-8"))
        else:
            zout.writestr(item, zin.read(item.filename))
zin.close()
print("wrote:", OUT, os.path.getsize(OUT), "bytes")
print("mapped", min(len(items), len(ordered)), "slides; blanked", max(0, len(ordered) - len(items)))
