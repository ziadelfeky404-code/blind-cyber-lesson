# -*- coding: utf-8 -*-
"""Regenerate only the lesson quiz clips (question narration + feedback) after
removing the correct answer from the question narration."""
import asyncio
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("build_audio", os.path.join(HERE, "build-audio.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

import edge_tts

quiz_items = [it for it in mod.items if it[0].startswith("q")]


async def run():
    for sid, text in quiz_items + mod.feed:
        path = os.path.join(mod.AUDIO, sid + ".mp3")
        try:
            await edge_tts.Communicate(text, mod.VOICE, rate=mod.RATE).save(path)
            print("ok", sid, len(text))
        except Exception as exc:
            print("FAIL", sid, exc)


asyncio.run(run())
print("done")
