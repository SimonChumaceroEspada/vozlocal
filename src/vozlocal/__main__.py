# -*- coding: utf-8 -*-
"""vozlocal.__main__ — punto de entrada: arranca el overlay, el listener y aplica config.

Ejecuta:  python -m vozlocal   (con PYTHONPATH apuntando a ./src)
"""
import sys
import tkinter as tk
from pynput import keyboard

from . import config, autostart
from . import dictation
from .overlay import Overlay
from .settings import SettingsWindow


def main():
    # Evitar UnicodeEncodeError ('.', '●', '⏳'...) en consola/exe con cp1252
    for _s in (sys.stdout, sys.stderr):
        if _s is not None:
            try:
                _s.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    cfg = config.load_config()
    # aplicar la preferencia de auto-inicio con Windows (crea/elimina el .vbs en Inicio)
    autostart.set_autostart(bool(cfg.get("autostart", True)))

    root = tk.Tk()

    def open_settings():
        # seguro desde cualquier hilo (doble clic o F10): enruta al hilo Tk
        root.after(0, lambda: SettingsWindow(root, cfg, on_apply=_on_apply))

    def _on_apply(new_cfg):
        ui.apply_cfg(new_cfg)

    dictation.ui = Overlay(root, dictation._state, cfg=cfg, open_settings=open_settings)
    ui = dictation.ui
    dictation.open_settings = open_settings

    listener = keyboard.Listener(on_press=dictation.on_press)
    listener.daemon = True
    listener.start()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
