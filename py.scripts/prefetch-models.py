import time
from faster_whisper import WhisperModel

for name in ("base", "small"):
    t = time.time()
    WhisperModel(name, device="cpu", compute_type="int8")
    print(name, "ready in", round(time.time() - t, 1), "s", flush=True)
print("ALL_MODELS_READY")
