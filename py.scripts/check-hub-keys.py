# -*- coding: utf-8 -*-
"""يتأكد أن كل مفتاح صوتي مستخدم في الموقع موجود في نصوص مولّد الصوت."""
import importlib.util
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "الموقع.html"
PY = ROOT / "scripts" / "build-hub-audio.py"

spec = importlib.util.spec_from_file_location("builder", str(PY))
mod = importlib.util.module_from_spec(spec)
sys.modules["builder"] = mod
spec.loader.exec_module(mod)

src = io.open(HTML, encoding="utf-8").read()
used = set()
for m in re.finditer(r'data-speak="([^"]+)"', src):
    used.update(m.group(1).split())
# مفاتيح تُشغَّل من JavaScript مباشرة: speak("...") أو say("...")
for m in re.finditer(r'\b(?:speak|say)\(\s*"([a-z0-9.]+)"', src):
    used.add(m.group(1))

texts = set(mod.TEXTS)
print("used:", len(used), "| texts:", len(texts))
missing = sorted(used - texts)
unused = sorted(texts - used)
print("missing in TEXTS:", missing)
print("unused in TEXTS:", unused)
