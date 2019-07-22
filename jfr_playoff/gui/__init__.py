#coding=utf-8

import codecs, copy, json, os, sys
from collections import OrderedDict

import tkinter as tk
from tkinter import ttk
import tkFileDialog as tkfd
import tkMessageBox as tkmb

from .tabs import *
from .icons import GuiImage

class PlayoffGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        ttk.Style().configure('TLabelframe.Label', foreground='black')
        ttk.Style().configure('TLabelframe', padding=5)
        self.geometry('920x640')
        self.tabs = {}
        self._buildMenu()
        self.newFileIndex = 0
        self._title = tk.StringVar()
        self._title.trace('w', self._setTitle)
        self._dirty = tk.BooleanVar()
        self._dirty.trace('w', self._setTitle)
        self._dirty.trace('w', self._setMenuButtons)
        self._filepath = None

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
        self.bind('<<ValueChanged>>', self._onFileChange, add='+')
        self.mainloop()

    def _onFileChange(self, *args):
        self._dirty.set(True)

    def _checkSave(self):
        if self._dirty.get():
            if tkmb.askyesno(
                    'Zapisz zmiany',
                    'Czy chcesz zapisać zmiany w bieżącej drabince?'):
                self.onSave()

    def _setTitle(self, *args):
        self.title('%s - %s%s' % (
            'TeamyPlayOff',
            self._title.get(),
            ' *' if self._dirty.get() else ''
        ))

    def _setMenuButtons(self, *args):
        self.menuButtons['save'].configure(
            state=tk.NORMAL if self._dirty.get() else tk.DISABLED)

    def _setValues(self, config):
        for tab in self.tabs.values():
            tab.setValues(config)

    def _resetValues(self):
        self._setValues({})

    def _buildMenu(self):
        menu = tk.Frame(self)
        menu.pack(side=tk.TOP, fill=tk.X)
        self.menuButtons = {}
        for icon, command in [('new', self.onNewFile),
                              ('open', self.onFileOpen),
                              ('save', self.onSave),
                              ('saveas', self.onSaveAs)]:
            self.menuButtons[icon] = ttk.Button(
                menu, image=GuiImage.get_icon(icon), command=command)
            self.menuButtons[icon].pack(side=tk.LEFT)

    def onNewFile(self):
        self._checkSave()
        self.newFile()

    def onFileOpen(self):
        self._checkSave()
        filename = tkfd.askopenfilename(
            title='Wybierz plik drabniki',
            filetypes=(('JFR Teamy Play-Off files', '*.jtpo'),
                       ('JSON files', '*.json'),))
        if filename:
            self.openFile(filename)

    def onSave(self):
        if self._filepath is not None:
            self.saveFile(self._filepath)
        else:
            self.onSaveAs()

    def onSaveAs(self):
        filename = tkfd.asksaveasfilename(
            title='Wybierz plik drabniki',
            filetypes=(('JFR Teamy Play-Off files', '*.jtpo'),
                       ('JSON files', '*.json'),))
        if filename:
            if not filename.lower().endswith('.jtpo'):
                filename = filename + '.jtpo'
            self.saveFile(filename)

    def newFile(self):
        self._filepath = None
        self.newFileIndex += 1
        self._title.set('Nowa drabinka %d' % (self.newFileIndex))
        self._resetValues()
        self.after(0, self._dirty.set, False)

    def openFile(self, filepath):
        self._filepath = filepath
        self._title.set(os.path.basename(filepath))
        self._setValues(json.load(open(filepath)))
        self.after(0, self._dirty.set, False)

    def saveFile(self, filepath):
        json.dump(
            self.getConfig(), codecs.open(filepath, 'w', encoding='utf8'),
            indent=4, ensure_ascii=False)
        self._filepath = filepath
        self._title.set(os.path.basename(filepath))
        self.after(0, self._dirty.set, False)

    def getConfig(self):
        config = OrderedDict()
        for tab in self.tabs.values():
            tabConfig = tab.getConfig()
            if tabConfig is not None:
                config = self._mergeConfig(config, tab.getConfig())
        return config

    def _mergeConfig(self, base, update):
        result = copy.copy(base)
        for key, value in update.iteritems():
            if key in result:
                if isinstance(result[key], dict):
                    result[key] = self._mergeConfig(
                        result[key], update[key])
                else:
                    result[key] = update[key]
            else:
                result[key] = value
        return result

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
