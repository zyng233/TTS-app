import tkinter as tk
from tkinter import ttk
from typing import Dict

class QuotaPanel(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="Usage Quota", **kwargs)
        self._setup_ui()
        
    def _setup_ui(self):
        self.char_var = tk.StringVar(value="Remaining free characters: - / -")
        self.req_var = tk.StringVar(value="Remaining free requests: - / -")

        ttk.Label(self, textvariable=self.char_var, anchor="w", justify="left").pack(anchor=tk.W, fill=tk.X, pady=(0, 2))
        ttk.Label(self, textvariable=self.req_var, anchor="w", justify="left").pack(anchor=tk.W, fill=tk.X)

    def update_stats(self, stats: Dict):
        self.char_var.set(f"Remaining free characters: {stats['characters_remaining']:,} / {stats['characters_remaining'] + stats['characters_used']:,}")
        self.req_var.set(f"Remaining free requests: {stats['requests_remaining']:,} / {stats['requests_remaining'] + stats['requests_used']:,}")