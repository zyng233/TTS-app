import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap.widgets import Scale

class ElevenLabsLayout(ttk.Frame):
    def __init__(self, parent_frame: ttk.Frame):
        super().__init__(parent_frame)
        self.models = [
            ("Multilingual v2", "eleven_multilingual_v2"),
            ("Turbo v2", "eleven_turbo_v2")
        ]
        self.model_mapping = {display: value for display, value in self.models}
        self.model_var = tk.StringVar(value="Multilingual v2")
        self._setup_voice_controls(parent_frame)
        self._setup_bindings()
        
    def _setup_voice_controls(self, parent):
        """Voice controls specific to ElevenLabs"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        voice_control = ttk.LabelFrame(container, text="Voice Controls", padding=(10, 5))
        voice_control.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Stability
        ttk.Label(voice_control, text="Stability:").pack(anchor=tk.W)
        self._add_slider_with_entry(
            voice_control, "stability", 0.0, 1.0, 0.5, "success"
        )
        
        # Similarity boost
        ttk.Label(voice_control, text="Similarity Boost:").pack(anchor=tk.W)
        self._add_slider_with_entry(
            voice_control, "boost", 0.0, 1.0, 0.75, "warning"
        )
        
        # Speed
        ttk.Label(voice_control, text="Speed:").pack(anchor=tk.W)
        self._add_slider_with_entry(
            voice_control, "speed", 0.7, 1.2, 1.0, "info"
        )
        
        # Style
        ttk.Label(voice_control, text="Style:").pack(anchor=tk.W)
        self._add_slider_with_entry(
            voice_control, "style", 0.0, 1.0, 0.0, "secondary"
        )
        
        # Speaker boost
        self.speaker_boost_var = tk.BooleanVar(value=False)
        speaker_boost_checkbox = ttk.Checkbutton(
            voice_control, text="Enable Speaker Boost", variable=self.speaker_boost_var
        )
        speaker_boost_checkbox.pack(anchor=tk.W, pady=(5, 0))

    def _add_slider_with_entry(self, parent, name, from_, to, value, style):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 5))

        slider = Scale(
            frame, from_=from_, to=to, value=value,
            orient=tk.HORIZONTAL, length=100, bootstyle=style
        )
        slider.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        var = tk.StringVar(value=f"{value:.2f}")
        entry = ttk.Entry(frame, textvariable=var, width=5)
        entry.pack(side=tk.LEFT)

        setattr(self, f"{name}_slider", slider)
        setattr(self, f"{name}_var", var)
        
    def get_voice_parameters(self):
        """Return the voice parameters for ElevenLabs"""
        try:
            model = self.model_mapping.get(self.model_var.get())
            stability = float(self.stability_var.get())
            similarity_boost = float(self.boost_var.get())
            speed = float(self.speed_var.get())
            style = float(self.style_var.get())
            speaker_boost = self.speaker_boost_var.get()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numeric values for stability and similarity boost.")
            return None

        if not (0.0 <= stability <= 1.0):
            messagebox.showwarning("Invalid Stability", "Stability must be between 0.0 and 1.0.")
            return None

        if not (0.0 <= similarity_boost <= 1.0):
            messagebox.showwarning("Invalid Similarity Boost", "Similarity Boost must be between 0.0 and 1.0.")
            return None
        
        if not (0.7 <= speed <= 1.2):
            messagebox.showwarning("Invalid Speed", "Speed must be between 0.7 and 1.2.")
            return None
        
        if not (0.0 <= style <= 1.0):
            messagebox.showwarning("Invalid Style Exaggeration", "Style Exaggeration must be between 0.0 and 1.0.")
            return None

        return {
            "model": model,
            "stability": stability,
            "similarity_boost": similarity_boost,
            "speed": speed,
            "style": style,
            "use_speaker_boost": speaker_boost
        }
            
    def _setup_bindings(self):
        """Bind slider events to update voice entry fields.""" 
        for name in ["stability", "boost", "speed", "style"]:
            slider = getattr(self, f"{name}_slider")
            var = getattr(self, f"{name}_var")

            def update_entry(event=None, name=name):
                getattr(self, f"{name}_var").set(f"{getattr(self, f'{name}_slider').get():.2f}")
            slider.bind("<B1-Motion>", update_entry)
            slider.bind("<ButtonRelease-1>", update_entry)

            def update_slider(*args, name=name):
                try:
                    val = float(getattr(self, f"{name}_var").get())
                    if 0.0 <= val <= 2.0:
                        getattr(self, f"{name}_slider").set(val)
                except ValueError:
                    pass
            var.trace_add("write", lambda *args, name=name: update_slider())
            
    def _setup_model_dropdown(self, parent, language_dropdown, voice_dropdown):
        self.language_dropdown = language_dropdown  
        self.voice_dropdown = voice_dropdown
        if hasattr(self, 'model_frame') and self.model_frame.winfo_exists():
            self.model_frame.destroy()
        self.model_frame = ttk.LabelFrame(parent, text="Model", padding=(5, 2))
        self.model_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.model_dropdown = ttk.Combobox(
            self.model_frame,
            textvariable=self.model_var,
            state="readonly",
            values=[m[0] for m in self.models],
            width=20
        )
        self.model_dropdown.pack(fill=tk.X, padx=5, pady=2)
        self.model_dropdown.bind("<<ComboboxSelected>>", self._on_model_changed)
        
    def _on_model_changed(self, event=None):
        """Handle model selection change"""
        selected_model_key = self.model_mapping.get(self.model_var.get())
        if not selected_model_key:
            return

        try:
            # Update language dropdown
            if hasattr(self, 'language_dropdown') and self.language_dropdown:
                self.language_dropdown.load_languages(model=selected_model_key)

        except Exception as e:
            messagebox.showerror("Model Change Error", f"Failed to update UI after model change:\n{e}")

    def get_selected_model(self):
        """Get the currently selected model value"""
        return self.model_mapping.get(self.model_var.get())