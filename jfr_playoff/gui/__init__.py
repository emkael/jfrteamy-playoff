import json, os, sys

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
        self.newFileIndex = 0
        self._title = tk.StringVar()
        self._title.trace('w', self._setTitle)
        self._dirty = False

    def run(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        for tab in tabs.__all__:
            self.tabs[tab] = globals()[tab](self.notebook)
            self.notebook.add(self.tabs[tab], text=self.tabs[tab].title)
        if len(sys.argv) > 1:
            self.openFile(sys.argv[1])
        else:
            self.newFile()
        self.mainloop()

    def _setValues(self, config):
        for tab in self.tabs.values():
            tab.setValues(config)

    def _resetValues(self):
        self._setValues({})

    def newFile(self):
        self.newFileIndex += 1
        self._title.set('Nowa drabinka %d' % (self.newFileIndex))
        self._resetValues()

    def _setTitle(self, *args):
        self.title('%s - %s%s' % (
            'TeamyPlayOff',
            self._title.get(),
            '* ' if self._dirty else ''
        ))

    def openFile(self, filepath):
        self._title.set(os.path.basename(filepath))
        self._setValues(json.load(open(filepath)))

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
