# 🎙️ VozLocal — dictado offline para PCs de bajos recursos

> **Habla. Escribe. Sin nube, sin límites, sin GPU.**

VozLocal es un dictado de voz **100% offline** en **español e inglés** pensado para
**computadoras viejas**. Corre, literalmente, en una **GTX 750 Ti de 2014** con CPU —
sin tarjeta de video, sin internet y sin pagar suscripción.

*(captura del overlay en `assets/overlay.png` — próximamente)*

---

## ✨ Por qué existe

Los dictados modernos (Wispr Flow, etc.) mandan tu voz a la nube y cobran por palabra
o por mes. VozLocal hace lo contrario:

- 🔒 **Tu voz nunca sale de tu PC** — privacidad total.
- 🪙 **Gratis e ilimitado** — cero suscripción, cero límites de palabras.
- 💻 **Corre en hardware humilde** — diseñado y probado en una GTX 750 Ti (CPU-int8).
- 🎧 **ES + EN** — dos teclas, un idioma fiable cada vez (nada de detecciones fallidas).
- ⚡ **Feedback visual en vivo** — un colgante que te muestra *escuchando*, con barritas
  que reaccionan a tu voz real (RMS del micrófono).

---

## 🚀 Empezar

### Requisitos
- Windows 10/11
- Python 3.10+
- Un micrófono

### Instalar dependencias
```bash
pip install faster-whisper sounddevice pynput pyperclip numpy
```

### Ejecutar
```bash
# desde la carpeta del repo
set PYTHONPATH=%CD%\src
python -m vozlocal
```

O simplemente doble clic en `Dictar.bat` (lanzador preconfeccionado).

---

## 🎮 Cómo se usa

| Tecla | Acción |
|---|---|
| **F8** | Dictar en **español** (pulsa para empezar, pulsa de nuevo para escribir) |
| **F9** | Dictar en **inglés** (ídem) |

1. Haz clic en el campo de texto donde quieras escribir (Word, navegador, bloc de notas…).
2. Pulsa **F8** (o **F9**), habla en frases cortas, pulsa la MISMA tecla de nuevo.
3. VozLocal transcribe y **pega el texto en tu app**. El colgante te va indicando el estado.

### El colgante (indicador)
- `🎙️ F8=ES · F9=EN` — inactivo (pill oscuro).
- `Escuchando (ES)` — pill verde con **5 barritas** que siguen tu voz.
- `⏳ Transcribiendo…` — ámbar.
- `✓ Listo` — verde, texto escrito.
- **Clic en el colgante** = colapsar/expandir.

### Atajos y configuración (variables de entorno)
| Variable | Valores | Default | Qué hace |
|---|---|---|---|
| `DICTATE_MODEL` | `base` \| `small` | `small` | `base` = más rápido; `small` = más preciso. |
| `DICTATE_LANG` | `es` \| `en` | auto | Fuerza el idioma (ignora F8/F9). |

---

## 🧠 ¿Cómo funciona?

- **Motor:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper) en **CPU (int8)**.
  No necesitas GPU; el modelo `small` transcribe en ~1.5–5s por frase en un CPU de 4 núcleos.
- **UI:** `tkinter` — un pill redondeado (sobre fondo transparente en Windows) que se queda
  encima de todas tus ventanas.
- **Idioma fiable:** cada tecla **fuerza** el idioma en lugar de auto-detectar, que en
  hardware modesto es lento y se equivoca.
- **Barritas de voz:** el callback del micrófono calcula el **RMS** y lo suaviza; la UI lo
  dibuja como 5 barras con leve jitter, así ves tu voz "en vivo".

---

## 🖥️ En hardware humilde

Probado en una **NVIDIA GTX 750 Ti (2 GB, Maxwell)** con CPU:

| Modelo | Tiempo (~9 s de voz) | Calidad | Nota |
|---|---|---|---|
| `base` | ~2 s | baja | rápido, pero se equivoca |
| **`small`** | ~4.7 s | ✅ buena | **recomendado** (default) |

> 💡 ¿GPU vieja? No la necesitas. faster-whisper en CPU-int8 es la vía correcta
> (las GPUs Maxwell sin FP16 + CUDA 12/cuDNN 9 complican la aceleración). VozLocal
> elige **CPU** a propósito.

*(captura del overlay en `assets/overlay.png` — próximamente)*

---

## 🗺️ Roadmap

- [x] Dictado EN/ES offline con overlay y barritas de voz
- [ ] Posición / colores del colgante configurables
- [ ] Transcribir archivos de audio (clips)
- [ ] Empaquetado como `.exe` portable (PyInstaller)
- [ ] Puntuación y formato del texto con IA (comas, párrafos, listas)

---

## 🧪 Tests

```bash
pytest
```

## 📄 Licencia

MIT — haz lo que quieras, solo deja el aviso. © VozLocal contributors.

---

**Hecho con 🎙️ para que la gente con una PC vieja también pueda dictar.**
