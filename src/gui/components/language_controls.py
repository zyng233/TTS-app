import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple, Dict

class LanguageControls(ttk.Frame):
    def __init__(self, master, tts_engine=None, **kwargs):
        super().__init__(master, **kwargs)
        self.tts_engine = tts_engine
        self.languages: List[Tuple[str, str]] = []
        self.name_to_code: Dict[str, str] = {} 
        self._setup_ui()
    
    def _setup_ui(self):
        ttk.Label(self, text="Language:").pack(side=tk.LEFT, padx=(0, 5))
        self.language_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.language_var,
            state="readonly",
            width=15
        )
        self.dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def load_languages(self, model):
        """Load all available languages from TTS engine"""
        try:
            if not self.tts_engine:
                raise ValueError("TTS engine not initialized")
            
            self.languages = self.tts_engine.get_available_languages(model, format="both")
            self.name_to_code = {name: code for code, name in self.languages}
            display_names = [name for (code, name) in self.languages]
            self.dropdown['values'] = display_names
            
            if display_names:
                self.language_var.set(display_names[0])
        except Exception as e:
            messagebox.showerror("Language Error", f"Failed to load languages:\n{str(e)}")
            raise
            
    def get_selected_language(self) -> Optional[str]:
        """Get the currently selected language code"""
        selected_name = self.language_var.get()
        return self.name_to_code.get(selected_name)
    
    def get_selected_language_name(self) -> Optional[str]:
        """Get the currently selected language NAME"""
        return self.language_var.get()
    
    def get_first_language(self) -> Optional[str]:
        """Return the first available language code, if any"""
        if self.languages:
            return self.languages[0][0]
        return None
    
    def set_tts_service(self, tts_engine):
        """Update the TTS engine and current service"""
        self.tts_engine = tts_engine
        self.language_var.set("")
        self.dropdown['values'] = []
        self.languages = []