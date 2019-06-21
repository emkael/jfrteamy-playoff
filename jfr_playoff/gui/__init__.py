import tkinter as tk
from tkinter import ttk

from .tabs import *

class PlayoffGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        ttk.Style().configure('TLabelframe.Label', foreground='black')
        ttk.Style().configure('TLabelframe', padding=5)
        self.geometry('920x640')
        self.tabs = {}

    def run(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        for tab in tabs.__all__:
            self.tabs[tab] = globals()[tab](self.notebook)
            self.notebook.add(self.tabs[tab], text=self.tabs[tab].title)
        self.mainloop()

    def getDbConfig(self):
        return self.tabs['NetworkTab'].getDB()

    def getTeams(self):
        return self.tabs['TeamsTab'].getTeams()

    def getDBs(self):
        return self.tabs['NetworkTab'].getDBList()

    def getMatches(self):
        return self.tabs['MatchesTab'].getMatches()

    def getNewMatchID(self, match):
        matches = self.tabs['MatchesTab'].getMatches()
        if len(matches) > 0:
            return max([m.getMatchID() for m in matches]) + 1
        return 1
