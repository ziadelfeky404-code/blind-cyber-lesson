# -*- coding: utf-8 -*-
"""فحص مسموع للنصوص: يحوّل مقاطع مولّدة إلى نص (Whisper) ويقارنها بالنص المتوقع.

الهدف: كشف الكلمات التي قرأها المحرّك الآلي خطأً (تشكيل خاطئ، إضافة/حذف حرف،
نطق رقم أو رمز) قبل أن يسمعها المتعلم. الأداة تشخيصية: تُطبع نسبة الخطأ لكل
مقطع مرتبة تنازليًا، ولا تعدّل شيئًا.

التشغيل:
    python scripts\\qa-asr.py --src hub --limit 20 [--voice f] [--model small]
"""
import argparse
import importlib.util
import os
import re
import sys
import difflib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

FFMPEG = os.path.expandvars(r"%LOCALAPPDATA%\bin\ffmpeg.exe")

AR_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]")
NORM = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ة": "ه", "ى": "ي", "ئ": "ي", "ؤ": "و",
    "ـ": "",
})


def norm_words(t):
    t = AR_DIAC.sub("", t)
    t = t.translate(NORM)
    # الأرقام والرموز اللاتينية تُسقط من المقارنة (المحرّك ينطقها بألفاظ)
    t = re.sub(r"[A-Za-z]+", " ", t)
    t = re.sub(r"[^\u0621-\u064A\s]", " ", t)
    return [w for w in t.split() if w]


def wer(expected, got):
    a, b = norm_words(expected), norm_words(got)
    if not a:
        return 0.0, a, b
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    dist = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")
    return dist / float(len(a)), a, b


def load_audio(path, sr=16000):
    import subprocess
    import numpy as np
    import shutil
    ffmpeg = FFMPEG if os.path.exists(FFMPEG) else (shutil.which("ffmpeg") or "ffmpeg")
    raw = subprocess.run(
        [ffmpeg, "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype="int16").astype("float32") / 32768.0


def texts_for(src):
    """يرجع {مفتاح: نص} للنصوص المخزَّنة في نفس مجلد المقاطع."""
    if src == "hub":
        spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "build-hub-audio.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["b"] = mod
        spec.loader.exec_module(mod)
        return dict(mod.TEXTS), os.path.join(ROOT, "audio", "hub")
    if src == "act":
        import json
        spec = importlib.util.spec_from_file_location("a", os.path.join(HERE, "build-activity-audio.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["a"] = mod
        spec.loader.exec_module(mod)
        with open(os.path.join(ROOT, "audio", "act", "questions.json"), encoding="utf-8") as f:
            return mod.build_texts(json.load(f)), os.path.join(ROOT, "audio", "act")
    if src == "course":
        spec = importlib.util.spec_from_file_location("c", os.path.join(HERE, "build-audio.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["c"] = mod
        spec.loader.exec_module(mod)
        return dict(mod.items + mod.feed), os.path.join(ROOT, "audio")
    raise SystemExit("src غير معروف: " + src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", choices=["hub", "act", "course"], default="hub")
    ap.add_argument("--voice", choices=["m", "f"], default="f")
    ap.add_argument("--limit", type=int, default=20, help="أقصى عدد مقاطع للفحص")
    ap.add_argument("--model", default="small")
    ap.add_argument("--all", action="store_true", help="افحص كل مقطع (بطيء)")
    ap.add_argument("--keys", default="", help="مفاتيح محددة مفصولة بفاصلة")
    args = ap.parse_args()

    sys.path.insert(0, HERE)
    import voice as vmod

    texts, base = texts_for(args.src)
    vdir = os.path.join(base, args.voice)
    if not os.path.isdir(vdir):
        vdir = base  # النشاط القديم بلا مجلدات صوت

    items = []
    for k, raw in texts.items():
        path = os.path.join(vdir, k.replace(".", "_") + ".mp3")
        if os.path.exists(path):
            items.append((k, vmod.variants(raw)[args.voice], path))
    if args.keys:
        want = set(args.keys.split(","))
        items = [x for x in items if x[0] in want]
    elif not args.all:
        # عيّنة موجّهة: النصوص الطويلة والأكثر عرضة للخطأ
        items.sort(key=lambda x: -len(x[1]))
        items = items[:args.limit]

    print("صوت %s | %d مقطعًا | نموذج %s" % (args.voice, len(items), args.model))
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    rows = []
    for i, (key, expected, path) in enumerate(items, 1):
        audio = load_audio(path)
        segments, _info = model.transcribe(audio, language="ar", beam_size=5, vad_filter=False)
        got = " ".join(s.text.strip() for s in segments)
        ratio, a, b = wer(expected, got)
        rows.append((ratio, key, expected, got, a, b))
        print("  [%d/%d] %-16s خطأ %5.1f%%" % (i, len(items), key, ratio * 100), flush=True)

    rows.sort(reverse=True)
    print("\n== ترتيب الأسوأ أولًا (نسبة الخطأ) ==")
    for ratio, key, expected, got, a, b in rows:
        flag = "  <-- راجع" if ratio >= 0.2 else ""
        print("%5.1f%% %-16s%s" % (ratio * 100, key, flag))
    bad = [r for r in rows if r[0] >= 0.2]
    print("\nمقاطع تحتاج مراجعة (>= 20%%): %d / %d" % (len(bad), len(rows)))
    for ratio, key, expected, got, a, b in bad[:6]:
        print("\n--- %s (%.0f%%) ---" % (key, ratio * 100))
        print("  متوقع:", " ".join(a))
        print("  مسموع:", " ".join(b))
    sys.exit(0)


if __name__ == "__main__":
    main()
