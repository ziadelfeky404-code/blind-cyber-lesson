import zipfile
import html
import re

TPL = r"C:\Program Files (x86)\Articulate\Storyline 3\Content\Templates\Velocity 16x9.storytemplate"
z = zipfile.ZipFile(TPL)
names = [n for n in z.namelist() if re.match(r"story/slides/slide\d+\.xml$", n)]
names.sort(key=lambda n: int(re.search(r"(\d+)", n.split("/")[-1]).group(1)))
print("total slides:", len(names))
for n in names:
    s = z.read(n).decode("utf-8")
    g = re.search(r'<sld [^>]*g="([^"]+)"', s)
    blocks = re.findall(r"<text>(.*?)</text>", s, re.S)
    print(f"\n### {n}  g={g.group(1) if g else '?'}  blocks={len(blocks)}")
    for i, b in enumerate(blocks):
        dec = html.unescape(b)
        spans = re.findall(r'<Span Text="([^"]*)"', dec)
        sizes = re.findall(r'FontSize="([^"]*)"', dec)
        bolds = re.findall(r'FontIsBold="([^"]*)"', dec)
        for j, sp in enumerate(spans):
            sz = sizes[j] if j < len(sizes) else "?"
            bd = bolds[j] if j < len(bolds) else "?"
            print(f"   b{i}.s{j} size={sz} bold={bd} :: {sp[:60]!r}")
