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


def test_clean_text_capitalizes_first_letter():
    assert clean_text("dos palabras") == "Dos palabras."
    assert clean_text("¿estás seguro?") == "¿Estás seguro?"


def test_clean_text_adds_final_period():
    assert clean_text("y como te iba diciendo estoy a punto") == "Y como te iba diciendo estoy a punto."


def test_clean_text_keeps_existing_end_sign():
    assert clean_text("listo!") == "Listo!"
    assert clean_text("¿qué tal?") == "¿Qué tal?"
    assert clean_text("ya está…") == "Ya está…"


def test_clean_text_strips_leading_trailing():
    assert clean_text("\n\ttexto\t\n") == "Texto."


def test_clean_text_empty():
    assert clean_text("") == ""
    assert clean_text("   ") == ""
