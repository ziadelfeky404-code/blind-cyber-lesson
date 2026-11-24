import zipfile
import html
import re

z = zipfile.ZipFile(r"C:\Program Files (x86)\Articulate\Storyline 3\Content\Templates\Velocity 16x9.storytemplate")
names = [n for n in z.namelist() if n.startswith("story/slides/") and n.endswith(".xml")]
attrs = {}
samples = {}
for n in names:
    s = z.read(n).decode("utf-8-sig")
    for bm in re.finditer(r"<text>(.*?)</text>", s, re.S):
        dec = html.unescape(bm.group(1))
        for em in re.finditer(r"<([A-Za-z]+)([^>]*)>", dec):
            tag = em.group(1)
            body = em.group(2)
            for am in re.finditer(r'([A-Za-z]+)="([^"]*)"', body):
                key = (tag, am.group(1))
                attrs[key] = attrs.get(key, 0) + 1
                if key not in samples:
                    samples[key] = am.group(2)[:40]
for (tag, a), c in sorted(attrs.items()):
    print(f"{tag}.{a}  x{c}  e.g. {samples[(tag,a)]!r}")
