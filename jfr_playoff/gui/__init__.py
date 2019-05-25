import tkinter as tk
from tkinter import ttk

from .tabs import *

class PlayoffGUI(object):
    def __init__(self):
        self.root = tk.Tk()

    def run(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        for tab in tabs.__all__:
            tabObj = globals()[tab](self.notebook)
            self.notebook.add(tabObj, text=tabObj.title)
        self.root.mainloop()
