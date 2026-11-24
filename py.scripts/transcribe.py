import subprocess
import numpy as np
from faster_whisper import WhisperModel

VIDEO = r"D:\projects\instrucsal design\media-work\video\التهديدات_السيبرانية_المتقدمة.mp4"
CAPT = r"D:\projects\instrucsal design\media-work\captions"


def fmt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def load_audio(path):
    import subprocess, os, shutil
    ffmpeg = shutil.which("ffmpeg") or os.path.expandvars(r"%LOCALAPPDATA%\bin\ffmpeg.exe")
    raw = subprocess.run(
        [ffmpeg, "-v", "quiet", "-i", path, "-f", "s16le", "-ac", "1",
         "-ar", "16000", "-"],
        capture_output=True, check=True,
    ).stdout
    import numpy as np
    return np.frombuffer(raw, dtype="int16").astype("float32") / 32768.0


def main():
    audio = load_audio(VIDEO)
    print("samples", len(audio), "seconds", round(len(audio) / 16000, 1))
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        audio, language="ar", beam_size=5, vad_filter=True, word_timestamps=True,
    )
    print("lang", info.language, "prob", round(info.language_probability, 3))

    srt, txt = [], []
    for i, s in enumerate(segments, 1):
        srt.append(f"{i}\n{fmt(s.start)} --> {fmt(s.end)}\n{s.text.strip()}\n")
        txt.append(s.text.strip())
        print(i, round(s.start, 1), round(s.end, 1), s.text.strip(), flush=True)

    with open(CAPT + r"\narration.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt))
    with open(CAPT + r"\narration.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt))
    print("DONE", len(srt), "segments")


if __name__ == "__main__":
    main()
