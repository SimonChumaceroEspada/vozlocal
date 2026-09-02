# -*- coding: utf-8 -*-
"""vozlocal.autostart — activa/desactiva el arranque de VozLocal con Windows.

Usa un .vbs en la carpeta de Inicio (mismo patrón que ya usa el usuario para los
gateways de Hermes). El toggle crea/elimina ese archivo.

En modo ejecutable (PyInstaller) el .vbs ejecuta el propio VozLocal.exe.
En modo desarrollo ejecuta `python -m vozlocal` con PYTHONPATH=src.
"""
import os
import sys
from pathlib import Path

VBS_NAME = "VozLocal.vbs"


def _startup_dir():
    return Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup"


def _vbs_content():
    exe = sys.executable
    if getattr(sys, "frozen", False):
        # exe portable: basta con lanzar el ejecutable
        return (
            'Set WshShell = CreateObject("WScript.Shell")\n'
            f'WshShell.Run """{exe}""", 0, False\n'
        )
    from .config import CONFIG_PATH
    base = CONFIG_PATH.parent             # raíz del repo
    src = str(base / "src")
    return (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        'Set env = WshShell.Environment("PROCESS")\n'
        f'env("PYTHONPATH") = "{src}"\n'
        f'WshShell.Run """{exe}"" -m vozlocal", 0, False\n'
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
