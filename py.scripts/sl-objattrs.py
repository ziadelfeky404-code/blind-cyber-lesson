import zipfile
import re

z = zipfile.ZipFile(r"C:\Program Files (x86)\Articulate\Storyline 3\Content\Templates\Velocity 16x9.storytemplate")
names = [n for n in z.namelist() if n.startswith("story/slides/") and n.endswith(".xml")]
attrs = {}
samples = {}
for n in names:
    s = z.read(n).decode("utf-8-sig")
    for em in re.finditer(r"<([A-Za-z]+)([^>]*)>", s):
        tag = em.group(1)
        for am in re.finditer(r'([A-Za-z]+)="([^"]*)"', em.group(2)):
            k = (tag, am.group(1))
            attrs[k] = attrs.get(k, 0) + 1
            if k not in samples:
                samples[k] = am.group(2)[:50]

print("=== attrs matching dir/rtl/just/align/lang/para/bidi ===")
for (t, a), c in sorted(attrs.items()):
    if any(x in a.lower() for x in ["dir", "rtl", "just", "align", "lang", "para", "bidi"]):
        print(f"  {t}.{a} x{c} e.g. {samples[(t,a)]!r}")

print("\n=== all distinct attribute names (any element) ===")
seen = sorted({a for (t, a) in attrs})
print(seen)
