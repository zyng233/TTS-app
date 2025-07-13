import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class TextEditor(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
        
    def _setup_ui(self):
        self.text_widget = ScrolledText(self, wrap=tk.WORD, height=10)
        self.text_widget.pack(expand=True, fill=tk.BOTH)
    
    def get_text(self):
        """Get the current text content"""
        return self.text_widget.get("1.0", tk.END).strip()
    
    def set_text(self, text):
        """Set the text content"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)
    
    def clear(self):
        """Clear the editor"""
        self.set_text("")