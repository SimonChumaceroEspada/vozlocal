# -*- coding: utf-8 -*-
"""vozlocal.dictation — núcleo: modelo faster-whisper, micrófono, atajos y dictado.

Vive en CPU (int8) para correr en hardware modesto (ordenadores sin GPU o con
tarjetas antiguas). F8 → español, F9 → inglés, todo offline.
"""
import sys
import ctypes
import os
import queue
import time

import numpy as np
import sounddevice as sd
from pynput import keyboard
from faster_whisper import WhisperModel

from .text import clean_text

# --- Guardia de instancia única (antes de importar nada pesado) ---
_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_mutex = _k32.CreateMutexW(None, False, "Local\\VozLocalDictadoENES")
if ctypes.get_last_error() == 183:   # ERROR_ALREADY_EXISTS
    sys.exit(0)

# --- Config (variables de entorno, opcional) ---
MODEL      = os.getenv("DICTATE_MODEL", "small")
DEVICE     = "cpu"
COMPUTE    = "int8"
SR         = 16000
CH         = 1
KEY_ES     = keyboard.Key.f8
KEY_EN     = keyboard.Key.f9
FORCE_LANG = os.getenv("DICTATE_LANG")   # 'es'/'en' para fijar el idioma
VAD        = True


def beep(freq=1000, dur=0.09):
    try:
        import winsound
        winsound.Beep(int(freq), int(dur * 1000))
    except Exception:
        pass


# Cargar modelo (una vez, al arrancar la app)
print(f"[vozlocal] cargando modelo '{MODEL}' ({DEVICE}/{COMPUTE})...", flush=True)
try:
    model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE, cpu_threads=os.cpu_count())
except Exception as e:
    print(f"[vozlocal] ERROR al cargar modelo: {e}", flush=True)
    sys.exit(1)

if FORCE_LANG:
    _lista = f"idioma fijado: {FORCE_LANG.upper()}"
else:
    _lista = "F8=ESPAÑOL  ·  F9=INGLÉS"
print(f"[vozlocal] LISTO. {_lista}. Presiona la tecla para empezar y de nuevo para escribir.", flush=True)
beep(1200, 0.1)

_state = {"rec": False, "lang": None, "level": 0.0}
_q = queue.Queue()
_stream = None
ui = None   # lo asigna __main__ (instancia de overlay.Overlay)


def _ui_set(kind, lang=None):
    global ui
    if ui:
        ui.set(kind, lang)


def _cb(indata, frames, t, status):
    if _state["rec"]:
        _q.put(indata[:, 0].copy())
        # nivel de voz para las barritas (RMS suavizado)
        rms = float(np.sqrt(np.mean(indata[:, 0] ** 2)))
        _state["level"] = 0.6 * _state.get("level", 0.0) + 0.4 * rms


def start():
    global _stream
    if _state["rec"]:
        return
    while not _q.empty():
        try:
            _q.get_nowait()
        except Exception:
            break
    _state["rec"] = True
    _state["level"] = 0.0
    try:
        _stream = sd.InputStream(samplerate=SR, channels=CH, dtype="float32", callback=_cb)
        _stream.start()
        beep(880, 0.08)
        _ui_set("listen", _state["lang"] or FORCE_LANG or "es")
        print(f"● Escuchando ({str(_state['lang'] or FORCE_LANG or 'es').upper()})... "
              "presiona la tecla para detener y escribir", flush=True)
    except Exception as e:
        _state["rec"] = False
        print(f"[vozlocal] error de microfono: {e}", flush=True)


def stop():
    global _stream
    if not _state["rec"]:
        return
    _state["rec"] = False
    try:
        if _stream:
            _stream.stop()
            _stream.close()
    except Exception:
        pass
    chunk = []
    while not _q.empty():
        try:
            chunk.append(_q.get_nowait())
        except Exception:
            break
    beep(660, 0.08)
    if not chunk:
        print("(sin audio)", flush=True)
        _ui_set("idle")
        return
    audio = np.concatenate(chunk)
    print("⏳ transcribiendo...", flush=True)
    _ui_set("trans")
    t0 = time.time()
    lang = FORCE_LANG or _state["lang"] or "es"
    print(f"   (idioma: {lang.upper()})", flush=True)
    try:
        segs, info = model.transcribe(audio, language=lang, beam_size=1, vad_filter=VAD)
    except Exception as e:
        print(f"[vozlocal] error transcribiendo: {e}", flush=True)
        _ui_set("idle")
        return
    text = "".join(s.text for s in segs)
    text = clean_text(text)
    dt = time.time() - t0
    if text:
        print(f"[{dt:.1f}s] -> {text}", flush=True)
        try:
            import pyperclip
            pyperclip.copy(text)
            kbd = keyboard.Controller()
            time.sleep(0.15)
            kbd.press(keyboard.Key.ctrl)
            kbd.press('v')
            kbd.release('v')
            kbd.release(keyboard.Key.ctrl)
            beep(1200, 0.09)
            beep(1500, 0.09)
            _ui_set("done")
            if ui:
                ui.lazy_idle()
        except Exception as e:
            print(f"[vozlocal] no se pudo pegar: {e}", flush=True)
            print("   (texto en portapapeles: " + text + ")", flush=True)
            _ui_set("done")
            if ui:
                ui.lazy_idle()
    else:
        print("(no se reconocio audio)", flush=True)
        _ui_set("idle")


def on_press(key):
    if key == KEY_ES:
        lang = "es"
    elif key == KEY_EN:
        lang = "en"
    else:
        return
    if _state["rec"]:
        stop()
    else:
        _state["lang"] = lang
        start()
