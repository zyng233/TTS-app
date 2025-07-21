import tkinter as tk
from tkinter import ttk

class AudioFormatDropdown(ttk.Frame):
    """Dialog window for selecting audio format"""
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Select audio format:").pack(anchor=tk.W)
        self.format_var = tk.StringVar(value="MP3")
        self.format_dropdown = ttk.Combobox(
            self, 
            textvariable=self.format_var,
            values=["MP3", "WAV", "OGG"],
            state="readonly",
            width=8
        )
        self.format_dropdown.pack(fill=tk.X)
    
    def get_selected_format(self):
        """Returns the selected format in lowercase"""
        return self.format_var.get().lower()
        
    def set_selected_format(self, format_name):
        """Set the dropdown to a specific format"""
        if format_name.upper() in ["MP3", "WAV", "OGG"]:
            self.format_var.set(format_name.upper())