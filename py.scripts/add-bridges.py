# -*- coding: utf-8 -*-
"""Add spoken "bridge" sentences that link each slide to the one before it.

The bridges are connective wording only (no new facts); all lesson content
stays exactly as it is in course.json / the book.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
COURSE = os.path.join(ROOT, "course.json")

BRIDGES = {
    "s02": "قبل أن نبدأ، نعرض ما سنتعلمه في هذا الدرس.",
    "s03": "نبدأ بمراجعة ما تعلمناه في الدرس السابق، لنبني عليه.",
    "s03b": "ما المقصود بالتهديدات السيبرانية المتقدمة؟ نحدد المفهوم أولًا.",
    "s04": "أول أنواع هذه التهديدات: برامج الفدية.",
    "s04b": "بعد أن عرفنا برامج الفدية، ننتقل إلى كيفية الحماية منها.",
    "s04c": "النوع الثاني يستهدف الإنسان نفسه: الهندسة الاجتماعية المتقدمة.",
    "s05": "أول أساليب الهندسة الاجتماعية: التصيد الاحتيالي الموجه.",
    "s06": "الأسلوب الثاني: انتحال الشخصية.",
    "s07": "الأسلوب الثالث: الاستدراج.",
    "s08": "بعد أساليب خداع الإنسان، ننتقل إلى هجوم يستهدف الخدمة نفسها: هجمات الحرمان من الخدمة الموزعة.",
    "s08b": "بعد أن عرفنا أنواع التهديدات، نرتب التصرفات الآمنة التي نتبعها.",
    "s09": "نطبّق ما تعلمناه على موقف من الحياة اليومية.",
    "s10": "نلخص الدرس في نقاط سريعة.",
}

with open(COURSE, encoding="utf-8") as f:
    data = json.load(f)

added = 0
for slide in data["slides"]:
    bridge = BRIDGES.get(slide["id"])
    if bridge and slide.get("bridge") != bridge:
        slide["bridge"] = bridge
        added += 1

with open(COURSE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("bridges added/updated:", added)
for slide in data["slides"]:
    print(slide["id"], "->", slide.get("bridge", "-"))
