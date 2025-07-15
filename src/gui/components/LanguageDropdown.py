import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple, Dict

class LanguageDropdown(ttk.Frame):
    def __init__(self, master, tts_generator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.tts = tts_generator
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
    
    def load_languages(self):
        """Load all available languages from TTS engine"""
        try:
            if not self.tts:
                raise ValueError("TTS engine not initialized")
                
            self.languages = self.tts.get_available_languages(format="both")
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