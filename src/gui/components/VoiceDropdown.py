import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional

class VoiceDropdown(ttk.Frame):
    def __init__(self, master, tts_generator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.voices: List[Dict] = []
        self.tts = tts_generator
        self._setup_ui()
    
    def _setup_ui(self):
        self.details_var = tk.StringVar()
        ttk.Label(self, text="Voice: ").grid(row=0, column=0, sticky=tk.W)
        self.voice_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.voice_var,
            state="readonly",
            width=25
        )
        self.dropdown.grid(row=0, column=1, sticky=tk.EW)
        self.dropdown.bind("<<ComboboxSelected>>", self._update_details)
        
        ttk.Label(self, textvariable=self.details_var, wraplength=300).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.columnconfigure(1, weight=1)

    def load_voices_for_language(self, language_code: str):
        """Load voices for a specific language code."""
        try:
            if not self.tts:
                raise ValueError("TTS engine not initialized")
                
            self.voice_var.set("")
            self.details_var.set("Loading voices...")
            self.update_idletasks()
            
            self.voices = self.tts.get_voices_for_language(language_code)
            voice_names = [v['name'] for v in self.voices]
            
            if not voice_names:
                raise ValueError("No voices available for selected language")
                
            self.dropdown['values'] = voice_names
            self.voice_var.set(voice_names[0])
            self._update_details()
            
        except Exception as e:
            messagebox.showerror("Voice Error", f"Failed to load voices:\n{str(e)}")
            self.details_var.set("Error loading voices")

    def _update_details(self, event=None):
        """Update voice details when selection changes."""
        selected = self.voice_var.get()
        voice = next((v for v in self.voices if v['name'] == selected), None)
        if voice:
            details = (
                f"Type: {voice.get('voice_type', 'Standard')} | "
                f"Gender: {voice['gender']}"
            )
            self.details_var.set(details)
        else:
            self.details_var.set("No voice details available")

    def get_selected_voice(self) -> Optional[Dict]:
        """Get complete details of the currently selected voice."""
        if not self.voices or not self.voice_var.get():
            return None
        
        selected = self.voice_var.get()
        try:
            return next(v for v in self.voices if v['name'] == selected)
        except StopIteration:
            return None

    def clear_voices(self):
        """Reset the voice dropdown"""
        self.voice_var.set("")
        self.details_var.set("No voice selected")
        self.dropdown['values'] = []
        self.voices = []

    def set_tts_engine(self, tts_generator):
        self.tts = tts_generator
        self.clear_voices()