import zipfile
import html
import re
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.abspath(os.path.join(HERE, "..", "التهديدات_السيبرانية_المتقدمة.story"))

z = zipfile.ZipFile(STORY)
rels = z.read("story/_rels/story.xml.rels").decode("utf-8-sig")
id2target = {}
for typ, tgt, rid in re.findall(r'<Relationship Type="([^"]+)" Target="([^"]+)" Id="([^"]+)"', rels):
    id2target[rid] = tgt
story = z.read("story/story.xml").decode("utf-8-sig")
sldids = re.findall(r"<sldId>([^<]+)</sldId>", story)
ordered = [id2target[i].lstrip("/") for i in sldids if i in id2target]

for idx in [0, 1, 3, 13, 14]:
    raw = z.read(ordered[idx]).decode("utf-8-sig")
    print(f"\n===== slot {idx}: {ordered[idx]} =====")
    for bm in re.finditer(r"<text>(.*?)</text>", raw, re.S):
        dec = html.unescape(bm.group(1))
        for sm in re.finditer(r'<Span Text="([^"]*)"', dec):
            t = sm.group(1)
            if t.strip():
                t2 = t.replace("&#xA;", "\n    ")
                print("   TEXT:", t2[:300])
                break
