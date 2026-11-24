# -*- coding: utf-8 -*-
"""تقرير جودة النصوص المنطوقة: لاتينية، أرقام، بريد، وقواعد مؤنث غير مستخدمة."""
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import voice

spec = importlib.util.spec_from_file_location("h", "scripts/build-hub-audio.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

spec = importlib.util.spec_from_file_location("c", "scripts/build-audio.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

spec = importlib.util.spec_from_file_location("a", "scripts/build-activity-audio.py")
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

qs = json.load(open("audio/act/questions.json", encoding="utf-8"))
act = a.build_texts(qs)

corpus = {}
corpus.update({("hub", k): v for k, v in h.TEXTS.items()})
corpus.update({("slide", k): v for k, v in c.items})
corpus.update({("feed", k): v for k, v in c.feed})
corpus.update({("act", k): v for k, v in act.items()})

bad = 0
fem_only = 0
for (src, k), raw in corpus.items():
    v = voice.variants(raw)
    for tag in ("m", "f"):
        t = v[tag]
        if re.search(r"[A-Za-z@]", t):
            print(f"  لاتيني [{src}/{k}/{tag}]: {t[:120]}")
            bad += 1
        if re.search(r"[0-9]", t):
            print(f"  أرقام [{src}/{k}/{tag}]: {t[:120]}")
            bad += 1
        if "  " in t or " ،" in t or " ." in t or ".." in t.replace("...", ""):
            print(f"  ترقيم [{src}/{k}/{tag}]: {t[:120]}")
            bad += 1

print("نصوص:", len(corpus), "| مشاكل:", bad)
print("\n--- قواعد مؤنث لم تُطبَّق ---")
print(voice.unused_rules(voice.FEM, [raw for raw in corpus.values()]))

print("\n--- نماذج من صيغة المؤنث ---")
for key in ["e.skip", "n.lesson", "v.home", "kt.title", "lp.intro", "kb.dialogue", "v.help"]:
    print("•", key)
    print("   م:", voice.variants(h.TEXTS[key])["m"][:160])
    print("   ف:", voice.variants(h.TEXTS[key])["f"][:160])
