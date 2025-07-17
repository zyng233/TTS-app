import io
import platform
import sys
from pathlib import Path
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Scale
from .components.TextEditor import TextEditor
from .components.VoiceDropdown import VoiceDropdown
from .components.LanguageDropdown import LanguageDropdown
from .components.QuotapPanel import QuotaPanel
from core.tts import TTSGenerator
from core.utils import setup_logger

class TTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text-to-Speech Player")
        self._set_platform_specifics()
        self.is_playing = False
        self._init_audio()
        self.logger = setup_logger()
                
        try:
            self.tts_engine = TTSGenerator()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize TTS engine: {str(e)}")
            self.destroy()
            return
        
        self._setup_ui()

    def _set_platform_specifics(self):
        """Platform-specific adjustments"""
        if platform.system() == 'Darwin':
            self.geometry("620x500") 
            if getattr(sys, 'frozen', False) and '.app' in sys.executable:
                self.createcommand('tk::mac::ReopenApplication', self._on_reopen)
        else:
            self.geometry("600x480")
        self.minsize(400, 350)

    def _init_audio(self):
        """Initialize audio with platform-appropriate settings"""
        buffer_size = 2048 if platform.system() == 'Darwin' else 1024
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=buffer_size)

    def _setup_ui(self):
        style = Style("simplex") 
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Enter text:").pack(anchor=tk.W)
        self.text_editor = TextEditor(main_frame)
        self.text_editor.pack(expand=True, fill=tk.BOTH, pady=(0, 10))

        top_controls_frame = ttk.Frame(main_frame)
        top_controls_frame.pack(fill=tk.X, pady=(0, 10))

        dropdown_frame = ttk.LabelFrame(top_controls_frame, text="Language & Voice", padding=(10, 5))
        dropdown_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, anchor='center')

        # Language and voice dropdown
        self.language_dropdown = LanguageDropdown(dropdown_frame, self.tts_engine)
        self.language_dropdown.pack(fill=tk.X, pady=(0, 5))
        
        self.voice_dropdown = VoiceDropdown(dropdown_frame, self.tts_engine)
        self.voice_dropdown.pack(fill=tk.X)
        
        self.language_dropdown.load_languages()
        self.language_dropdown.dropdown.bind("<<ComboboxSelected>>", self._update_voices)
        
        voice_control = ttk.LabelFrame(top_controls_frame, text="Voice Controls", padding=(10, 5))
        voice_control.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 0))

        # Rate control
        ttk.Label(voice_control, text="Rate:").pack(anchor=tk.W)
        rate_inner_frame = ttk.Frame(voice_control)
        rate_inner_frame.pack(fill=tk.X, pady=(0, 5))
        self.rate_slider = Scale(rate_inner_frame, from_=0.25, to=4.0, value=1.0,
                                 orient=tk.HORIZONTAL, length=100, bootstyle="success")
        
        self.rate_slider.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.rate_var = tk.StringVar(value="1.0")
        self.rate_entry = ttk.Entry(rate_inner_frame, textvariable=self.rate_var, width=5)
        self.rate_entry.pack(side=tk.LEFT)
        
        # Pitch control
        ttk.Label(voice_control, text="Pitch:").pack(anchor=tk.W)
        pitch_inner_frame = ttk.Frame(voice_control)
        pitch_inner_frame.pack(fill=tk.X)
        self.pitch_slider = Scale(pitch_inner_frame, from_=-20.0, to=20.0, value=0.0,
                                  orient=tk.HORIZONTAL, length=100, bootstyle="warning")
        
        self.pitch_slider.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.pitch_var = tk.StringVar(value="0.0")
        self.pitch_entry = ttk.Entry(pitch_inner_frame, textvariable=self.pitch_var, width=5)
        self.pitch_entry.pack(side=tk.LEFT)
        
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

        ttk.Button(
            control_frame, 
            text="Stop",
            command=self.stop_audio,
            style="Stop.TButton"
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
        
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", foreground='black', background='#0078d7')
        self.style.configure("Stop.TButton", foreground='black', background='#0078d7') 
        
        self.quota_panel = QuotaPanel(main_frame)
        self.quota_panel.pack(fill=tk.X, pady=10)
        self.update_quota()
    
        # Sync slider -> rate_entry
        def update_rate_entry(event=None):
            self.rate_var.set(f"{self.rate_slider.get():.2f}")
        
        self.rate_slider.bind("<B1-Motion>", update_rate_entry)
        self.rate_slider.bind("<ButtonRelease-1>", update_rate_entry)

        # Sync slider -> pitch_entry
        def update_pitch_entry(event=None):
            self.pitch_var.set(f"{self.pitch_slider.get():.1f}")
        
        self.pitch_slider.bind("<B1-Motion>", update_pitch_entry)
        self.pitch_slider.bind("<ButtonRelease-1>", update_pitch_entry)
    
    def _update_voices(self, event=None):
        """Update available voices when language changes"""
        selected_language = self.language_dropdown.get_selected_language()
        if selected_language:
            self.voice_dropdown.load_voices_for_language(selected_language)
    
    def update_quota(self):
        """Update quota display"""
        try:
            stats = self.tts_engine.get_usage_stats()
            self.quota_panel.update_stats({
                'characters_used': stats['characters_used'],
                'characters_remaining': stats['characters_remaining'],
                'requests_used': stats['requests_used'],
                'requests_remaining': stats['requests_remaining']
            })
        except Exception as e:
            self.logger.error(f"Failed to update quota: {str(e)}")
        
        self.after(300000, self.update_quota)
        
    def play_audio(self):
        """Generate and play audio directly"""
        self.status_var.set("Generating audio...")
        self.update()

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
        
        voice_params = {
            "language_code": voice_data["language"],
            "name": voice_data["name"],
            "ssml_gender": voice_data["gender"]
        }

        is_ssml = self.ssml_var.get()
        audio_content = None

        try:
            try:
                speaking_rate = float(self.rate_var.get())
                pitch = float(self.pitch_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter numeric values for speaking rate and pitch.")
                self.status_var.set("Error: Invalid input")
                return
            
            if not (0.25 <= speaking_rate <= 4.0):
                messagebox.showwarning(
                    "Invalid Rate",
                    "Speaking rate must be between 0.25 and 4.0.\n\nNote: Some voices only support rate between 0.25 and 2.0."
                    )
                self.status_var.set("Error: Invalid rate")
                return
            
            if not (-20.0 <= pitch <= 20.0):
                messagebox.showwarning(
                    "Invalid Pitch", 
                    "Pitch must be between -20 and 20.\n\nNote: Some voices do not support custom pitch values."
                    )
                self.status_var.set("Error: Invalid pitch")
                return
    
            if is_ssml:
                audio_content = self.tts_engine.generate_to_memory(
                    text=text,
                    voice_data=voice_params,
                    speaking_rate=speaking_rate,
                    pitch=pitch,
                    is_ssml=True
                )
            else:
                audio_content = self.tts_engine.generate_to_memory(
                    text=text,
                    voice_data=voice_params,
                    speaking_rate=speaking_rate,
                    pitch=pitch,
                    is_ssml=False
                )

            self._play_audio_content(audio_content)

        except RuntimeError as e:
            if "does not support SSML" in str(e) and is_ssml:
                self._handle_ssml_fallback()
            else:
                self.status_var.set("Error during generation")
                messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")
        except Exception as e:
            self.status_var.set("Error during generation")
            messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")
        
    def _play_audio_content(self, audio_content):
        """Play audio from binary content"""
        try:
            audio_file = io.BytesIO(audio_content)
            
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.status_var.set("Playing audio...")
            
            self.after(100, self._check_playback_status)

        except Exception as e:
            self.is_playing = False
            self.status_var.set("Playback failed")
            messagebox.showerror("Playback Error", f"Could not play audio: {str(e)}")
            raise
    
    def _check_playback_status(self):
        """Check if audio is still playing"""
        if pygame.mixer.music.get_busy():
            self.after(100, self._check_playback_status)
        else:
            self.is_playing = False
            self.status_var.set("Ready")

    def stop_audio(self):
        """Stop currently playing audio"""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                self.is_playing = False
                self.status_var.set("Playback stopped")
                self.after(3000, lambda: self.status_var.set("Ready"))
        except Exception as e:
            self.status_var.set("Stop failed")
            messagebox.showerror("Stop Error", f"Could not stop audio: {str(e)}")

    def _handle_ssml_fallback(self):
        """Handle SSML fallback scenario"""
        self.status_var.set("Voice doesn't support SSML - using plain text")
        self.update_idletasks()
        self.after(3000, lambda: self.status_var.set("Ready"))

    def _on_reopen(self):
        """Handle macOS app reopen event (for App Store)"""
        self.deiconify()

    def on_close(self):
        """Cleanup when closing the app"""
        pygame.mixer.quit()
        self.destroy()
        
if __name__ == "__main__":
    if platform.system() == 'Darwin' and getattr(sys, 'frozen', False):
        try:
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            if bundle:
                info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if info:
                    info['CFBundleName'] = "TTS Player"
        except ImportError:
            pass

    app = TTSApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()