# -*- coding: utf-8 -*-
"""يتحقق من مقاطع النشاط والدرس في الصوتين: الوجود، الحجم، سلامة الفك، وتطابق المفاتيح.

التشغيل: python scripts\\verify-site-audio.py
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FFPROBE = Path(r"C:\Users\ziad elfky\AppData\Local\bin\ffprobe.exe")
sys.path.insert(0, str(HERE))
import voice  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), str(HERE / name))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def probe(path):
    out = subprocess.run(
        [str(FFPROBE), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def check_group(label, expected_keys, map_for, min_size=1000):
    ok = True
    total = 0.0
    for vk in ("m", "f"):
        keys = map_for(vk)
        missing_manifest = sorted(set(expected_keys) - set(keys))
        missing_file, empty, broken = [], [], []
        for key in sorted(set(expected_keys) & set(keys)):
            path = ROOT / keys[key]
            if not path.exists():
                missing_file.append(key)
                continue
            if path.stat().st_size < min_size:
                empty.append(key)
                continue
            dur = probe(path)
            if dur is None:
                broken.append(key)
            else:
                total += dur
        good = len(set(expected_keys) & set(keys)) - len(missing_file) - len(empty) - len(broken)
        print("%s [%s]: %d/%d سليم | مفقود %d | فارغ %d | تالف %d | بلا مدخل %d" % (
            label, vk, good, len(expected_keys), len(missing_file), len(empty), len(broken), len(missing_manifest)))
        if missing_file or empty or broken or missing_manifest:
            ok = False
            print("   عيّنة:", (missing_file + empty + broken + missing_manifest)[:8])
    print("%s: إجمالي المدة %.1f دقيقة" % (label, total / 60.0))
    return ok


def main():
    ok = True

    # ---------- النشاط ----------
    a = load("build-activity-audio.py")
    with open(ROOT / "audio" / "act" / "questions.json", encoding="utf-8") as f:
        questions = json.load(f)
    act_texts = a.build_texts(questions)
    act_keys = set(act_texts) | set(a.SFX_EXTRA)
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"const ACT_AUDIO = (\{.*?\});", html, re.S)
    if not m:
        print("NO ACT MANIFEST")
        return 1
    act_manifest = json.loads(m.group(1))
    if "f" not in act_manifest:
        print("ACT MANIFEST IS FLAT (لم يُحدَّث)")
        return 1
    ok &= check_group("النشاط", act_keys, lambda vk: act_manifest[vk])

    # ---------- الدرس ----------
    c = load("build-audio.py")
    course_keys = {sid for sid, _ in c.items} | {sid for sid, _ in c.feed}
    html = (ROOT / "course.html").read_text(encoding="utf-8")
    srcs = re.findall(r'data-a="([^"]+)"', html)
    expected_paths = {s for s in srcs}
    missing_html = [k + ".mp3" for k in sorted(course_keys) if k + ".mp3" not in expected_paths]
    print("الدرس: عناصر <audio> بـ data-a = %d | نصوص متوقعة = %d" % (len(expected_paths), len(course_keys)))
    if missing_html:
        print("   ملفات بلا عنصر صوت في الصفحة:", missing_html)
        ok = False
    for vk in ("m", "f"):
        missing_file, empty, broken = [], [], []
        total = 0.0
        for name in sorted(expected_paths):
            path = ROOT / "audio" / vk / name
            if not path.exists():
                missing_file.append(name)
                continue
            if path.stat().st_size < 1000:
                empty.append(name)
                continue
            dur = probe(path)
            if dur is None:
                broken.append(name)
            else:
                total += dur
        good = len(expected_paths) - len(missing_file) - len(empty) - len(broken)
        print("الدرس [%s]: %d/%d سليم | إجمالي %.1f دقيقة" % (vk, good, len(expected_paths), total / 60.0))
        if missing_file or empty or broken:
            ok = False
            print("   عيّنة:", (missing_file + empty + broken)[:8])
        full = ROOT / "audio" / vk / "narration_full.mp3"
        if not full.exists() or full.stat().st_size < 100000:
            print("   narration_full.mp3 مفقود أو صغير للصوت", vk)
            ok = False

    print("\nالنتيجة:", "سليم" if ok else "به مشاكل")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
