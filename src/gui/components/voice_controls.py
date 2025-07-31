import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
from core.tts.base_voice import BaseVoiceManager

class VoiceControls(ttk.Frame):
    def __init__(self, master, tts_engine=None, **kwargs):
        super().__init__(master, **kwargs)
        self.voices: List[Dict] = []
        self.tts_engine= tts_engine
        self.voice_manager = None
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

    def load_voices_for_language(self, language: str):
        """Load voices for a specific language."""
        try:
            if not self.tts_engine:
                raise ValueError("TTS engine not initialized")
                
            self.voice_var.set("")
            self.details_var.set("Loading voices...")
            self.update_idletasks()
            self.voices = self.tts_engine.get_available_voices(language)
            voice_names = [v['name'] for v in self.voices]
            
            if not voice_names:
                raise ValueError("No voices available for selected language")
                
            self.dropdown['values'] = voice_names
            self.voice_var.set(voice_names[0])
            self._update_details()
            
        except Exception as e:
            messagebox.showerror("Voice Error", f"Failed to load voices:\n{str(e)}")
            self.details_var.set("Error loading voices")
            raise

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
    
    def _update_details(self, event=None):
        """Update voice details when selection changes"""
        selected = self.voice_var.get()
        voice = next((v for v in self.voices if v['name'] == selected), None)

        if voice and self.voice_manager:
            details = self.voice_manager.format_voice_details(voice)
            self.details_var.set(details)
        else:
            self.details_var.set("No voice details available")
            
    def set_voice_manager(self, voice_manager: BaseVoiceManager):
        """Set the voice manager and clear current selection"""
        self.voice_manager = voice_manager
        self.clear_voices()
        
    def set_tts_engine(self, tts_engine):
        self.tts_engine = tts_engine