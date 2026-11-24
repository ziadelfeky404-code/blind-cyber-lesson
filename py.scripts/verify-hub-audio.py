# -*- coding: utf-8 -*-
"""يتحقق من وجود كل مقطع صوتي في الصوتين وأنه سليم (عبر ffprobe).

يقرأ المانيفست من الموقع.html (شكل {f:{...}, m:{...}})، ويقارن مفاتيحه بـ TEXTS
في مولّد الصوت، ثم يتأكد أن كل مسار في المانيفست موجود وقابل للفك.

التشغيل: python scripts\\verify-hub-audio.py
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "الموقع.html"
FFPROBE = Path(r"C:\Users\ziad elfky\AppData\Local\bin\ffprobe.exe")

spec = importlib.util.spec_from_file_location("builder", str(ROOT / "scripts" / "build-hub-audio.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["builder"] = mod
spec.loader.exec_module(mod)

src = HTML.read_text(encoding="utf-8")
m = re.search(r"/\* HUB_AUDIO_START \*/\s*const HUB_AUDIO = (\{.*?\});\s*/\* HUB_AUDIO_END \*/", src, re.S)
if not m:
    print("NO MANIFEST")
    sys.exit(1)
manifest = json.loads(m.group(1))

if "f" not in manifest or "m" not in manifest:
    print("MANIFEST IS NOT PER-VOICE:", list(manifest)[:5])
    sys.exit(1)

# مفاتيح مطلوبة: كل نصوص TEXTS + المؤثرات
needed = set(mod.TEXTS) | set(getattr(mod, "SFX", {}))
ok = True
for vk in ("m", "f"):
    keys = set(manifest[vk])
    absent = sorted(needed - keys)
    extra = sorted(keys - needed)
    missing, empty, broken = [], [], []
    durations = 0.0
    for key in sorted(needed & keys):
        path = ROOT / manifest[vk][key]
        if not path.exists():
            missing.append(key)
            continue
        if path.stat().st_size < 1200:
            empty.append(key)
            continue
        out = subprocess.run(
            [str(FFPROBE), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        try:
            durations += float(out.stdout.strip())
        except ValueError:
            broken.append("%s: %s" % (key, out.stderr.strip()[:70]))

    good = len(needed & keys) - len(missing) - len(empty) - len(broken)
    print("== صوت %s: %d/%d مقطعًا سليمًا، %d مفقود، %d فارغ، %d تالف" % (
        vk, good, len(needed), len(missing), len(empty), len(broken)))
    print("   مدخلات المانيفست: %d | بلا مفتاح: %s | زائدة: %s" % (
        len(keys), absent[:6] or "لا شيء", extra[:6] or "لا شيء"))
    print("   إجمالي المدة: %.1f دقيقة" % (durations / 60.0))
    if missing or empty or broken or absent:
        ok = False
        for label, items in (("missing", missing), ("empty", empty), ("broken", broken)):
            if items:
                print("   %s: %s" % (label, items[:10]))

# تطابق المفاتيح بين الصوتين
same = set(manifest["f"]) == set(manifest["m"])
print("مفاتيح الصوتين متطابقة:", "نعم" if same else "لا")
paths_ok = True
for key in manifest["f"]:
    pf, pm = manifest["f"][key], manifest["m"][key]
    if key in ("sfx.clap", "sfx.buzz"):
        if pf != pm:
            paths_ok = False
            print("  مؤثر غير مشترك:", key)
    elif "/f/" not in pf or "/m/" not in pm:
        paths_ok = False
        print("  مسار في مجلد خطأ:", key, pf, pm)
print("المسارات في مجلداتها:", "نعم" if paths_ok else "لا")
sys.exit(0 if (ok and same and paths_ok) else 1)
