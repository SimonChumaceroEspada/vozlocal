# Dictado offline para PC de bajos recursos — Plan del producto/repo

> **Meta:** Convertir el dictado actual (F8/F9 + overlay, ya funcionando) en un repo público
> y pulido, con una UI simple, lista para portafolio. Posicionamiento: **transcripción de voz
> offline para computadoras viejas / baja GPU.**

**Goal:** Un empaquetado, documentado y bonito que cualquier persona (incluso con una PC de 2013)
pueda instalar y dictar en español/inglés, sin nube y sin límites.

**Architecture:** Python + faster-whisper (CPU int8) + tkinter UI. Sin dependencias pesadas de GPU.
El "mago" es que corre local en hardware modesto (verificado: GTX 750 Ti, funciona en CPU).

**Tech Stack:** Python 3.10+, faster-whisper, sounddevice, pynput, pyperclip, tkinter; empaquetado con
PyInstaller en un .exe portable.

---

## Contexto / estado actual

- Código funcional: `D:\Hermes\dictation\dictate.py` (F8=ES / F9=EN, overlay flotante con pill + respiro suave).
- Lanzadores: `Dictar.bat`, `Dictar.vbs`; docs: `LEEME.md`.
- Verificado: GPU 750 Ti NO sirve para CUDA en faster-whisper (falta cuBLAS/cuDNN + Maxwell sin FP16) → **CPU es la vía correcta** = ventaja de marketing ("no necesitas GPU").
- No hay repo git ni tests aún.

---

## Fases

### Fase 1 — Overlay "en vivo" (visual + voz)
- ✅ **Barritas de nivel de voz (equalizer)** que se mueven con tu voz real (RMS del micrófono), no falsas.
      Estado `listen` → 5 barritas escalando con la amplitud + suavizado, pill verde. ✅ hecho
- [ ] Ajustes de estética: posición (4 esquinas), tamaño, color verde/ámbar, velocidad de animación.
- [ ] Estados extra: "cargando modelo", "microrófono bloqueado" (error).
- [ ] Config en `config.toml` (o env) en vez de solo variables de entorno.

### Fase 2 — Repo de portafolio  ✅
- ✅ `git init` en `D:\Hermes\dictation\` → estructura de proyecto Python limpia (`src/`, `pyproject.toml`). ✅ hecho
- ✅ `README.md` con la historia + sección "por qué existe". ✅ hecho
- ✅ `LICENSE` (MIT) + `.gitignore`. ✅ hecho
- ✅ Paquete renombrado a **`vozlocal`**. ✅ hecho
- ✅ Tests mínimos (`tests/test_text.py`, 4 passed). ✅ hecho

### Fase 3 — Mini GUI (accesible para no-técnicos)
- [ ] Ventana tkinter simple: elegir idioma (ES/EN), modelo (base/small), bandas de voz on/off,
      botón "Iniciar/Detener", indicador de estado y hotkeys.
- [ ] La GUI sustituye al chip cuando se abre; opción a "modo minimalista" (solo chip).

### Fase 4 — Distribución
- [ ] Build con PyInstaller → `dictaflow.exe` portable (una carpeta, sin instalar Python).
- [ ] Guía "cómo corrió esto en una GTX 750 Ti" (caso de éxito) → gran pieza de README.

### Fase 5 — Lanzamiento / portafolio
- [ ] Push a GitHub (repo público).
- [ ] GIF corto del dictado en acción en el README.
- [ ] (Opcional) pyproject `pip install` para gente técnica.

---

## Archivos que cambiarán

- `D:\Hermes\dictation\dictate.py` → refactor a `src/<nombre>/`.
- Nuevos: `pyproject.toml`, `LICENSE`, `README.md`, `config.toml`, `src/<nombre>/ui.py`, `src/<nombre>/dictation.py`, `tests/`.
- Mantener: `Dictar.bat`/`.vbs` como lanzadores de usuario final.

## Validación

- Dictar (F8 ES / F9 EN) en un campo de texto → el texto pegado es correcto.
- Overlay: barritas suben/bajan con la voz, sin parpadeo duro.
- Build .exe: corre en Windows 10 sin Python instalado.
- Tests: `pytest` en green.

## Riesgos / preguntas abiertas

- **Alcance del repo:** ¿Diccionario simple o quieres también modo "transcribir archivo" (WhisperDesktop-style)?
- **Nombre del producto** (marca) — pendiente de elegir.
- **Emoji/unicode en tkinter:** el pill usa `🎙️`, los emojis dependen del font del sistema (Segoe UI Emoji). OK en Windows.
- **GUI vs chip:** cuánta UI querés para no sobreingenierar (YAGNI).
