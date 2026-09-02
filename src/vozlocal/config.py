# -*- coding: utf-8 -*-
"""vozlocal.config — configuración persistente.

En modo desarrollo (python -m vozlocal) se guarda en la raíz del repo.
En modo ejecutable (PyInstaller, sys.frozen) se guarda en %APPDATA%\\VozLocal.
"""
import json
import os
import sys
from pathlib import Path


def _config_path():
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / "VozLocal"
        base.mkdir(parents=True, exist_ok=True)
        return base / "config.json"
    return Path(__file__).resolve().parents[2] / "config.json"


CONFIG_PATH = _config_path()
DEFAULTS = {"model": "small", "autostart": True, "bars": True, "hide_when_idle": True}


def load_config():
    cfg = dict(DEFAULTS)
    try:
        if CONFIG_PATH.exists():
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for key in DEFAULTS:
                if key in loaded:
                    cfg[key] = loaded[key]
    except Exception:
        pass
    return cfg


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
