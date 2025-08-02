import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable
from core.tts.factory import TTSService

class ServiceSwitcher(ttk.Frame):
    def __init__(self, parent, app, services: Dict[str, TTSService], command: Optional[Callable] = None):
        super().__init__(parent)
        self.app = app
        self.services = services
        self.command = command
        self._setup_ui()

    def _setup_ui(self):
        ttk.Label(self, text="TTS Service:").pack(side=tk.LEFT, padx=(10, 5))
        
        self.service_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.service_var,
            values=list(self.services.keys()),
            state="readonly"
        )
        self.dropdown.pack(side=tk.LEFT)
        self.dropdown.bind("<<ComboboxSelected>>", self._on_service_changed)
        
        if self.services:
            first_service = next(iter(self.services.keys()))
            self.service_var.set(first_service)

    def _on_service_changed(self, event):
        selected_name = self.service_var.get()
        if selected_name in self.services:
            service = self.services[selected_name]
            if self.command:
                self.command(service)

    def set_service(self, service: TTSService):
        """Set the current service in the dropdown"""
        for name, svc in self.services.items():
            if svc == service:
                self.service_var.set(name)
                break
            
    def disable(self):
        """Disable the service switcher"""
        self.dropdown.config(state='disabled')

    def enable(self):
        """Enable the service switcher"""
        self.dropdown.config(state='readonly')