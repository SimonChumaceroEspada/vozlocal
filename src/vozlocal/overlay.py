# -*- coding: utf-8 -*-
"""vozlocal.overlay — indicador flotante (pill redondeado) con barritas de voz en vivo.

Un chip siempre-en-cima que avisa del estado (inactivo / escuchando / transcribiendo / listo).
Al escuchar, 5 barritas a la derecha siguen el nivel real de la voz (RMS del micrófono).
"""
import math
import time
import tkinter as tk


class Overlay:
    """Pill flotante, siempre encima. Barritas de voz a la derecha del texto."""

    W, H, R = 252, 40, 20
    _INVIS = "#010203"   # color que Tk hace transparente en Windows → solo el pill queda

    def __init__(self, root, state, cfg=None, open_settings=None):
        self.root = root
        self.state = state           # dict compartido con dictation (lee "level")
        self._show_bars = bool((cfg or {}).get("bars", True))
        self._open_settings = open_settings
        self.root.overrideredirect(True)                 # sin marco (flotante)
        self.root.attributes("-topmost", True)           # siempre encima
        try:
            self.root.attributes("-transparentcolor", self._INVIS)
        except Exception:
            pass
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"{self.W}x{self.H}+{max(0, sw - self.W - 28)}+30")
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg=self._INVIS, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda e: self._toggle())
        self.canvas.bind("<Double-Button-1>", lambda e: self._open_settings and self._open_settings())
        self._kind = "idle"
        self._lang = "es"
        self._expand = True
        self._idle_job = None
        self._bars = []
        self._bar_h = [0.0] * 5
        self._redraw()
        self.root.after(40, self._tick)

    def _palette(self):
        if self._kind == "listen":
            return "#16a34a", "#ffffff", f"Escuchando ({self._lang.upper()})"
        if self._kind == "trans":
            return "#d97706", "#ffffff", "⏳  Transcribiendo…"
        if self._kind == "done":
            return "#16a34a", "#ffffff", "✓  Listo"
        if self._expand:
            return "#23232d", "#cfd2dc", "🎙️  F8=ES  ·  F9=EN"
        return "#23232d", "#cfd2dc", "🎙️"

    def _redraw(self):
        c = self.canvas
        c.delete("all")
        bg, fg, text = self._palette()
        W, H, r = self.W, self.H, self.R
        # pill redondeado (cuatro arcos + rectángulos)
        for args in [(0, 0, 2 * r, 2 * r, 90), (W - 2 * r, 0, W, 2 * r, 270),
                     (0, H - 2 * r, 2 * r, H, 180), (W - 2 * r, H - 2 * r, W, H, 0)]:
            c.create_arc(*args[:4], start=args[4], extent=180, fill=bg, outline=bg)
        c.create_rectangle(r, 0, W - r, H, fill=bg, outline=bg)
        c.create_rectangle(0, r, W, H - r, fill=bg, outline=bg)
        c.create_rectangle(r, r, W - r, H - r, fill=bg, outline=bg)
        if self._kind == "listen":
            if self._show_bars:
                # barritas de nivel de voz A LA DERECHA del texto (estilo visualizador)
                self._bars = []
                bx = W - 58
                for _ in range(5):
                    bid = c.create_rectangle(bx, H - 16, bx + 5, H - 11, fill="#d9ffe9", outline="")
                    self._bars.append(bid)
                    bx += 8
                self._bar_h = [0.0] * 5
                c.create_text(22, H // 2, text=text, fill=fg, font=("Segoe UI", 11, "bold"), anchor="w")
            else:
                self._bars = []
                c.create_text(W // 2, H // 2, text=text, fill=fg, font=("Segoe UI", 11, "bold"))
        else:
            self._bars = []
            c.create_text(W // 2, H // 2, text=text, fill=fg, font=("Segoe UI", 11, "bold"))

    def apply_cfg(self, cfg):
        self._show_bars = bool(cfg.get("bars", True))
        self._redraw()

    def _apply(self, kind, lang=None):
        if lang:
            self._lang = lang
        if kind != "idle" and self._idle_job:      # cancelar idle pendiente
            try:
                self.root.after_cancel(self._idle_job)
            except Exception:
                pass
            self._idle_job = None
        self._kind = kind
        self._redraw()
        self._base_alpha = 0.72 if kind == "idle" else 0.95
        self.root.attributes("-alpha", self._base_alpha)

    def set(self, kind, lang=None):
        # seguro desde hilos: enruta al hilo principal de Tk
        self.root.after(0, self._apply, kind, lang)

    def lazy_idle(self):
        if self._idle_job:
            try:
                self.root.after_cancel(self._idle_job)
            except Exception:
                pass
        self._idle_job = self.root.after(1500, lambda: self._apply("idle", None))

    def _tick(self):
        # barritas de voz: siguen el RMS real del micrófono (con suavizado + leve jitter)
        if self._kind == "listen" and self._bars:
            lvl = min(1.0, self.state.get("level", 0.0) / 0.03)
            t = time.time()
            shape = (0.9, 0.5, 1.1, 0.6, 0.85)
            for i, bid in enumerate(self._bars):
                jitter = 0.10 * math.sin(t * 8 + i * 1.3)
                target = min(1.0, max(0.06, 0.08 + lvl * shape[i] + jitter))
                cur = self._bar_h[i] + (target - self._bar_h[i]) * 0.5
                self._bar_h[i] = cur
                h = 5 + int(cur * 16)
                self.canvas.coords(bid, self.W - 58 + i * 8, self.H - 11 - h,
                                   self.W - 58 + i * 8 + 5, self.H - 11)
        self.root.after(40, self._tick)

    def _toggle(self):
        self._expand = not self._expand
        if self._kind == "idle":
            self._redraw()
