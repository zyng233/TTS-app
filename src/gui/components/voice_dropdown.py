import tkinter as tk
from tkinter import ttk

class VoiceDropdown(ttk.Frame):
    def __init__(self, master, voices=None, **kwargs):
        super().__init__(master, **kwargs)
        self.voices = voices or self._default_voices()
        self._setup_ui()
        
    def _default_voices(self):
        return [
            "en-US-Wavenet-A",
            "en-US-Wavenet-B",
            "en-US-Wavenet-D",
            "en-US-Neural2-J"
        ]
    
    def _setup_ui(self):
        ttk.Label(self, text="Voice:").pack(side=tk.LEFT)
        self.voice_var = tk.StringVar(value=self.voices[0])
        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.voice_var,
            values=self.voices,
            state="readonly",
            width=20
        )
        self.dropdown.pack(side=tk.LEFT, padx=5)
    
    def get_selected_voice(self):
        """Get the currently selected voice"""
        return self.voice_var.get()
    
    def set_voices(self, voices):
        """Update available voices"""
        self.voices = voices
        self.dropdown['values'] = voices
        if voices:
            self.voice_var.set(voices[0])