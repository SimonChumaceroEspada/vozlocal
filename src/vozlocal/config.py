# -*- coding: utf-8 -*-
"""vozlocal.config — configuración persistente (config.json en la raíz del repo)."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"
DEFAULTS = {"model": "small", "autostart": True, "bars": True}


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
