import time

t = time.time()
from faster_whisper import WhisperModel

m = WhisperModel("tiny", device="cpu", compute_type="int8")
print("model ready in", round(time.time() - t, 1), "s")
