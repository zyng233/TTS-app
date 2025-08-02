import io
import platform
import sys
import pygame
import tkinter as tk
from threading import Thread
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
        self.is_playing = False
        self.is_paused = False
        
        # Service management
        self.services = {}
        self.voice_manager_factory = VoiceManagerFactory()
        self._initialize_tts_service()
        self._activate_service(TTSService.GOOGLE)
        self._setup_ui()

    def _set_platform_specifics(self):
        """Platform-specific adjustments"""
        if platform.system() == 'Linux':
            self.style = Style("flatly") 
            self.tk.call('tk', 'scaling', 1.25)
            self.geometry("650x650")
            
            self.tk_setPalette(background='#f0f0f0')
            self.option_add('*TCombobox*Listbox.background', '#ffffff')
            self.option_add('*TCombobox*Listbox.foreground', '#000000')
        elif platform.system() == 'Darwin':
            self.geometry("650x630") 
            if getattr(sys, 'frozen', False) and '.app' in sys.executable:
                self.createcommand('tk::mac::ReopenApplication', self._on_reopen)
        else:
            self.geometry("630x630")
        self.minsize(430, 500)

    def _init_audio(self):
        """Initialize audio with platform-appropriate settings"""
        buffer_size = 2048 if platform.system() == 'Darwin' else 1024
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=buffer_size)
            
    def _initialize_tts_service(self):
        """Initialize all TTS services"""
        try:
            self.services[TTSService.GOOGLE] = TTSFactory.create(
                service_type=TTSService.GOOGLE,
                auth_manager=self.auth_manager,
                update_callback=lambda stats: self.update_quota(stats)
            )
            self.services[TTSService.ELEVENLABS] = TTSFactory.create(
                service_type=TTSService.ELEVENLABS,
                auth_manager=self.auth_manager,
                update_callback=lambda stats: self.update_quota(stats)
            )
        except Exception as e:
            messagebox.showerror("Initialization Error", 
                f"Failed to initialize {self.current_service.name} TTS engine: {str(e)}")
            raise
    
    def _activate_service(self, service: TTSService):
        """Activate a pre-initialized service"""
        self.current_service = service
        self.tts_engine = self.services[service]
        self.current_voice_manager = self.tts_engine.voice_manager
    
    def _setup_ui(self):
        self.style = Style("simplex") 
        self._setup_scrollable_container()
        
        available_services = {
            "Google": TTSService.GOOGLE,
            "ElevenLabs": TTSService.ELEVENLABS
        }
        self.service_switcher = ServiceSwitcher(
            self.scrollable_frame, 
            self, 
            available_services,
            command=self.switch_service
        )
        self.service_switcher.pack(fill=tk.X, padx=10, pady=5)

        self._setup_main_content(self.scrollable_frame) 
    
    def _setup_scrollable_container(self):
        """Make the main window scrollable with proper expansion"""
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        if platform.system() == "Linux":
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        else:
            self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _on_frame_configure(self, event=None):
        """Update scrollregion when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Resize the inner frame to match canvas width"""
        canvas_width = event.width
        self.canvas.itemconfig("frame", width=canvas_width)
        
    def _setup_main_content(self, parent):
        """Setup the main content area with original layout"""
        self.main_wrapper = ttk.Frame(parent)
        self.main_wrapper.pack(fill=tk.BOTH, expand=True, padx=20)
        
        content_frame = ttk.Frame(self.main_wrapper)
        content_frame.pack(fill=tk.BOTH, expand=True)

        self._setup_text_editor(content_frame)
        self._setup_top_controls(content_frame)
        self._setup_control_buttons(content_frame)
        self._setup_status_bar(content_frame)
    
    def _safe_set_cursor(self, cursor_type):
        """Ultimate cross-platform cursor handling"""
        if not self.winfo_exists():
            return
        
        cursor_aliases = {
            "watch": {
                "linux": ["wait", "left_ptr_watch", "progress", ""],
                "default": ["watch", ""]
            },
            "": {
                "linux": ["", "left_ptr", "arrow"],
                "default": ["", "arrow"]
            }
        }
        
        platform_key = "linux" if platform.system() == "Linux" else "default"
        cursor_options = cursor_aliases.get(cursor_type, {}).get(platform_key, [""])
        
        for cursor_name in cursor_options:
            try:
                self.tk.call("tk", "setCursor", self._w, cursor_name)
                self.update_idletasks()
                return
            except tk.TclError:
                continue
        
        try:
            self.config(cursor="")
        except:
            pass
        
    def switch_service(self, service: TTSService):
        """Thread-safe service switching with cursor guarantees"""
        if service == self.current_service:
            return
        
        def _execute_switch():
            try:
                if not self.winfo_exists():
                    return
                
                self._safe_set_cursor("watch")
                self.service_switcher.disable()
                self.update_status_meter(0, f"Switching to {service.name}...")
                self.update()
                
                if hasattr(self, 'service_controls_frame'):
                    for widget in self.service_controls_frame.winfo_children():
                        widget.destroy()
                
                try:
                    self._perform_service_switch(service)
                    self.after(0, self._finalize_successful_switch, service)
                except Exception as e:
                    self.after(0, self._handle_switch_failure, service, str(e))
                    
            except Exception as e:
                self._safe_set_cursor("")
                self.service_switcher.enable()
                self.update_status_meter(0, f"Failed to switch to {service.name}")
                messagebox.showerror("Error", f"Failed to switch to {service.name}: {str(e)}")

        self.after(0, _execute_switch)
    
    def _finalize_successful_switch(self, service):
        """Cleanup after successful switch"""
        if not self.winfo_exists():
            return
            
        try:
            self._safe_set_cursor("")
            self.service_switcher.enable()
            self.update_status_meter(100, f"Switched to {service.name}")
            self.after(1000, lambda: self.update_status_meter(0, "Ready"))
        except:
            pass

    def _handle_switch_failure(self, service, error):
        """Failure handler with window existence checks"""
        if not self.winfo_exists():
            return
            
        try:
            self._safe_set_cursor("")
            self.service_switcher.enable()
            self.update_status_meter(0, f"Failed to switch to {service.name}")
            
            if self.winfo_exists():
                try:
                    messagebox.showerror("Error", 
                        f"Failed to switch to {service.name}:\n{error}")
                except:
                    pass
        except:
            pass
    
    def _perform_service_switch(self, service):
        """Perform the actual service switch in background"""
        try:
            self._activate_service(service)
            self.after(0, self._update_ui_after_switch, service)
            
        except Exception as e:
            self.after(0, self._handle_switch_error, service, str(e))

    def _update_ui_after_switch(self, service):
        """Update UI after successful switch"""
        if hasattr(self, "top_controls_frame"):
            self._populate_top_controls(self.top_controls_frame)

        self.update_quota()
        self.is_playing = False
        self.is_paused = False
        self.current_audio_content = None
        
        if hasattr(self, 'download_button'):
            self.download_button.config(state=tk.DISABLED)
        
        self.service_switcher.enable()

        self.update_status_meter(100, f"Switched to {service.name}")
        messagebox.showinfo("Service Changed", f"Switched to {service.name} service")

    def _handle_switch_error(self, service, error):
        """Handle errors during service switch"""
        self.service_switcher.enable()
        self.update_status_meter(0, f"Failed to switch to {service.name}")
        messagebox.showerror("Error", f"Failed to switch to {service.name}: {error}")
        
    def _setup_text_editor(self, parent):
        """Create and pack the main text editor for input."""
        ttk.Label(parent, text="Enter text:").pack(anchor=tk.W)
        self.text_editor = TextEditor(parent)
        self.text_editor.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
    
    def _setup_top_controls(self, parent):
        """Create the top controls section."""  
        self.top_controls_frame = ttk.Frame(parent)
        self.top_controls_frame.pack(fill=tk.X, pady=(0, 10))
        self._populate_top_controls(self.top_controls_frame)
    
    def _populate_top_controls(self, frame): 
        for widget in frame.winfo_children():
            widget.destroy()
            
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)

        left_frame = ttk.Frame(frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Service-specific controls
        self.service_controls_frame = ttk.Frame(right_frame)
        self.service_controls_frame.pack(fill=tk.BOTH, expand=True)
        self._setup_service_controls()
        
        model = self.service_controls.get_selected_model()
        
        self._setup_language_voice_dropdowns(left_frame, model)
        self._setup_format_selector(left_frame) 

        if self.current_service == TTSService.ELEVENLABS:
            self.service_controls._setup_model_dropdown(left_frame, self.language_dropdown, self.voice_dropdown)
    
    def _setup_language_voice_dropdowns(self, parent, model=None):
        """Initialize and pack the language and voice selection dropdowns."""
        dropdown_frame = ttk.LabelFrame(parent, text="Language & Voice", padding=(10, 5))
        dropdown_frame.pack(fill=tk.X, pady=(0, 5))

        self.language_dropdown = LanguageControls(dropdown_frame, self.tts_engine)
        self.language_dropdown.pack(fill=tk.X, pady=(0, 5))

        self.voice_dropdown = VoiceControls(dropdown_frame, self.tts_engine)
        self.voice_dropdown.pack(fill=tk.X)

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
            
        if not hasattr(self, 'service_controls_cache'):
            self.service_controls_cache = {}
        
        if (self.current_service not in self.service_controls_cache or 
            not self.service_controls_cache[self.current_service].winfo_exists()):
            
            if self.current_service == TTSService.GOOGLE:
                self.service_controls_cache[self.current_service] = GoogleTTSLayout(self.service_controls_frame)
            elif self.current_service == TTSService.ELEVENLABS:
                self.service_controls_cache[self.current_service] = ElevenLabsLayout(self.service_controls_frame)

        
        self.service_controls_cache[self.current_service].pack(fill=tk.BOTH, expand=True)
        self.service_controls = self.service_controls_cache[self.current_service]
    
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
                messagebox.showerror("Generation Error", f"Voice doesn't support SSML - using plain text")
                self.update_status_meter(0, "Generation Error")
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