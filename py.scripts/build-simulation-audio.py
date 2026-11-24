# -*- coding: utf-8 -*-
"""يولّد المقاطع الصوتية للمحاكاة الواقعية وتحدي الإشعارات بصوتين (مذكر/مؤنث).

المصدر الوحيد للنصوص هو كائن SIM_TEXTS المكتوب داخل «النشاط التفاعلي.html»،
فلا يختلف المنطوق عن المكتوب. النص يُهيّأ بنفس طبقات voice.py المستخدمة في
بقية المشروع (نطق الأرقام والإنجليزية، وتشكيل المصطلحات، وصيغة المؤنث).

التشغيل: python py.scripts\\build-simulation-audio.py [--force]
"""
import asyncio
import json
import os
import re
import sys

import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import voice  # noqa: E402

PAGE = os.path.join(ROOT, "النشاط التفاعلي.html")
OUTDIR = os.path.join(ROOT, "audio", "sim")
CACHE = os.path.join(OUTDIR, ".texts.json")
CONCURRENCY = 6
# مؤثرات حقيقية جاهزة من النشاط الأصلي — لا تُولّد بالتلاوة الآلية
SFX = {
    "sfx.clap": "audio/act/clap.mp3",
    "sfx.buzz": "audio/act/buzz.mp3",
}


def read_texts():
    with open(PAGE, encoding="utf-8") as fh:
        html = fh.read()
    m = re.search(r"/\* SIM_TEXTS_START \*/\s*const SIM_TEXTS = (\{.*?\});\s*/\* SIM_TEXTS_END \*/",
                  html, re.S)
    if not m:
        raise SystemExit("SIM_TEXTS block not found in activity page")
    return json.loads(m.group(1))


def file_for(vk, key):
    return os.path.join(OUTDIR, vk, key.replace(".", "_") + ".mp3")


def inject_manifest(texts):
    manifest = {}
    for vk in voice.VOICES:
        manifest[vk] = {k: "audio/sim/%s/%s.mp3" % (vk, k.replace(".", "_"))
                        for k in sorted(texts)}
        for key, rel in SFX.items():
            manifest[vk][key] = rel
    block = "const SIM_AUDIO = " + json.dumps(manifest, ensure_ascii=False,
                                              separators=(",", ":")) + ";"

    with open(PAGE, encoding="utf-8") as fh:
        html = fh.read()
    pattern = re.compile(r"(/\* SIM_AUDIO_START \*/\s*)(const SIM_AUDIO = .*?;)(\s*/\* SIM_AUDIO_END \*/)", re.S)
    new_html, n = pattern.subn(lambda mm: mm.group(1) + block + mm.group(3), html, count=1)
    if n != 1:
        raise SystemExit("SIM_AUDIO block not found in activity page")
    with open(PAGE, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_html)
    return len(manifest["f"])


async def gen(sem, vk, key, text, force, cache):
    path = file_for(vk, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    spoken = voice.variants(text)[vk]
    if not force and not voice.needs_build(cache, vk, key, spoken, path):
        return key, "skip"
    async with sem:
        last = ""
        for attempt in range(4):
            try:
                await asyncio.wait_for(
                    edge_tts.Communicate(spoken, voice.VOICES[vk], rate=voice.RATE).save(path),
                    timeout=35,
                )
                if os.path.getsize(path) > 1000:
                    voice.mark_built(cache, vk, key, spoken)
                    return key, "ok"
                last = "small file"
            except Exception as exc:  # noqa: BLE001
                last = str(exc)
            await asyncio.sleep(1.5 * (attempt + 1))
        return key, "FAIL " + last


async def main():
    force = "--force" in sys.argv
    texts = read_texts()
    os.makedirs(OUTDIR, exist_ok=True)
    cache = voice.load_cache(CACHE)
    sem = asyncio.Semaphore(CONCURRENCY)
    print("simulation texts:", len(texts))
    for vk in voice.VOICES:
        print("== صوت %s (%s) ==" % (voice.VOICE_LABEL[vk], voice.VOICES[vk]))
        results = await asyncio.gather(*[gen(sem, vk, k, t, force, cache)
                                         for k, t in texts.items()])
        failed = [r for r in results if r[1].startswith("FAIL")]
        print("  ok:", len([r for r in results if r[1] == "ok"]),
              "skip:", len([r for r in results if r[1] == "skip"]),
              "failed:", len(failed))
        for f in failed[:10]:
            print("   FAIL", f[0], f[1])
        voice.save_cache(CACHE, cache)
        if failed:
            raise SystemExit(1)
    n = inject_manifest(texts)
    total = sum(os.path.getsize(os.path.join(base, f))
                for base, _dirs, files in os.walk(OUTDIR) for f in files
                if f.endswith(".mp3"))
    print("manifest entries per voice:", n)
    print("total MB: %.2f" % (total / 1048576.0))


if __name__ == "__main__":
    asyncio.run(main())
