import tkinter as tk
from tkinter import ttk
from typing import List

class AudioFormatDropdown(ttk.Frame):
    """Dialog window for selecting audio format"""
    def __init__(self, master, tts_engine=None, **kwargs):
        super().__init__(master, **kwargs)
        self.tts_engine=tts_engine
        self._setup_ui()

    def _setup_ui(self):
        ttk.Label(self, text="Select audio format:").pack(anchor=tk.W)
        self.format_var = tk.StringVar(value="MP3")
        initial_formats = (
            self.tts_engine.audio_config.get_supported_formats()
            if self.tts_engine and self.tts_engine.audio_config
            else ["MP3"]
        )
        self.format_dropdown = ttk.Combobox(
            self, 
            textvariable=self.format_var,
            values=initial_formats,
            state="readonly",
            width=8
        )
        self.format_dropdown.pack(fill=tk.X)
        
    def set_available_formats(self, formats: List[str]):
        """Dynamically update available formats"""
        self.format_dropdown['values'] = formats
        if formats:
            self.format_var.set(formats[0])
    
    def get_selected_format(self):
        """Returns the selected format in lowercase"""
        return self.format_var.get().lower()
        
    def set_selected_format(self, format_name):
        if format_name.upper() in self.format_dropdown['values']:
            self.format_var.set(format_name.upper())