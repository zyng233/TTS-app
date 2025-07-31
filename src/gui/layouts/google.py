import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap.widgets import Scale
from ..components.audio_controls import AudioControls

class GoogleTTSLayout(ttk.Frame):
    def __init__(self, parent_frame: ttk.Frame):
        super().__init__(parent_frame)
        self._setup_voice_controls(parent_frame)
        self._setup_audio_profile(parent_frame)
        self._setup_ssml_toggle(parent_frame)
        self._setup_bindings()
        
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
        """Audio Profile dropdown"""
        audio_profile_frame = ttk.LabelFrame(parent, text="Audio Profile", padding=(10, 5))
        audio_profile_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.audio_profile_dropdown = AudioControls(audio_profile_frame)
        self.audio_profile_dropdown.pack(fill=tk.X)
        
    def _setup_ssml_toggle(self, parent):
        """SSML toggle for Google"""
        ssml_frame = ttk.Frame(parent)
        ssml_frame.pack(fill=tk.X, pady=(10, 0))

        self.ssml_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            ssml_frame, 
            text="SSML", 
            variable=self.ssml_var
        ).pack(side=tk.RIGHT, anchor=tk.E)
 
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
        
        def on_rate_var_change(*args):
            try:
                val = float(self.rate_var.get())
                if 0.25 <= val <= 4.0:
                    self.rate_slider.set(val)
            except ValueError:
                pass

        def on_pitch_var_change(*args):
            try:
                val = float(self.pitch_var.get())
                if -20.0 <= val <= 20.0:
                    self.pitch_slider.set(val)
            except ValueError:
                pass

        self.rate_var.trace_add("write", lambda *args: on_rate_var_change())
        self.pitch_var.trace_add("write", lambda *args: on_pitch_var_change())
        
    def get_voice_parameters(self):
        """Return the voice parameters for Google TTS"""
        try:
            speaking_rate = float(self.rate_var.get())
            pitch = float(self.pitch_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numeric values for speaking rate and pitch.")
            return None
        
        if not (0.25 <= speaking_rate <= 4.0):
            messagebox.showwarning(
                "Invalid Rate",
                "Speaking rate must be between 0.25 and 4.0.\n\nNote: Some voices only support rate between 0.25 and 2.0."
                )
            return None
        
        if not (-20.0 <= pitch <= 20.0):
            messagebox.showwarning(
                "Invalid Pitch", 
                "Pitch must be between -20 and 20.\n\nNote: Some voices do not support custom pitch values."
                )
            return None
        
        effects_profile_id = None
        if hasattr(self, 'audio_profile_dropdown'):
            selected_profile = self.audio_profile_dropdown.get_selected_profile()
            if selected_profile:
                effects_profile_id = [selected_profile]
                
        return {
            "speaking_rate": speaking_rate,
            "pitch": pitch,
            "is_ssml": self.ssml_var.get(),
            "effects_profile_id": effects_profile_id
        }
        
    def get_selected_model(self):
        return None