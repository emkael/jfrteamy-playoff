#coding=utf-8

import os

import tkinter as tk
from tkinter import ttk
import tkFileDialog as tkfd

from .frames.team import *

from ..data import PlayoffData

class PlayoffTab(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.renderContent(self.frame)

    @property
    def title(self):
        pass

    def renderContent(self, container):
        pass

class MainSettingsTab(PlayoffTab):
    @property
    def title(self):
        return 'Główne ustawienia'

    def _chooseOutputPath(self):
        currentPath = self.outputPath.get()
        filename = tkfd.asksaveasfilename(
            initialdir=os.path.dirname(currentPath) if currentPath else '.',
            title='Wybierz plik wyjściowy',
            filetypes=(('HTML files', '*.html'),))
        if filename:
            if not filename.lower().endswith('.html'):
                filename = filename + '.html'
            self.outputPath.set(filename)

    def _updateRefreshFields(self):
        self.refreshInterval.configure(
            state=tk.NORMAL if self.refresh.get() else tk.DISABLED)

    def renderContent(self, container):
        (ttk.Label(container, text='Plik wynikowy:')).grid(
            row=0, column=0, sticky=tk.E, pady=2)
        outputPath = tk.Frame(container)
        outputPath.grid(row=0, column=1, sticky=tk.E+tk.W, pady=2)
        self.outputPath = tk.StringVar()
        (ttk.Entry(outputPath, width=60, textvariable=self.outputPath)).grid(
            row=0, column=0, sticky=tk.W+tk.E)
        (ttk.Button(
            outputPath,
            text='[]', command=self._chooseOutputPath)).grid(row=0, column=1)
        outputPath.columnconfigure(0, weight=1)

        (ttk.Separator(container, orient=tk.HORIZONTAL)).grid(
            row=1, column=0, columnspan=2, sticky=tk.E+tk.W, pady=2)

        (ttk.Label(container, text='Ustawienia strony')).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        (ttk.Label(container, text='Tytuł:')).grid(
            row=3, column=0, sticky=tk.E, pady=2)
        self.pageTitle = tk.StringVar()
        (tk.Entry(container, textvariable=self.pageTitle)).grid(
            row=3, column=1, sticky=tk.W+tk.E, pady=2)
        (ttk.Label(container, text='Logoh:')).grid(
            row=4, column=0, sticky=tk.E+tk.N, pady=2)
        self.pageLogoh = tk.Text(container, width=45, height=10)
        self.pageLogoh.grid(
            row=4, column=1,
            sticky=tk.W+tk.N+tk.E+tk.S, pady=2)

        (ttk.Label(container, text='Odświeżaj:')).grid(
            row=5, column=0, sticky=tk.E, pady=2)
        refreshPanel = tk.Frame(container)
        refreshPanel.grid(row=5, column=1, sticky=tk.W+tk.E, pady=2)
        self.refresh = tk.IntVar()
        (ttk.Checkbutton(
            refreshPanel,
            command=self._updateRefreshFields, variable=self.refresh)).grid(
                row=0, column=0)
        (ttk.Label(refreshPanel, text='co:')).grid(row=0, column=1)
        self.refreshInterval = tk.Spinbox(
            refreshPanel, from_=30, to=3600, width=5, justify=tk.RIGHT)
        self.refreshInterval.grid(row=0, column=2)
        (ttk.Label(refreshPanel, text='sekund')).grid(row=0, column=3)
        self._updateRefreshFields()

        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

class TeamsTab(PlayoffTab):
    @property
    def title(self):
        return 'Uczestnicy'

    def renderContent(self, container):
        leftFrame = tk.Frame(container)
        leftFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.settingsFrame = TeamSettingsFrame(
            leftFrame, vertical=True, padx=5, pady=5)
        self.settingsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        (ttk.Separator(
            leftFrame, orient=tk.HORIZONTAL)).pack(
                side=tk.TOP, fill=tk.X)
        self.aliasFrame = TeamAliasFrame(leftFrame, vertical=True)
        self.aliasFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.previewFrame = TeamPreviewFrame(container, vertical=True)
        self.previewFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._teamList = []
        self._teamListFetcher = None

        self.winfo_toplevel().bind(
            '<<TeamSettingsChanged>>', self.onTeamSettingsChange, add='+')

    def onTeamSettingsChange(self, event):
        if self._teamListFetcher is not None:
            self.after_cancel(self._teamListFetcher)
        self._teamListFetcher = self.after(500, self._fetchTeamList)

    def _fetchTeamList(self):
        config = self.collectConfig()
        dbConfig = self.winfo_toplevel().getDbConfig()
        if dbConfig is not None:
            config['database'] = dbConfig
        data = PlayoffData()
        self._teamList = data.fetch_team_list(config['teams'], dbConfig)
        self.winfo_toplevel().event_generate(
            '<<TeamListChanged>>', when='tail')

    def getTeams(self):
        return self._teamList

    def collectConfig(self):
        config = {
            'teams': self.settingsFrame.getConfig(),
            'team_aliases': self.aliasFrame.getConfig()
        }
        tieConfig = self.previewFrame.getTieConfig()
        if tieConfig is not None and isinstance(config['teams'], dict):
            config['teams']['ties'] = tieConfig
        return config

class MatchesTab(PlayoffTab):
    @property
    def title(self):
        return 'Mecze'

class SwissesTab(PlayoffTab):
    @property
    def title(self):
        return 'Swissy'

class NetworkTab(PlayoffTab):
    @property
    def title(self):
        return 'Sieć'

    def getDB(self):
        return None

class VisualTab(PlayoffTab):
    @property
    def title(self):
        return 'Wygląd'

class StyleTab(PlayoffTab):
    @property
    def title(self):
        return 'Style'

class TranslationsTab(PlayoffTab):
    @property
    def title(self):
        return 'Tłumaczenia'

__all__ = ['MainSettingsTab', 'TeamsTab', 'MatchesTab', 'SwissesTab',
           'NetworkTab', 'VisualTab', 'StyleTab', 'TranslationsTab']
