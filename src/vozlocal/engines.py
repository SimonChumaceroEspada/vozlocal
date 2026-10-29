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
SILENCE_SPLIT_S = 1.0   # pausa que separa dos tramos (parakeet se degrada con silencios largos)

MODEL_DIR_NAME = "parakeet-tdt-0.6b-v3"


def _candidate_dirs(explicit=None):
    """Carpetas donde se busca el modelo Parakeet, en orden de prioridad."""
    out = []
    if explicit:
        out.append(Path(explicit))
    env = os.getenv("DICTATE_PARAKEET_DIR")
    if env:
        out.append(Path(env))
    out.append(Path(__file__).resolve().parents[2] / "models" / MODEL_DIR_NAME)   # repo/models/
    out.append(Path.home() / ".cache" / "vozlocal" / MODEL_DIR_NAME)
    out.append(Path.home() / ".cache" / "openwhispr" / "parakeet-models" / MODEL_DIR_NAME)
    return out


def resolve_model_dir(explicit=None):
    """Primera carpeta que tenga el modelo completo. Lanza FileNotFoundError si no hay ninguna."""
    for d in _candidate_dirs(explicit):
        if (d / "encoder.int8.onnx").exists() and (d / "tokens.txt").exists():
            return d
    buscadas = ", ".join(str(d) for d in _candidate_dirs(explicit))
    raise FileNotFoundError(
        "modelo Parakeet no encontrado. Descargalo y descomprimilo en models/"
        f"{MODEL_DIR_NAME} (o definí DICTATE_PARAKEET_DIR). Buscado en: {buscadas}"
    )


DEFAULT_PARAKEET_DIR = Path.home() / ".cache" / "vozlocal" / MODEL_DIR_NAME


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


def _split_on_silence(audio, min_silence_s=SILENCE_SPLIT_S):
    """Parte el audio en segmentos de voz separados por pausas largas.

    Parakeet no digiere bien un silencio largo en medio del buffer (se degrada o
    pierde palabras), así que cada pausa de >= min_silence_s pasa a ser un corte:
    se transcribe segmento por segmento y se unen con un espacio.
    """
    frame = int(BLOCK_S * SR)
    n = len(audio) // frame
    if n < 2:
        return [audio]
    rms = np.sqrt(np.mean(audio[: n * frame].reshape(n, frame) ** 2, axis=1))
    thr = max(0.004, 0.12 * float(np.percentile(rms, 95)))
    voiced = rms > thr
    min_frames = max(int(min_silence_s / BLOCK_S), 2)

    bounds = []
    start = None
    i = 0
    while i < n:
        if voiced[i]:
            if start is None:
                start = i
            i += 1
            continue
        j = i
        while j < n and not voiced[j]:
            j += 1
        if j - i >= min_frames and start is not None:
            bounds.append((start * frame, i * frame))
            start = None
        i = j
    if start is not None:
        bounds.append((start * frame, len(audio)))

    if not bounds:
        return [audio]

    pad = int(0.2 * SR)
    segs = [audio[max(0, s - pad): min(len(audio), e + pad)] for s, e in bounds]

    # unir restos muy cortos (<0.3 s) al segmento anterior para no perder sílabas
    out = []
    for seg in segs:
        if out and len(seg) < int(0.3 * SR):
            out[-1] = np.concatenate([out[-1], seg])
        elif out and len(out[-1]) < int(0.3 * SR):
            out[-1] = np.concatenate([out[-1], seg])
        else:
            out.append(seg)
    return out


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

        d = resolve_model_dir(model_dir)
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
        for seg in _split_on_silence(a):
            for chunk in _chunks(seg):
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
