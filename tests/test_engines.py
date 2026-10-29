# -*- coding: utf-8 -*-
"""Tests puros de los helpers de audio (sin modelo, sin sherpa-onnx, sin display)."""
import sys
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vozlocal import engines  # noqa: E402

SR = 16000


def _tono(segundos, amp=0.2):
    t = np.arange(int(segundos * SR)) / SR
    return (amp * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


def _silencio(segundos):
    return np.zeros(int(segundos * SR), dtype=np.float32)


def test_split_on_silence_corta_en_pausa_larga():
    audio = np.concatenate([_tono(1.0), _silencio(2.0), _tono(1.0)])
    segs = engines._split_on_silence(audio, min_silence_s=1.0)
    assert len(segs) == 2, [len(s) / SR for s in segs]
    assert all(len(s) > 0.9 * SR for s in segs)


def test_split_on_silence_no_corta_pausa_corta():
    audio = np.concatenate([_tono(1.0), _silencio(0.3), _tono(1.0)])
    segs = engines._split_on_silence(audio, min_silence_s=1.0)
    assert len(segs) == 1


def test_split_on_silence_todo_silencio_no_revienta():
    segs = engines._split_on_silence(_silencio(3.0))
    assert len(segs) == 1


def test_trim_silence_recorta_bordes():
    audio = np.concatenate([_silencio(2.0), _tono(1.0), _silencio(2.0)])
    out = engines._trim_silence(audio, pad_s=0.3)
    assert len(out) < len(audio)
    assert 1.0 * SR <= len(out) <= 2.0 * SR


def test_trim_silence_silencio_puro_devuelve_vacio():
    out = engines._trim_silence(_silencio(2.0))
    assert len(out) == 0
