# -*- coding: utf-8 -*-
"""vozlocal.text — utilidades de texto puras (sin dependencias pesadas)."""
import re

# Signos que ya cierran una frase: si el texto termina en uno de estos, no se agrega punto.
_FINALES = ".!?…:;\"')]}»"


def _capitalizar_primera(t):
    """Pone en mayúscula la primera letra, saltando signos de apertura (¿ ¡ « ")."""
    for i, ch in enumerate(t):
        if ch.isalpha():
            return t[:i] + ch.upper() + t[i + 1:]
    return t


def clean_text(s):
    """Normaliza el texto transcrito.

    - colapsa espacios sobrantes y recorta extremos
    - capitaliza la primera letra
    - asegura punto final si el texto no termina en un signo de cierre

    No inventa comas ni signos de interrogación/exclamación: eso depende de la prosodia.
    """
    t = re.sub(r"\s+", " ", s).strip()
    if not t:
        return ""
    t = _capitalizar_primera(t)
    if t[-1] not in _FINALES:
        t += "."
    return t
