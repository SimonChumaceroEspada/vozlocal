# 🎙️ Dictado local EN/ES (Whisper) — Windows

Dictado de voz con **faster-whisper** (modelo `small`, CPU int8). Funciona **offline, privado**, y
detecta el idioma según tu **tecla de inicio (F8/F9)** → español o inglés, sin tocar nada.

## 👁️ Indicador flotante (overlay)

Aparece un **chip flotante** (arriba a la derecha, siempre encima) que te avisa del estado:

- `🎙️ F8=ES  F9=EN` → inactivo (pill oscuro, ~72% opacidad)
- `Escuchando (ES)` → grabando (pill verde con **5 barritas de voz** que suben/bajan con el RMS real de tu micrófono)
- `⏳ Transcribiendo…` → procesando (ámbar)
- `✓ Listo` → texto escrito (verde)

**Clic en el chip = colapsar/expandir.** Pill redondeado con `tkinter` + `-transparentcolor` (Windows).

## ▶️ Cómo usarlo

1. Doble clic en **`Dictar.bat`**. Espera a que diga `[dictate] LISTO. F8=ESPAÑOL · F9=INGLÉS...` (el modelo tarda unos segundos en cargar).
2. Haz clic en la app donde quieres escribir (Word, bloc de notas, navegador...).
3. **F8** para dictar en **español** / **F9** para dictar en **inglés** → empieza a escuchar (bip).
4. Habla (en una frase corta).
5. Presiona la **misma tecla** de nuevo → transcribe y **escribe el texto en tu app** (bip doble).

> El dictado escribe en la ventana que tenga el foco en ese momento. Asegúrate de tener un campo de texto abierto.
> Corta en frases cortas: F8 → habla → F8 → habla → F8…

## 🌐 Idioma EN/ES

- **F8 = español** 🇪🇸 · **F9 = inglés** 🇬🇧 (eliges la tecla según lo que vas a hablar — 100% fiable, sin adivinación).
- Cada tecla **fuerza** el idioma: eso hace el dictado rápido y preciso (nada de detecciones erróneas).

### Forzar idioma (opcional)
```bat
set DICTATE_LANG=es
```
(usa `es` o `en`; ignora F8/F9 y usa siempre ese idioma)

## ⚙️ Configuración (en `dictate.py`)

| Variable | Valores | Default | Qué hace |
|---|---|---|---|
| `DICTATE_MODEL` | `base` \| `small` | `base` | `base` = rápido. `small` = más preciso, ~3x más lento. |
| `DICTATE_LANG` | `es` \| `en` \| (vacío) | auto | Fuerza el idioma. |
| `HOTKEY` | `keyboard.Key.f8` | `f8` | Tecla para iniciar/detener el dictado. |

## 🔧 Requisitos

- faster-whisper (1.2.1) — ya instalado en tu venv.
- sounddevice, pynput, pyperclip — instalados vía `uv`.
- Funciona offline (el modelo corre local en tu CPU).

## 📂 Archivos

- `dictate.py` — el dictado.
- `Dictar.bat` — lanzador (doble clic).
- `test_es.wav` / `test_en.wav` — clips de prueba (puedes borrarlos).
