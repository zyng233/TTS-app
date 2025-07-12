import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import io
import pygame
from .components.TextEditor import TextEditor
from .components.VoiceDropdown import VoiceDropdown
from .components.LanguageDropdown import LanguageDropdown 
from core.tts import TTSGenerator

class TTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text-to-Speech Player")
        self.geometry("600x400")
        self.minsize(400, 300)
        
        pygame.mixer.init()
        
        try:
            self.tts_engine = TTSGenerator()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize TTS engine: {str(e)}")
            self.destroy()
            return
        
        self._setup_ui()
        
    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Enter text:").pack(anchor=tk.W)
        self.text_editor = TextEditor(main_frame)
        self.text_editor.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
 
        self.language_dropdown = LanguageDropdown(main_frame, self.tts_engine)
        self.language_dropdown.pack(fill=tk.X, pady=(0, 5))
        
        self.voice_dropdown = VoiceDropdown(main_frame, self.tts_engine)
        self.voice_dropdown.pack(fill=tk.X, pady=(0, 10))
        
        self.language_dropdown.dropdown.bind("<<ComboboxSelected>>", self._update_voices)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)
        
        self.ssml_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="SSML", variable=self.ssml_var).pack(side=tk.LEFT)
        
        ttk.Button(
            control_frame, 
            text="Play Audio",
            command=self.play_audio,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
        
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", foreground='white', background='#0078d7')
    
        self.language_dropdown.load_languages()
        
    def _update_voices(self, event=None):
        """Update available voices when language changes"""
        selected_language = self.language_dropdown.get_selected_language()
        if selected_language:
            self.voice_dropdown.load_voices_for_language(selected_language)
            
    def play_audio(self):
        """Generate and play audio directly"""
        text = self.text_editor.get_text()
        if not text:
            self.status_var.set("Error: Please enter some text")
            messagebox.showwarning("Input Error", "Please enter some text to convert to speech.")
            return
            
        voice_data = self.voice_dropdown.get_selected_voice()
        if not voice_data:
            self.status_var.set("Error: No voice selected")
            messagebox.showwarning("Voice Error", "Please select a voice.")
            return
        
        is_ssml = self.ssml_var.get()
        
        self.status_var.set("Generating speech...")
        self.update_idletasks()  
        
        try:
            audio_content = self.tts_engine.generate_to_memory(
                text=text,
                is_ssml=is_ssml,
                voice_data={  # Correct parameter name
                    "language_code": voice_data["language"],
                    "name": voice_data["name"],
                    "ssml_gender": voice_data["gender"]
                }
            )
            
            self._play_audio_content(audio_content)
            self.status_var.set("Playing audio...")
            
        except Exception as e:
            self.status_var.set("Error during generation")
            messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")

            raise
        
    def _play_audio_content(self, audio_content):
        """Play audio from binary content"""
        try:
            audio_file = io.BytesIO(audio_content)
            
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
        except Exception as e:
            self.status_var.set("Playback failed")
            messagebox.showerror("Playback Error", f"Could not play audio: {str(e)}")
            raise
    
    def on_close(self):
        """Cleanup when closing the app"""
        pygame.mixer.quit()
        self.destroy()
        
if __name__ == "__main__":
    app = TTSApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()