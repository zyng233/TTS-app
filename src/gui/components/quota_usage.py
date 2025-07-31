import tkinter as tk
from tkinter import ttk
from typing import Dict

class QuotaPanel(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="Character Usage", **kwargs)
        self._setup_ui()
        
    def _setup_ui(self):
        self.char_var = tk.StringVar(value="Remaining free characters: - / -")

        ttk.Label(self, textvariable=self.char_var, anchor="w", justify="left").pack(anchor=tk.W, fill=tk.X, pady=(0, 2))
    
    def update_stats(self, stats: Dict):
        try:
            local_used = stats.get('used', 0)
            local_text = f" Local: {local_used:,} chars"
            api_text = "API: Not Available"

            if stats.get('api_used') is not None and stats.get('api_limit') is not None:
                api_text = f"API: {stats['api_used']:,} / {stats['api_limit']:,} chars"
                
            display_text = f"{api_text} | {local_text}"
            self.char_var.set(display_text)
            
        except Exception as e:
            self.char_var.set("Characters: Error loading usage") 