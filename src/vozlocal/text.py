# -*- coding: utf-8 -*-
"""vozlocal.text — utilidades de texto puras (sin dependencias pesadas)."""
import re


def clean_text(s):
    """Normaliza el texto transcrito: espacios sobrantes y espacios iniciales/finales."""
    return re.sub(r"\s+", " ", s).strip()
