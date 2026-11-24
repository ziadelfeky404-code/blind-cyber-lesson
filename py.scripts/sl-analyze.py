import zipfile
import re

TPL = r"C:\Program Files (x86)\Articulate\Storyline 3\Content\Templates\Velocity 16x9.storytemplate"
z = zipfile.ZipFile(TPL)
s6 = z.read("story/slides/slide6.xml").decode("utf-8")

m = re.search(r"<slide [^>]*>", s6)
print("SLIDE6 ROOT:", m.group(0)[:500])
print()

print("OBJECTS WITH NAMES:")
for mm in re.finditer(r'<(rect|textBox|pic|shape)\b([^>]*)>', s6):
    nm = re.search(r'name="([^"]*)"', mm.group(2))
    gid = re.search(r'\bg="([^"]*)"', mm.group(2))
    if nm:
        print(f"  {mm.group(1):9s} name={nm.group(1)!r} g={gid.group(1) if gid else ''}")

print()
print("TEXT SPANS (Span Text=...):")
for mm in re.finditer(r'<text>(.*?)</text>', s6, re.S):
    spans = re.findall(r'<Span Text="([^"]*)"', mm.group(1))
    print("  payload spans:", spans)
