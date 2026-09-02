# -*- coding: utf-8 -*-
"""Tests de vozlocal.text (puros, sin GPU/display/modelo)."""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vozlocal.text import clean_text


def test_clean_text_collapses_whitespace():
    assert clean_text("  Hola,   mundo.  ") == "Hola, mundo."


def test_clean_text_keeps_inner_spacing():
    assert clean_text("dos  palabras") == "dos palabras"


def test_clean_text_strips_leading_trailing():
    assert clean_text("\n\ttexto\t\n") == "texto"


def test_clean_text_empty():
    assert clean_text("") == ""
    assert clean_text("   ") == ""
