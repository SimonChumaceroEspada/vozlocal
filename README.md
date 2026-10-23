# VozLocal - offline dictation for low-end PCs

> **Speak. It types. No cloud, no limits, no GPU.**

VozLocal is 100% offline voice dictation in **Spanish and English**, built for **old
computers**. It runs on a 2014-era machine (NVIDIA GTX 750 Ti, Maxwell) using the **CPU
only**: no GPU, no internet, no subscription.

**Stack:** Python 3.10+ · faster-whisper (CPU int8) · tkinter · sounddevice · pynput

---

## Demo

Press **F9**, speak, press **F9** again. The transcript is pasted into whatever window has
focus, in this case Microsoft Word.

![Full demo: dictating into Word while the overlay shows listening, transcribing, done](assets/vozlocal-demo.gif)

**The same demo with audio** - spoken in non-native English, and it still comes out right:
28 words, zero typos. Press play, it has sound.

https://github.com/user-attachments/assets/3358f7b3-5787-49d6-a6be-644522253ea0

**The overlay, zoomed in** from that same recording: listening with the live voice bars, then
transcribing, then done.

![The overlay pill: listening with live voice bars, transcribing, done](assets/pill-states.gif)

---

## Why it exists

Modern dictation tools send your voice to the cloud and charge per word or per month.
VozLocal does the opposite:

- **Your voice never leaves your PC.** Nothing is uploaded, ever.
- **Free and unlimited.** No subscription, no word cap.
- **Runs on humble hardware.** Designed and measured on a 4-core i5-4460 with a GTX 750 Ti.
- **ES + EN, one reliable language per key.** Each hotkey *forces* the language instead of
  auto-detecting, which is slow and error-prone on modest hardware.
- **Live visual feedback.** A floating pill shows *listening*, with five bars driven by the
  real RMS of your microphone.

---

## Quick start

### Requirements

- Windows 10/11 (64-bit)
- Python 3.10+
- A microphone

### Install

```bash
pip install faster-whisper sounddevice pynput pyperclip numpy

# optional: fast Parakeet engine (see "Two engines" below)
pip install "sherpa-onnx>=1.10"
```

### Run

```bash
# from the repo root
set PYTHONPATH=%CD%\src
python -m vozlocal
```

Or double-click `Dictar.bat`, a ready-made launcher. The Whisper model is downloaded **once**
on first start (that first run needs internet, after that it is cached).

---

## Two engines: Parakeet (fast) or Whisper (classic)

VozLocal ships **two interchangeable engines**. Pick one in **Settings (F10) → Engine**; no code
changes needed.

| Engine | Model | Disk | Measured latency\* | Spanish |
|---|---|---|---|---|
| **Parakeet** (recommended) | NVIDIA Parakeet TDT 0.6B v3 int8 — sherpa-onnx / ONNX Runtime | 641 MB | **1.3 s** (6.8 s of speech) · **2.7 s** (20.8 s) | ✅ punctuation, accents, casing |
| Whisper | faster-whisper `small` int8 — CTranslate2 | 466 MB | 3.8 s · 4.1 s | good, no punctuation, more typos |

\* Measured on an **Intel i5-4460** (4 cores, 2014), **no GPU**. Same recording, both engines:
Whisper wrote `…el estado de la lazaña` and `sigo pensando en lo demónica`; Parakeet wrote
`…el estado de la lasaña` and `sigo pensando en lo de Mónica`.

**About punctuation:** Parakeet infers it from **prosody**. Speak in one unbroken stream and you get
plain text; add a short pause at the end of each sentence and it punctuates. VozLocal also
**capitalizes the first letter and ensures a final period** (it never invents commas or `¿?`).

### Install the Parakeet engine

```bash
pip install "sherpa-onnx>=1.10"     # or: pip install "vozlocal[parakeet]"
```

Download the int8 ONNX model and unpack it into `models/parakeet-tdt-0.6b-v3/`:

```bash
curl -L -o parakeet.tar.bz2 \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2
tar xjf parakeet.tar.bz2
mkdir -p models
mv sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 models/parakeet-tdt-0.6b-v3
```

VozLocal looks for the model in this order: `DICTATE_PARAKEET_DIR` → `models/parakeet-tdt-0.6b-v3/`
→ `~/.cache/vozlocal/parakeet-tdt-0.6b-v3`. If it is missing, it says so and **falls back to Whisper**.

> 💡 **Don't want to download anything?** The default stays **Whisper `small`**: it downloads itself
> on first run and works out of the box. Switching engines is one line in `config.json`
> (`"engine": "parakeet"`) or one click in Settings.

---

## How to use

| Key | Action |
|---|---|
| **F8** | Dictate in **Spanish** (press to start, press again to write) |
| **F9** | Dictate in **English** (same behaviour) |

1. Click the text field where you want to write (Word, browser, Notepad, anything).
2. Press **F8** (or **F9**), speak in short sentences, press the SAME key again.
3. VozLocal transcribes and **pastes the text into your app**.

### The overlay pill

| State | What you see |
|---|---|
| Idle | `F8=ES · F9=EN` dark pill |
| Recording | `Escuchando (ES)` green pill, 5 bars following your voice |
| Processing | `Transcribiendo…` amber |
| Done | `Listo` green, text already written |

Click the pill to collapse or expand it.

---

## Configuration

Environment variables:

| Variable | Values | Default | Effect |
|---|---|---|---|
| `DICTATE_ENGINE` | `whisper` \| `parakeet` | `whisper` | Transcription engine (also selectable in Settings) |
| `DICTATE_PARAKEET_DIR` | path | `models/parakeet-tdt-0.6b-v3` | Where the Parakeet model lives |
| `DICTATE_MODEL` | `base` \| `small` | `small` | Whisper engine only: `base` is faster, `small` is more accurate |
| `DICTATE_LANG` | `es` \| `en` | auto | Forces one language and ignores F8/F9 |

Settings are also persisted to `config.json` (repo root in development,
`%APPDATA%\VozLocal` when frozen):

```json
{ "engine": "whisper", "model": "small", "autostart": true, "bars": true, "hide_when_idle": true }
```

---

## How it works

- **Engines:** [Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) int8
  via [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) (fast, ~641 MB) or
  [faster-whisper](https://github.com/SYSTRAN/faster-whisper) `small` int8 (classic, ~466 MB).
  Both run on **CPU with int8**; no GPU is required.
- **Text:** `clean_text()` collapses whitespace, capitalizes the first letter and ensures a
  final period.
- **Silence:** before transcribing, audio is trimmed by energy (RMS over 50 ms frames) so long
  pauses cost nothing; audio longer than 28 s is split at the quietest point.
- **UI:** `tkinter`, a rounded pill on a transparent window that stays on top of every other
  window.
- **Reliable language:** each hotkey forces the language instead of auto-detecting.
- **Voice bars:** the microphone callback computes the **RMS**, smooths it, and the UI draws
  it as five bars with a slight jitter, so you see your voice live.
- **Empty GPU is on purpose:** Maxwell cards without FP16 plus CUDA 12/cuDNN 9 make GPU
  acceleration fragile. CPU int8 is the correct path here, and it keeps the tool portable to
  machines that have no usable GPU at all.

Source layout:

```
src/vozlocal/
  __main__.py    entry point and wiring
  engines.py     transcription engines (whisper / parakeet)
  dictation.py   microphone, hotkeys, dictation loop
  overlay.py     tkinter floating pill
  settings.py    settings window
  config.py      persistent configuration
  autostart.py   Windows startup shortcut
  text.py        transcript cleaning
tests/           pure tests, no model or display required
```

---

## Performance on humble hardware

Measured on an Intel i5-4460 (4 cores) with a GTX 750 Ti present but unused, transcribing
about 9 seconds of speech:

| Model | Time | Quality | Note |
|---|---|---|---|
| `base` | ~2 s | low | fast, but it misses words |
| **`small`** | **~4.7 s** | **good** | **recommended** (default) |

### Hardware requirements

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 2 x64 cores | 4 cores (i5-4460 @ 3.2 GHz) |
| System RAM | 4 GB | 8 GB |
| RAM while dictating | ~200 MB (Whisper `base`) | ~800 MB (Parakeet) · ~435 MB (Whisper `small`) |
| GPU | not required (CPU int8) | not required |
| Free disk | ~1 GB | ~2 GB |
| OS | Windows 10 (64-bit) | Windows 11 |
| Microphone | any | decent USB |

Speaking in short sentences keeps latency low: transcribe per phrase, not per paragraph.

---

## Start with Windows

VozLocal can launch silently at login, like an always-available dictation assistant.
`Dictar.vbs` is a windowless launcher.

- **Enable:** create a shortcut to `wscript.exe "path\to\Dictar.vbs"` in your Startup folder
  (`Win+R` then `shell:startup`).
- **Disable:** delete that shortcut.
- **RAM note:** the `small` model holds roughly 435 MB while idle. On a low-memory machine,
  start it on demand with `Dictar.bat` instead.

---

## Build a portable `.exe` (PyInstaller)

So anyone can run it **without installing Python**:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --onedir --name VozLocal --paths src ^
  --collect-all ctranslate2 --collect-all faster_whisper --collect-all av ^
  --collect-all sounddevice --collect-all pynput --hidden-import pyperclip entry.py
```

Result: a `dist\VozLocal\` folder containing `VozLocal.exe`. Copy the **whole folder**, not
just the executable, because the native libraries live beside it.

---

## Tests

```bash
pytest
```

---

## Roadmap

- [x] Offline EN/ES dictation with overlay and live voice bars
- [x] Second switchable engine (NVIDIA Parakeet TDT 0.6B v3 int8 via sherpa-onnx)
- [x] Text normalization: first-letter capital and final period
- [ ] Configurable pill position and colours
- [ ] Transcribe audio files (clips)
- [ ] Portable `.exe` packaging
- [ ] Punctuation and paragraph formatting

---

## License

MIT. Do what you want, just keep the notice. © VozLocal contributors.

---

**Leer en español: [LEEME.md](LEEME.md)**
