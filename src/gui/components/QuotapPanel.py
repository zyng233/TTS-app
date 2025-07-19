import tkinter as tk
from tkinter import ttk
from typing import Dict

class QuotaPanel(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="Usage Quota", **kwargs)
        self._setup_ui()
        
    def _setup_ui(self):
        self.char_var = tk.StringVar(value="Remaining free characters: - / -")

        ttk.Label(self, textvariable=self.char_var, anchor="w", justify="left").pack(anchor=tk.W, fill=tk.X, pady=(0, 2))
    def update_stats(self, stats: Dict):
        used = stats['characters_used']
        remaining = stats['characters_remaining']
        total = used + remaining

        self.char_var.set(f"Characters: {used:,} / {total:,}")  