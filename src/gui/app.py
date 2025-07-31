import io
import platform
import sys
import pygame
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkbootstrap import Style
from ttkbootstrap.widgets import Progressbar
from .components.text_editor import TextEditor
from .components.audio_formats import AudioFormatDropdown
from .components.voice_controls import VoiceControls
from .components.language_controls import LanguageControls
from .components.quota_usage import QuotaPanel
from .components.service_switcher import ServiceSwitcher
from core.auth import AuthManager
from core.tts.factory import TTSFactory, TTSService
from core.tts.voice_factory import VoiceManagerFactory
from core.tts.service_types import TTSService
from core.utils import setup_logger
from gui.layouts.google import GoogleTTSLayout
from gui.layouts.elevenlabs import ElevenLabsLayout

class TTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text-to-Speech Player")
        self.auth_manager = AuthManager()
        self._set_platform_specifics()
        self._init_audio()
        self.logger = setup_logger()
        
        # Service management
        self.current_service = TTSService.GOOGLE
        self.voice_manager_factory = VoiceManagerFactory()
        self.current_voice_manager = None
        self.tts_engine = None
        self._initialize_tts_service()
        self._setup_ui()

    def _set_platform_specifics(self):
        """Platform-specific adjustments"""
        if platform.system() == 'Darwin':
            self.geometry("650x670") 
            if getattr(sys, 'frozen', False) and '.app' in sys.executable:
                self.createcommand('tk::mac::ReopenApplication', self._on_reopen)
        else:
            self.geometry("630x670")
        self.minsize(430, 540)

    def _init_audio(self):
        """Initialize audio with platform-appropriate settings"""
        buffer_size = 2048 if platform.system() == 'Darwin' else 1024
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=buffer_size)

    def _initialize_tts_service(self):
        """Initialize the current TTS service"""
        try:
            self.tts_engine = TTSFactory.create(
                service_type=self.current_service,
                auth_manager=self.auth_manager,
                update_callback=lambda stats: self.update_quota(stats)
            )
            self.current_voice_manager = self.tts_engine.voice_manager
        except Exception as e:
            messagebox.showerror("Initialization Error", 
                f"Failed to initialize {self.current_service.name} TTS engine: {str(e)}")
            raise
    
    def _setup_ui(self):
        self.style = Style("simplex") 
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        available_services = {
            "Google": TTSService.GOOGLE,
            "ElevenLabs": TTSService.ELEVENLABS
        }
        self.service_switcher = ServiceSwitcher(
            container, 
            self, 
            available_services,
            command=self.switch_service
        )
        self.service_switcher.pack(fill=tk.X, padx=10, pady=5)

        self._setup_main_content(container)
            
    def _setup_main_content(self, parent):
        """Setup the main content area with original layout"""
        # Scroll bar setup
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
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
        
    def switch_service(self, service: TTSService):
        """Switch between different TTS services"""
        if service == self.current_service:
            return
        try:
            if hasattr(self, 'tts_engine'):
                del self.tts_engine

            self.current_service = service
            self._initialize_tts_service()
            self._setup_service_controls()
            self.update_quota()
            self.is_playing = False
            self.is_paused = False
            
            # Reset audio and disable download
            self.current_audio_content = None
            if hasattr(self, 'download_button'):
                self.download_button.config(state=tk.DISABLED)
                    
            self.model = (
                self.service_controls.get_selected_model()
                if hasattr(self.service_controls, "get_selected_model")
                else None
            )
            
            if hasattr(self, 'language_dropdown'):
                self.language_dropdown.set_tts_service(self.tts_engine)
                self.language_dropdown.load_languages(self.model)
                    
            if hasattr(self, 'voice_dropdown'):
                self.voice_dropdown.set_tts_engine(self.tts_engine)
                self.voice_dropdown.set_voice_manager(self.current_voice_manager)
                self.voice_dropdown.clear_voices()

                first_lang = self.language_dropdown.get_first_language()
                if first_lang:
                    self.voice_dropdown.load_voices_for_language(first_lang)
                    
            if hasattr(self, 'format_dropdown'):
                self.format_dropdown.set_available_formats(self.tts_engine.audio_config.get_supported_formats())

            messagebox.showinfo("Service Changed", f"Switched to {service.name} service")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch to {service.name}: {str(e)}")
        
    def _setup_text_editor(self, parent):
        """Create and pack the main text editor for input."""
        ttk.Label(parent, text="Enter text:").pack(anchor=tk.W)
        self.text_editor = TextEditor(parent)
        self.text_editor.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
    
    def _setup_top_controls(self, parent):
        """Create the top controls section."""  
        self.top_controls_frame = ttk.Frame(parent)
        self.top_controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.top_controls_frame.columnconfigure(0, weight=2)
        self.top_controls_frame.columnconfigure(1, weight=3)

        left_frame = ttk.Frame(self.top_controls_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        right_frame = ttk.Frame(self.top_controls_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Service-specific controls
        self.service_controls_frame = ttk.Frame(right_frame)
        self.service_controls_frame.pack(fill=tk.BOTH, expand=True)
        self._setup_service_controls()

        self._setup_language_voice_dropdowns(left_frame)
        self._setup_format_selector(left_frame) 
    
    def _setup_language_voice_dropdowns(self, parent):
        """Initialize and pack the language and voice selection dropdowns."""
        dropdown_frame = ttk.LabelFrame(parent, text="Language & Voice", padding=(10, 5))
        dropdown_frame.pack(fill=tk.X, pady=(0, 5))

        self.language_dropdown = LanguageControls(dropdown_frame, self.tts_engine)
        self.language_dropdown.pack(fill=tk.X, pady=(0, 5))

        self.voice_dropdown = VoiceControls(dropdown_frame, self.tts_engine)
        self.voice_dropdown.pack(fill=tk.X)

        model = self.service_controls.get_selected_model()
        self.language_dropdown.load_languages(model=model)
        self.language_dropdown.dropdown.bind("<<ComboboxSelected>>", self._update_voices)
        self.voice_dropdown.set_voice_manager(self.current_voice_manager)
        first_lang = self.language_dropdown.get_first_language()
        if first_lang:
            self.voice_dropdown.load_voices_for_language(first_lang)

    def _setup_format_selector(self, parent):
        """Setup audio format selection below language/voice dropdowns"""
        format_frame = ttk.LabelFrame(parent, text="Output Format", padding=(10, 5))
        format_frame.pack(fill=tk.X)
        
        control_frame = ttk.Frame(format_frame)
        control_frame.pack(fill=tk.X)
        
        self.format_dropdown = AudioFormatDropdown(control_frame, self.tts_engine)
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
        
    def _setup_service_controls(self):
        """Setup service-specific controls"""
        for widget in self.service_controls_frame.winfo_children():
            widget.destroy()
            
        if self.current_service == TTSService.GOOGLE:
            self.service_controls = GoogleTTSLayout(self.service_controls_frame)
        elif self.current_service == TTSService.ELEVENLABS:
            self.service_controls = ElevenLabsLayout(self.service_controls_frame, self.language_dropdown, self.voice_dropdown)
    
    def _setup_control_buttons(self, parent):
        """Create and pack audio control buttons""" 
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X)

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
    
    def update_status_meter(self, progress, status_text):
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
        self.update_idletasks()
        self.update()
    
    def _update_voices(self, event=None):
        """Update available voices when language changes"""    
        selected_language = self.language_dropdown.get_selected_language()
        self.voice_dropdown.load_voices_for_language(selected_language)   
    
    def update_quota(self, stats=None):
        """Update quota display"""    
        try:
            stats = stats or self.tts_engine.get_usage_stats()
            self.quota_panel.update_stats(stats)
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
        
        voice_params = self._get_voice_parameters(voice_data)
        tts_params = self.service_controls.get_voice_parameters()
        
        if tts_params is None:
            self.update_status_meter(0, "Invalid parameters")
            return
        
        self.update_status_meter(30, "Generating...")

        try:
            self.update_status_meter(50, "Generating...")
            self.current_audio_format = self.format_dropdown.get_selected_format()
            audio_content = self.tts_engine.generate_to_memory(
                text=text,
                voice_data=voice_params,
                audio_format=self.current_audio_format,
                **tts_params
            )

            self.update_status_meter(80, "Generating...")
            self._play_audio_content(audio_content)

        except RuntimeError as e:
            if "does not support SSML" in str(e) and tts_params.get('is_ssml', False):
                self._handle_ssml_fallback()
            else:
                messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")
                self.update_status_meter(0, "Generation Error")
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate speech:\n{str(e)}")
            self.update_status_meter(0, "Generation Error")
    
    def _get_voice_parameters(self, voice_data):
        """Get service-specific voice parameters"""
        if self.current_service == TTSService.GOOGLE:
            return {
                "language_code": voice_data["language"],
                "name": voice_data["name"],
                "ssml_gender": voice_data["gender"]
            }
        elif self.current_service == TTSService.ELEVENLABS:
            return {
                "voice_id": voice_data["id"],
                "model": self.service_controls.get_voice_parameters().get("model")
            }  
            
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