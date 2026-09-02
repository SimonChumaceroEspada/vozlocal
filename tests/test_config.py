# -*- coding: utf-8 -*-
"""Tests de vozlocal.config (puros, sin GPU/display/modelo)."""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vozlocal.config import load_config, DEFAULTS


def test_load_config_returns_all_default_keys():
    cfg = load_config()
    for key in DEFAULTS:
        assert key in cfg
    assert cfg["model"] in ("base", "small")
    assert isinstance(cfg["autostart"], bool)
    assert isinstance(cfg["bars"], bool)
