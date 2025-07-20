import tkinter as tk
from tkinter import ttk
from typing import Dict

FREE_TIER_CHAR_LIMIT = 1000000

class QuotaPanel(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="Usage Quota (Reference)", **kwargs)
        self._setup_ui()
        
    def _setup_ui(self):
        self.char_var = tk.StringVar(value="Remaining free characters: - / -")

        ttk.Label(self, textvariable=self.char_var, anchor="w", justify="left").pack(anchor=tk.W, fill=tk.X, pady=(0, 2))
    
    def update_stats(self, stats: Dict):
        try:
            used = stats.get('used', 0)
            remaining = stats.get('remaining', FREE_TIER_CHAR_LIMIT)
            total = FREE_TIER_CHAR_LIMIT
            
            display_text = f"Used Characters: {used:,} / {total:,}"
            self.char_var.set(display_text)
    
        except Exception as e:
            self.char_var.set("Characters: Error loading usage") 