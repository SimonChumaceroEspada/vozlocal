# -*- coding: utf-8 -*-
"""vozlocal.engines — motores de transcripción intercambiables.

Dos motores, mismo contrato:  engine.transcribe(audio_float32_16k, lang) -> str

  * WhisperEngine  — faster-whisper (CTranslate2, CPU int8). El clásico.
  * ParakeetEngine — NVIDIA Parakeet TDT 0.6B v3 int8 vía sherpa-onnx (ONNX Runtime).
                     Detecta el idioma solo, ~5x más rápido en CPU y devuelve
                     puntuación y acentos.

El audio que llega desde dictation.py ya viene en float32 mono a 16 kHz.
"""
import os
from pathlib import Path

import numpy as np

SR = 16000
MAX_CHUNK_S = 28.0      # parakeet: cortar audio largo para no inflar memoria
SEARCH_S = 1.5          # ventana donde se busca el silencio para cortar
BLOCK_S = 0.05          # resolución de la búsqueda de silencio

DEFAULT_PARAKEET_DIR = (
    Path.home() / ".cache" / "openwhispr" / "parakeet-models" / "parakeet-tdt-0.6b-v3"
)


def _trim_silence(audio, pad_s=0.3):
    """Recorta silencio inicial/final. Sin esto, un dictado con pausas largas
    se procesa entero y parakeet tarda proporcional al silencio total."""
    frame = int(0.05 * SR)
    n = len(audio) // frame
    if n < 1:
        return audio
    rms = np.sqrt(np.mean(audio[: n * frame].reshape(n, frame) ** 2, axis=1))
    thr = max(0.004, 0.12 * float(np.percentile(rms, 95)))
    idx = np.where(rms > thr)[0]
    if len(idx) == 0:
        return audio[:0]
    start = max(0, idx[0] * frame - int(pad_s * SR))
    end = min(len(audio), (idx[-1] + 1) * frame + int(pad_s * SR))
    return audio[start:end]


def _chunks(audio, max_s=MAX_CHUNK_S):
    """Parte el audio en trozos de <= max_s segundos, cortando por el punto más silencioso."""
    step = int(max_s * SR)
    i, n = 0, len(audio)
    block = max(int(BLOCK_S * SR), 1)
    while i < n:
        if n - i <= step:
            yield audio[i:n]
            return
        lo = max(i + step - int(SEARCH_S * SR), i + 1)
        win = audio[lo:i + step]
        energies = [
            float(np.sqrt(np.mean(win[k:k + block] ** 2)))
            for k in range(0, max(len(win) - block, 1), block)
        ]
        cut = lo + int(np.argmin(energies)) * block if energies else i + step
        if cut <= i:
            cut = i + step
        yield audio[i:cut]
        i = cut


class WhisperEngine:
    """faster-whisper en CPU (int8). Respeta el idioma que le pasa el atajo."""

    name = "whisper"

    def __init__(self, model_name="small", threads=None):
        from faster_whisper import WhisperModel

        self.model_name = model_name
        self.model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            cpu_threads=int(threads or os.cpu_count() or 4),
        )

    def transcribe(self, audio, lang="es"):
        segs, _info = self.model.transcribe(
            audio, language=lang, beam_size=1, vad_filter=True
        )
        return "".join(s.text for s in segs)


class ParakeetEngine:
    """NVIDIA Parakeet TDT 0.6B v3 int8 con sherpa-onnx. Detecta el idioma solo."""

    name = "parakeet"
    supports_language_hint = False

    def __init__(self, model_dir=None, threads=None):
        import sherpa_onnx

        d = Path(model_dir or os.getenv("DICTATE_PARAKEET_DIR") or DEFAULT_PARAKEET_DIR)
        need = ["encoder.int8.onnx", "decoder.int8.onnx", "joiner.int8.onnx", "tokens.txt"]
        missing = [f for f in need if not (d / f).exists()]
        if missing:
            raise FileNotFoundError(f"faltan archivos del modelo en {d}: {missing}")

        self.model_dir = d
        self.rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(d / "encoder.int8.onnx"),
            decoder=str(d / "decoder.int8.onnx"),
            joiner=str(d / "joiner.int8.onnx"),
            tokens=str(d / "tokens.txt"),
            num_threads=int(threads or os.cpu_count() or 4),
            sample_rate=SR,
            feature_dim=80,
            decoding_method="greedy_search",
            model_type="nemo_transducer",
        )

    def transcribe(self, audio, lang="es"):
        a = _trim_silence(np.asarray(audio, dtype=np.float32).reshape(-1))
        if len(a) < SR // 5:            # menos de 200 ms de voz: nada que transcribir
            return ""
        parts = []
        for chunk in _chunks(a):
            chunk = chunk.reshape(-1)
            if len(chunk) < SR // 10:      # menos de 100 ms: ignorar
                continue
            stream = self.rec.create_stream()
            stream.accept_waveform(SR, chunk)
            self.rec.decode_stream(stream)
            text = stream.result.text.strip()
            if text:
                parts.append(text)
        return " ".join(parts)


def create(cfg):
    """Devuelve el motor pedido en la config; si parakeet falla, cae a whisper."""
    want = str(cfg.get("engine") or "whisper").lower()
    if want == "parakeet":
        try:
            return ParakeetEngine(cfg.get("parakeet_dir"))
        except Exception as e:      # modelo ausente o sherpa-onnx no instalado
            print(f"[vozlocal] parakeet no disponible ({e}); uso whisper", flush=True)
    return WhisperEngine(cfg.get("model", "small"))
