# -*- coding: utf-8 -*-
"""tools/bench_engines.py — compara los motores de VozLocal con audio real.

Uso:
    .venv/Scripts/python.exe tools/bench_engines.py clip1.wav clip2.wav

Mide, por motor: tiempo de carga, latencia de transcripción (mejor de N pasadas)
y velocidad en múltiplos de tiempo real, y muestra el texto resultante.
"""
import sys
import time
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vozlocal import engines  # noqa: E402

SR = 16000


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SR, f"{path}: {w.getframerate()} Hz (se esperan 16000)"
        assert w.getnchannels() == 1, f"{path}: {w.getnchannels()} canales (se espera mono)"
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def bench(engine, audio, lang="es", passes=2):
    times = []
    text = ""
    for _ in range(passes):
        t0 = time.time()
        text = engine.transcribe(audio, lang)
        times.append(time.time() - t0)
    return min(times), text


def main(paths):
    clips = [(Path(p).name, read_wav(p)) for p in paths]

    for label, cfg in (("whisper small int8", {"engine": "whisper", "model": "small"}),
                       ("parakeet tdt 0.6b v3", {"engine": "parakeet"})):
        t0 = time.time()
        try:
            eng = engines.create(cfg)
        except Exception as e:
            print(f"\n=== {label}: NO DISPONIBLE ({e})")
            continue
        load = time.time() - t0
        print(f"\n=== {label}  (carga {load:.1f}s, motor={eng.name})")
        for name, audio in clips:
            dur = len(audio) / SR
            best, text = bench(eng, audio)
            print(f"  {name}  audio={dur:6.1f}s  latencia={best:6.2f}s  {dur/best:5.1f}x tiempo real")
            print(f"     -> {text[:400]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
