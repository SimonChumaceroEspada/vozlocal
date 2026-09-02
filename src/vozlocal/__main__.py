# -*- coding: utf-8 -*-
"""vozlocal.__main__ — punto de entrada: arranca la ventana del overlay y el listener.

Ejecuta:  python -m vozlocal   (con PYTHONPATH apuntando a ./src)
"""
import tkinter as tk
from pynput import keyboard

from . import dictation
from .overlay import Overlay


def main():
    root = tk.Tk()
    dictation.ui = Overlay(root, dictation._state)
    listener = keyboard.Listener(on_press=dictation.on_press)
    listener.daemon = True
    listener.start()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
