import zipfile
import re

TPL = r"C:\Program Files (x86)\Articulate\Storyline 3\Content\Templates\Velocity 16x9.storytemplate"
z = zipfile.ZipFile(TPL)
s = z.read("story/story.xml").decode("utf-8")

for tag in ["sceneLst", "toc"]:
    m = re.search(rf"<{tag}\b.*?</{tag}>", s, re.S)
    if not m:
        m = re.search(rf"<{tag}\b[^>]*/>", s, re.S)
    print(f"===== {tag} =====")
    print(m.group(0)[:3000] if m else "NOT FOUND (maybe self-closed / empty)")
    print()

for t in ["sceneLst", "toc", "sldIdLst", "refG", "corG", "sldId"]:
    print(t, s.count("<" + t))
