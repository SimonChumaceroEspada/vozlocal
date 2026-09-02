# -*- coding: utf-8 -*-
"""vozlocal.settings — ventanita de Ajustes (auto-inicio, modelo, barritas)."""
import tkinter as tk

from . import config
from .autostart import set_autostart


class SettingsWindow(tk.Toplevel):
    def __init__(self, master, cfg, on_apply=None):
        super().__init__(master)
        self.title("VozLocal · Ajustes")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.cfg = cfg
        self.on_apply = on_apply

        self.var_auto = tk.BooleanVar(value=bool(cfg.get("autostart", True)))
        self.var_model = tk.StringVar(value=cfg.get("model", "small"))
        self.var_bars = tk.BooleanVar(value=bool(cfg.get("bars", True)))

        tk.Label(self, text="Dictado de voz · offline", font=("Segoe UI", 12, "bold"),
                 fg="#16a34a").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 6))

        tk.Checkbutton(self, text="Auto-iniciar con Windows", variable=self.var_auto,
                       font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=2, sticky="w", padx=16)

        tk.Label(self, text="Modelo:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=16, pady=(6, 0))
        mf = tk.Frame(self)
        mf.grid(row=2, column=1, sticky="w", pady=(6, 0))
        tk.Radiobutton(mf, text="base (rápido)", variable=self.var_model, value="base",
                       font=("Segoe UI", 9)).pack(anchor="w")
        tk.Radiobutton(mf, text="small (preciso)", variable=self.var_model, value="small",
                       font=("Segoe UI", 9)).pack(anchor="w")

        tk.Checkbutton(self, text="Barritas de voz en el aviso", variable=self.var_bars,
                       font=("Segoe UI", 10)).grid(row=3, column=0, columnspan=2, sticky="w", padx=16, pady=(8, 0))

        btns = tk.Frame(self)
        btns.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        tk.Button(btns, text="Guardar", command=self._save, width=12,
                  bg="#16a34a", fg="white", activebackground="#128a4a").pack(side="left", padx=6)
        tk.Button(btns, text="Cancelar", command=self.destroy, width=12).pack(side="left", padx=6)

        self._status = tk.Label(self, text="", fg="#16a34a", font=("Segoe UI", 9))
        self._status.grid(row=5, column=0, columnspan=2, pady=(6, 8))

        self.geometry("340x290")
        try:
            self.grab_set()
        except Exception:
            pass

    def _save(self):
        self.cfg["autostart"] = bool(self.var_auto.get())
        self.cfg["model"] = self.var_model.get()
        self.cfg["bars"] = bool(self.var_bars.get())
        config.save_config(self.cfg)
        set_autostart(self.cfg["autostart"])
        if self.on_apply:
            self.on_apply(self.cfg)
        note = "(el modelo se aplica al reiniciar)" if self.var_model.get() != config.DEFAULTS["model"] else ""
        self._status.config(text=f"Guardado ✅ {note}")
        self.after(1200, self.destroy)
