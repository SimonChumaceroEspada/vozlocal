# -*- coding: utf-8 -*-
"""Punto de entrada para PyInstaller: arranca VozLocal."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from vozlocal.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
