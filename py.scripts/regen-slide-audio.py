# -*- coding: utf-8 -*-
"""Regenerate only the lesson slide narration (after adding bridge sentences)."""
import asyncio
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("build_audio", os.path.join(HERE, "build-audio.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

import edge_tts

slide_items = [it for it in mod.items if not it[0].startswith("q")]


async def run():
    for sid, text in slide_items:
        path = os.path.join(mod.AUDIO, sid + ".mp3")
        try:
            await edge_tts.Communicate(text, mod.VOICE, rate=mod.RATE).save(path)
            print("ok", sid, len(text))
        except Exception as exc:
            print("FAIL", sid, exc)


asyncio.run(run())
print("done")
