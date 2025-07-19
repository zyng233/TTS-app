import tkinter as tk
from tkinter import ttk

PROFILE_MAP = {
    "Mobile Phone (Telephony)": "telephony-class-application",
    "Mobile Handset": "handset-class-device",
    "Headphones": "headphone-class-device",
    "Small Bluetooth Speaker": "small-bluetooth-speaker-class-device",
    "Medium Bluetooth Speaker": "medium-bluetooth-speaker-class-device",
    "Large Home Entertainment System": "large-home-entertainment-class-device",
    "Car Audio System": "large-automotive-class-device"
}

DISPLAY_NAMES = list(PROFILE_MAP.keys())

class AudioProfileDropdown(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Simulate a playback device:").pack(anchor=tk.W)

        self.selected_display = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.selected_display,
            values=DISPLAY_NAMES,
            state="readonly"
        )
        self.dropdown.pack(fill=tk.X)
        self.dropdown.set(DISPLAY_NAMES[0])

    def get_selected_profile(self):
        """Returns the internal effects profile ID"""
        return PROFILE_MAP.get(self.selected_display.get(), None)

    def set_selected_profile(self, internal_name):
        """Set the dropdown based on internal ID"""
        for display, internal in PROFILE_MAP.items():
            if internal == internal_name:
                self.dropdown.set(display)
                break
