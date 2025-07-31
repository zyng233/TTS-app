import tkinter as tk
from tkinter import ttk
from ttkbootstrap.widgets import Progressbar

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        self.progress_var = tk.IntVar(value=0)
        self.progress = Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            bootstyle="info-striped"
        )
        self.progress.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))

        self.status_label = ttk.Label(self, text="Ready", anchor="w")
        self.status_label.pack(side=tk.RIGHT)
        
    def update_status(self, progress: int, message: str):
        self.progress_var.set(progress)
        self.status_label.config(text=message)