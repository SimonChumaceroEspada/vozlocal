# -*- coding: utf-8 -*-
"""vozlocal.autostart — activa/desactiva el arranque de VozLocal con Windows.

Usa un .vbs en la carpeta de Inicio (mismo patrón que ya usa el usuario para los
gateways de Hermes). El toggle crea/elimina ese archivo.
"""
import sys
from pathlib import Path

from .config import CONFIG_PATH

STARTUP = Path()  # se asigna abajo
VBS_NAME = "VozLocal.vbs"


def _startup_dir():
    import os
    return Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup"


def _vbs_content():
    base = CONFIG_PATH.parent             # raíz del repo
    py = sys.executable                   # python del venv que está corriendo VozLocal
    src = str(base / "src")
    return (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        'Set env = WshShell.Environment("PROCESS")\n'
        f'env("PYTHONPATH") = "{src}"\n'
        f'WshShell.Run """{py}"" -m vozlocal", 0, False\n'
    )


def set_autostart(enabled):
    """True → crea el .vbs en Inicio; False → lo elimina."""
    vbs = _startup_dir() / VBS_NAME
    if enabled:
        vbs.write_text(_vbs_content(), encoding="utf-8")
    else:
        if vbs.exists():
            vbs.unlink()


def is_autostart_enabled():
    return (_startup_dir() / VBS_NAME).exists()
