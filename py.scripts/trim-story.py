import zipfile
import re
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
STORY_DIR = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(STORY_DIR, "التهديدات_السيبرانية_المتقدمة.story")
FULL = os.path.join(STORY_DIR, "التهديدات_السيبرانية_المتقدمة_full.story")
TMP = os.path.join(STORY_DIR, "trimmed.story")

KEEP = 22

z = zipfile.ZipFile(OUT)
rels = z.read("story/_rels/story.xml.rels").decode("utf-8-sig")
id2target = {rid: tgt for typ, tgt, rid in
             re.findall(r'<Relationship Type="([^"]+)" Target="([^"]+)" Id="([^"]+)"', rels)}
story = z.read("story/story.xml").decode("utf-8-sig")

sldids = re.findall(r"<sldId>([^<]+)</sldId>", story)
keep_ids = sldids[:KEEP]

guids = set()
for i in keep_ids:
    tgt = id2target[i].lstrip("/")
    raw = z.read(tgt)
    m = re.search(rb'<sld\b[^>]*?\bg="([^"]+)"', raw)
    if m:
        guids.add(m.group(1).decode())

new_lst = "<sldIdLst>" + "".join(f"<sldId>{i}</sldId>" for i in keep_ids) + "</sldIdLst>"
story2 = re.sub(r"<sldIdLst>.*?</sldIdLst>", new_lst, story, count=1, flags=re.S)

removed = [0]


def toc_repl(m):
    entry = m.group(0)
    rg = re.search(r'refG="([^"]+)"', entry)
    if rg and rg.group(1) not in guids:
        removed[0] += 1
        return ""
    return entry


story2 = re.sub(r"<tocSlideEntry\b.*?</tocSlideEntry>", toc_repl, story2, flags=re.S)
print("kept slides:", KEEP, "| removed toc entries:", removed[0])

with zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in z.infolist():
        if item.filename == "story/story.xml":
            zout.writestr(item, story2.encode("utf-8"))
        else:
            zout.writestr(item, z.read(item.filename))
z.close()
print("wrote trimmed:", TMP, os.path.getsize(TMP), "bytes")

shutil.move(TMP, OUT)
print("final:", OUT, os.path.getsize(OUT), "bytes")
