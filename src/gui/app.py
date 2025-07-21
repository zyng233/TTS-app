import io
import platform
import sys
from pathlib import Path
import pygame
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkbootstrap import Style
from ttkbootstrap.widgets import Scale, Progressbar
from .components.TextEditor import TextEditor
from .components.AudioProfileDropdown import AudioProfileDropdown
from .components.AudioFormatDropdown import AudioFormatDropdown
from .components.VoiceDropdown import VoiceDropdown
from .components.LanguageDropdown import LanguageDropdown
from .components.QuotapPanel import QuotaPanel
from core.tts.factory import TTSFactory, TTSService
from core.utils import setup_logger

class TTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text-to-Speech Player")
        self._set_platform_specifics()
        self.is_playing = False
        self.is_paused = False
        self._init_audio()
        self.logger = setup_logger()
                
        try:
            self.tts_engine = TTSFactory.create(
                TTSService.GOOGLE,
                update_callback=lambda stats: self.update_quota(stats)
            )
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize TTS engine: {str(e)}")
            self.destroy()
            return
        
        self._setup_ui()
        self.update_quota()

    def _set_platform_specifics(self):
        """Platform-specific adjustments"""
        if platform.system() == 'Darwin':
            self.geometry("620x550") 
            if getattr(sys, 'frozen', False) and '.app' in sys.executable:
                self.createcommand('tk::mac::ReopenApplication', self._on_reopen)
        else:
            self.geometry("600x530")
        self.minsize(400, 400)

    def _init_audio(self):
        """Initialize audio with platform-appropriate settings"""
        buffer_size = 2048 if platform.system() == 'Darwin' else 1024
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=buffer_size)

    def _setup_ui(self):
        self.style = Style("simplex") 
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Scroll bar
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_wrapper = ttk.Frame(canvas, padding=(20, 0))
        self.main_frame = ttk.Frame(self.main_wrapper)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame_id = canvas.create_window((0, 0), window=self.main_wrapper, anchor="nw")
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.main_wrapper.bind("<Configure>", on_configure)

        def on_canvas_resize(event):
            canvas.itemconfig(self.main_frame_id, width=event.width)

        canvas.bind("<Configure>", on_canvas_resize)
        
        self.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._setup_text_editor(self.main_frame)
        self._setup_top_controls(self.main_frame)
        self._setup_control_buttons(self.main_frame)
        self._setup_status_bar(self.main_frame)
        self._setup_bindings()

    def _setup_text_editor(self, parent):
        """Create and pack the main text editor for input."""
        ttk.Label(parent, text="Enter text:").pack(anchor=tk.W)
        self.text_editor = TextEditor(parent)
        self.text_editor.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
    
    def _setup_top_controls(self, parent):
        """Create the top controls section."""
        top_controls_frame = ttk.Frame(parent)
        top_controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        top_controls_frame.columnconfigure(0, weight=2)
        top_controls_frame.columnconfigure(1, weight=1)

        left_frame = ttk.Frame(top_controls_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        right_frame = ttk.Frame(top_controls_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")

        self._setup_language_voice_dropdowns(left_frame)
        self._setup_audio_profile(left_frame)  
        
        self._setup_voice_controls(right_frame)
        self._setup_format_selector(right_frame) 
    
    def _setup_language_voice_dropdowns(self, parent):
        """Initialize and pack the language and voice selection dropdowns."""
        dropdown_frame = ttk.LabelFrame(parent, text="Language & Voice", padding=(10, 5))
        dropdown_frame.pack(fill=tk.X, pady=(0, 5)) 

        self.language_dropdown = LanguageDropdown(dropdown_frame, self.tts_engine)
        self.language_dropdown.pack(fill=tk.X, pady=(0, 5))

        self.voice_dropdown = VoiceDropdown(dropdown_frame, self.tts_engine)
        self.voice_dropdown.pack(fill=tk.X)

        self.language_dropdown.load_languages()
        self.language_dropdown.dropdown.bind("<<ComboboxSelected>>", self._update_voices)

    def _setup_format_selector(self, parent):
        """Setup audio format selection below language/voice dropdowns"""
        format_frame = ttk.LabelFrame(parent, text="Output Format", padding=(10, 5))
        format_frame.pack(fill=tk.X)
        
        control_frame = ttk.Frame(format_frame)
        control_frame.pack(fill=tk.X)
        
        self.format_dropdown = AudioFormatDropdown(control_frame)
        self.format_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_button = ttk.Button(
            control_frame,
            text="↓ Download Audio", 
            command=self._on_download_clicked,
            style="info.TButton",
            state=tk.DISABLED 
        )
        self.download_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.current_audio_content = None
    
    def _setup_voice_controls(self, parent):
        """Create and pack voice control"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        voice_control = ttk.LabelFrame(container, text="Voice Controls", padding=(10, 5))
        voice_control.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Rate
        ttk.Label(voice_control, text="Rate:").pack(anchor=tk.W)
        rate_frame = ttk.Frame(voice_control)
        rate_frame.pack(fill=tk.X, pady=(0, 5))

        self.rate_slider = Scale(rate_frame, from_=0.25, to=4.0, value=1.0,
                                orient=tk.HORIZONTAL, length=100, bootstyle="success")
        self.rate_slider.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        self.rate_var = tk.StringVar(value="1.0")
        self.rate_entry = ttk.Entry(rate_frame, textvariable=self.rate_var, width=5)
        self.rate_entry.pack(side=tk.LEFT)

        # Pitch
        ttk.Label(voice_control, text="Pitch:").pack(anchor=tk.W)
        pitch_frame = ttk.Frame(voice_control)
        pitch_frame.pack(fill=tk.X)

        self.pitch_slider = Scale(pitch_frame, from_=-20.0, to=20.0, value=0.0,
                                orient=tk.HORIZONTAL, length=100, bootstyle="warning")
        self.pitch_slider.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        self.pitch_var = tk.StringVar(value="0.0")
        self.pitch_entry = ttk.Entry(pitch_frame, textvariable=self.pitch_var, width=5)
        self.pitch_entry.pack(side=tk.LEFT)
        
    def _setup_audio_profile(self, parent):
        """Audio Profile dropdown moved to left column"""
        audio_profile_frame = ttk.LabelFrame(parent, text="Audio Profile", padding=(10, 5))
        audio_profile_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.audio_profile_dropdown = AudioProfileDropdown(audio_profile_frame)
        self.audio_profile_dropdown.pack(fill=tk.X)
    
    def _setup_control_buttons(self, parent):
        """Create and pack audio control buttons""" 
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X)

        # SSML Toggle
        self.ssml_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="SSML", variable=self.ssml_var).pack(side=tk.LEFT)

        # Control Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="⏹ Stop", command=self.stop_audio,
                style="danger.TButton").pack(side=tk.RIGHT, padx=(0, 5))
    
        self.pause_button = ttk.Button(button_frame, text="⏯ Pause", 
                                    command=self.toggle_pause,
                                    style="warning.TButton")
        self.pause_button.pack(side=tk.RIGHT, padx=5)  
        
        ttk.Button(button_frame, text="▶ Play", command=self.play_audio,
              style="success.TButton").pack(side=tk.RIGHT, padx=(5, 0))
    
    def _setup_status_bar(self, parent):
        """Create a status bar and quota panel at the bottom."""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, pady=(5, 0))

        self.progress_var = tk.IntVar(value=0)
        self.status_bar = Progressbar(
            self.status_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            bootstyle="info-striped"
        )
        self.status_bar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))

        self.status_label = ttk.Label(self.status_frame, text="Ready", anchor="w")
        self.status_label.pack(side=tk.RIGHT)

        self.quota_panel = QuotaPanel(parent)
        self.quota_panel.pack(fill=tk.X, pady=10)
        self.update_quota()

    def _setup_bindings(self):
        """Bind slider events to update rate and pitch entry fields.""" 
        def update_rate_entry(event=None):
            self.rate_var.set(f"{self.rate_slider.get():.2f}")
        self.rate_slider.bind("<B1-Motion>", update_rate_entry)
        self.rate_slider.bind("<ButtonRelease-1>", update_rate_entry)

        def update_pitch_entry(event=None):
            self.pitch_var.set(f"{self.pitch_slider.get():.1f}")
        self.pitch_slider.bind("<B1-Motion>", update_pitch_entry)
        self.pitch_slider.bind("<ButtonRelease-1>", update_pitch_entry)
        
        self.bind("<space>", lambda e: self.toggle_pause())
        self.bind("<s>", lambda e: self.stop_audio())
        self.bind("<p>", lambda e: self.play_audio())

    def update_status_meter(self, progress, status_text):
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
        self.update_idletasks()
        self.update()
    
    def _update_voices(self, event=None):
        """Update available voices when language changes"""       
        selected_language = self.language_dropdown.get_selected_language()
        if selected_language:
            self.voice_dropdown.load_voices_for_language(selected_language)
    
    def update_quota(self, stats=None):
        """Update quota display"""    
        try:
            stats = stats or self.tts_engine.get_usage_stats()
            self.quota_panel.update_stats({
                'used': stats['used'],
                'remaining': stats['remaining'],
                'source': stats['source'],
                'service': 'google'
            })
        except Exception as e:
            self.logger.error(f"Failed to update quota: {str(e)}")
        
        self.after(300000, self.update_quota)
        
    def play_audio(self):
        """Generate and play audio directly"""
        self.stop_audio()
        self.update_status_meter(10, "Generating...")

        text = self.text_editor.get_text()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text to convert to speech.")
            self.update_status_meter(0, "Input Error")
            return
            
        voice_data = self.voice_dropdown.get_selected_voice()
        if not voice_data:
            messagebox.showwarning("Voice Error", "Please select a voice.")
            self.update_status_meter(0, "Input Error")
            return
        
        voice_params = {
            "language_code": voice_data["language"],
            "name": voice_data["name"],
            "ssml_gender": voice_data["gender"]
        }

        is_ssml = self.ssml_var.get()
        audio_content = None
        self.update_status_meter(30, "Generating...")

        try:
            try:
                speaking_rate = float(self.rate_var.get())
                pitch = float(self.pitch_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter numeric values for speaking rate and pitch.")
                return
            
            if not (0.25 <= speaking_rate <= 4.0):
                messagebox.showwarning(
                    "Invalid Rate",
                    "Speaking rate must be between 0.25 and 4.0.\n\nNote: Some voices only support rate between 0.25 and 2.0."
                    )
                self.update_status_meter(0, "Invalid Rate")
                return
            
            if not (-20.0 <= pitch <= 20.0):
                messagebox.showwarning(
                    "Invalid Pitch", 
                    "Pitch must be between -20 and 20.\n\nNote: Some voices do not support custom pitch values."
                    )
                self.update_status_meter(0, "Invalid Pitch")
                return

            self.update_status_meter(50, "Generating...")
            
            selected_profile = self.audio_profile_dropdown.get_selected_profile()
            effects_profile_id = [selected_profile] if selected_profile else None
            self.current_audio_format = "MP3"
            
            audio_content = self.tts_engine.generate_to_memory(
                text=text,
                voice_data=voice_params,
                audio_format=self.current_audio_format,
                speaking_rate=speaking_rate,
                pitch=pitch,
                is_ssml=is_ssml,
                effects_profile_id=effects_profile_id
            )

            self.update_status_meter(80, "Generating...")
            self._play_audio_content(audio_content)

        except RuntimeError as e:
            if "does not support SSML" in str(e) and is_ssml:
                self._handle_ssml_fallback()
            else:
                messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")
                self.update_status_meter(0, "Generation Error")
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")
            self.update_status_meter(0, "Generation Error")
        
    def _play_audio_content(self, audio_content):
        """Play audio from binary content"""
        self.current_audio_content = audio_content
        self.download_button.config(state=tk.NORMAL)
        try:
            audio_file = io.BytesIO(audio_content)
            
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.update_status_meter(100, "Playing audio...")
            self.after(100, self._check_playback_status)

        except Exception as e:
            self.is_playing = False
            messagebox.showerror("Playback Error", f"Could not play audio: {str(e)}")
            self.update_status_meter(0, "Playback Error")
            raise
    
    def toggle_pause(self):
        """Toggle between pause and resume"""
        if not self.is_playing:
            messagebox.showinfo("Info", "No audio is currently playing")
            return
    
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.update_status_meter(100, "Playing audio...")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_button.config(text="Resume")
            self.update_status_meter(50, "Paused")
                
    def _check_playback_status(self):
        """Check if audio is still playing"""
        if self.is_paused:
            return

        if pygame.mixer.music.get_busy():
            self.after(100, self._check_playback_status)
        else:
            self.is_playing = False
            self.update_status_meter(0, "Ready")

    def stop_audio(self):
        """Stop currently playing audio"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.update_status_meter(100, "Playback stopped.")
            self.after(3000, lambda: self.update_status_meter(0, "Ready"))
        except Exception as e:
            messagebox.showerror("Stop Error", f"Could not stop audio: {str(e)}")
    
    def _on_download_clicked(self):
        """Wrapper method for download button click"""
        if hasattr(self, 'format_dropdown'):
            selected_format = self.format_dropdown.get_selected_format()
            self.download_audio(selected_format)
        else:
            messagebox.showerror("Error", "Format selection not available")
           
    def download_audio(self, selected_format):
        """Save the generated audio to a file with format selection"""
        if not self.current_audio_content:
            messagebox.showwarning("No Audio", "No audio has been generated yet")
            return
        
        text_sample = self.text_editor.get_text()[:20].strip().replace(" ", "_")
        default_name = f"tts_output_{text_sample or 'audio'}.{selected_format}"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{selected_format}",
            filetypes=[(f"{selected_format.upper()} files", f"*.{selected_format}"), ("All files", "*.*")],
            initialfile=default_name,
            title="Save Audio File"
        )
        
        if file_path:
            try:
                with open(file_path, "wb") as f:
                    f.write(self.current_audio_content)
                messagebox.showinfo("Success", f"Audio saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def _handle_ssml_fallback(self):
        """Handle SSML fallback scenario"""
        self.update_status_meter(0, "Voice doesn't support SSML - using plain text")
        self.update_idletasks()
        self.after(3000, lambda: self.update_status_meter(0, "Ready"))

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