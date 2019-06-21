#coding=utf-8

import os

import tkinter as tk
from tkinter import ttk
import tkFileDialog as tkfd
import tkMessageBox as tkmb

from .frames import getIntVal
from .frames.match import *
from .frames.network import *
from .frames.team import *
from .frames.translations import *
from .frames.visual import *

from ..data import PlayoffData
from ..db import PlayoffDB

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
            text='wybierz...', command=self._chooseOutputPath)).grid(
                row=0, column=1)
        outputPath.columnconfigure(0, weight=1)

        (ttk.Separator(container, orient=tk.HORIZONTAL)).grid(
            row=1, column=0, columnspan=2, sticky=tk.E+tk.W, pady=2)

        pageSettings = ttk.LabelFrame(
            container, text='Ustawienia strony')
        pageSettings.grid(
            row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)

        (ttk.Label(pageSettings, text='Tytuł:')).grid(
            row=0, column=0, sticky=tk.E, pady=2)
        self.pageTitle = tk.StringVar()
        (tk.Entry(pageSettings, textvariable=self.pageTitle)).grid(
            row=0, column=1, sticky=tk.W+tk.E, pady=2)
        (ttk.Label(pageSettings, text='Logoh:')).grid(
            row=1, column=0, sticky=tk.E+tk.N, pady=2)
        self.pageLogoh = tk.Text(pageSettings, width=45, height=10)
        self.pageLogoh.grid(
            row=1, column=1,
            sticky=tk.W+tk.N+tk.E+tk.S, pady=2)

        (ttk.Label(pageSettings, text='Odświeżaj:')).grid(
            row=2, column=0, sticky=tk.E, pady=2)
        refreshPanel = tk.Frame(pageSettings)
        refreshPanel.grid(row=2, column=1, sticky=tk.W+tk.E, pady=2)
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
        db = None
        try:
            db = PlayoffDB(dbConfig)
        except Exception:
            pass
        self._teamList = data.fetch_team_list(config['teams'], db)
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

    def renderContent(self, container):
        self.phase = MatchPhaseFrame(container, vertical=True)
        self.phase.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def getMatches(self):
        return [w for w in self.phase.matches.widgets
                if isinstance(w, MatchSettingsFrame)]

class SwissesTab(PlayoffTab):
    @property
    def title(self):
        return 'Swissy'

    def renderContent(self, container):
        self.swisses = SwissesFrame(container, vertical=True)
        self.swisses.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class NetworkTab(PlayoffTab):
    @property
    def title(self):
        return 'Sieć'

    def _onDBSettingsChange(self, event):
        if self.dbFetchTimer is not None:
            self.after_cancel(self.dbFetchTimer)
        self.dbFetchTimer = self.after(1500, self._fetchDBList)

    def _fetchDBList(self):
        self._dbList = []
        try:
            db = PlayoffDB(self.getDB())
            for row in db.fetch_all(
                    'information_schema',
                    'SELECT TABLE_SCHEMA FROM information_schema.COLUMNS WHERE TABLE_NAME = "admin" AND COLUMN_NAME = "teamcnt" ORDER BY TABLE_SCHEMA;', {}):
                self._dbList.append(row[0])
        except Exception as e:
            pass
        self.winfo_toplevel().event_generate('<<DBListChanged>>', when='tail')

    def getDBList(self):
        return self._dbList

    def getDB(self):
        return self.mysqlFrame.getConfig()

    def renderContent(self, container):
        self.mysqlFrame = MySQLConfigurationFrame(container)
        self.mysqlFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        (ttk.Separator(container, orient=tk.HORIZONTAL)).pack(
            side=tk.TOP, fill=tk.X)

        self.goniecFrame = GoniecConfigurationFrame(container)
        self.goniecFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        (ttk.Separator(container, orient=tk.HORIZONTAL)).pack(
            side=tk.TOP, fill=tk.X)

        self.remoteFrame = RemoteConfigurationFrame(container, vertical=True)
        self.remoteFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._dbList = []
        self.dbFetchTimer = None
        self.winfo_toplevel().bind(
            '<<DBSettingsChanged>>', self._onDBSettingsChange, add='+')

class VisualTab(PlayoffTab):
    @property
    def title(self):
        return 'Wygląd'

    def renderContent(self, container):
        self.settingsFrame = VisualSettingsFrame(container)
        self.settingsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.positionFrame = BoxPositionsFrame(container, vertical=True)
        self.positionFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class StyleTab(PlayoffTab):
    @property
    def title(self):
        return 'Style'

    def renderContent(self, container):
        self.linesFrame = LineStylesFrame(container)
        self.linesFrame.pack(side=tk.TOP, anchor=tk.W)

        (ttk.Separator(container, orient=tk.HORIZONTAL)).pack(
            side=tk.TOP, fill=tk.X)

        self.positionStylesFrame = PositionStylesFrame(
            container, vertical=True)
        self.positionStylesFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class TranslationsTab(PlayoffTab):
    @property
    def title(self):
        return 'Tłumaczenia'

    def renderContent(self, container):
        self.translationsFrame = TranslationConfigurationFrame(
            container, vertical=True)
        self.translationsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

__all__ = ['MainSettingsTab', 'TeamsTab', 'MatchesTab', 'SwissesTab',
           'NetworkTab', 'VisualTab', 'StyleTab', 'TranslationsTab']
