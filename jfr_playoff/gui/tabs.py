#coding=utf-8

import os
from collections import OrderedDict

import tkinter as tk
from tkinter import ttk
import tkFileDialog as tkfd
import tkMessageBox as tkmb

from .frames import TraceableText, NumericSpinbox
from .frames.match import *
from .frames.network import *
from .frames.team import *
from .frames.translations import *
from .frames.visual import *
from .variables import NotifyStringVar, NotifyNumericVar, NotifyBoolVar

from ..data import PlayoffData
from ..db import PlayoffDB

class PlayoffTab(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.initData()
        self.renderContent(self.frame)

    @property
    def title(self):
        pass

    def initData(self):
        pass

    def renderContent(self, container):
        pass

    def setValues(self, config):
        pass

    def getConfig(self):
        pass

class MainSettingsTab(PlayoffTab):
    DEFAULT_INTERVAL = 60

    @property
    def title(self):
        return 'Główne ustawienia'

    def initData(self):
        self.outputPath = NotifyStringVar()
        self.pageTitle = NotifyStringVar()
        self.pageLogoh = NotifyStringVar()
        self.refresh = NotifyBoolVar()
        self.refresh.trace('w', self._updateRefreshFields)
        self.refreshInterval = NotifyNumericVar()

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

    def _updateRefreshFields(self, *args):
        self.intervalField.configure(
            state=tk.NORMAL if self.refresh.get() else tk.DISABLED)

    def setValues(self, config):
        self.outputPath.set(config['output'] if 'output' in config else '')
        if 'page' in config:
            self.pageTitle.set(
                config['page']['title'] if 'title' in config['page'] else '')
            self.pageLogoh.set(
                config['page']['logoh'] if 'logoh' in config['page'] else '')
            try:
                interval = int(config['page']['refresh'])
                if interval > 0:
                    self.refresh.set(1)
                    self.refreshInterval.set(interval)
                else:
                    self.refresh.set(0)
                    self.refreshInterval.set(self.DEFAULT_INTERVAL)
            except:
                self.refresh.set(0)
                self.refreshInterval.set(self.DEFAULT_INTERVAL)
        else:
            self.pageTitle.set('')
            self.pageLogoh.set('')
            self.refresh.set(0)
            self.refreshInterval.set(self.DEFAULT_INTERVAL)

    def renderContent(self, container):
        (ttk.Label(container, text='Plik wynikowy:')).grid(
            row=0, column=0, sticky=tk.E, pady=2)
        outputPath = tk.Frame(container)
        outputPath.grid(row=0, column=1, sticky=tk.E+tk.W, pady=2)
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

        pageSettings.columnconfigure(1, weight=1)

        (ttk.Label(pageSettings, text='Tytuł:')).grid(
            row=0, column=0, sticky=tk.E, pady=2)
        (tk.Entry(pageSettings, textvariable=self.pageTitle)).grid(
            row=0, column=1, sticky=tk.W+tk.E, pady=2)
        (ttk.Label(pageSettings, text='Logoh:')).grid(
            row=1, column=0, sticky=tk.E+tk.N, pady=2)
        (TraceableText(pageSettings, width=45, height=10,
                       variable=self.pageLogoh)).grid(
                           row=1, column=1,
                           sticky=tk.W+tk.N+tk.E+tk.S, pady=2)

        (ttk.Label(pageSettings, text='Odświeżaj:')).grid(
            row=2, column=0, sticky=tk.E, pady=2)
        refreshPanel = tk.Frame(pageSettings)
        refreshPanel.grid(row=2, column=1, sticky=tk.W+tk.E, pady=2)
        (ttk.Checkbutton(
            refreshPanel,
            command=self._updateRefreshFields, variable=self.refresh)).grid(
                row=0, column=0)
        (ttk.Label(refreshPanel, text='co:')).grid(row=0, column=1)
        self.intervalField = NumericSpinbox(
            refreshPanel, from_=30, to=3600, width=5, justify=tk.RIGHT,
            textvariable=self.refreshInterval)
        self.intervalField.grid(row=0, column=2)
        (ttk.Label(refreshPanel, text='sekund')).grid(row=0, column=3)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

    def getConfig(self):
        return OrderedDict({
            'output': self.outputPath.get(),
            'page': OrderedDict({
                'title': self.pageTitle.get(),
                'logoh': self.pageLogoh.get(),
                'refresh': self.refreshInterval.get() \
                if self.refresh.get() > 0 else 0
            })
        })

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

        self.aliasFrame = TeamAliasFrame(
            leftFrame, vertical=True, padx=5, pady=5)
        self.aliasFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.previewFrame = TeamPreviewFrame(
            container, vertical=True, padx=5, pady=5)
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
        config = OrderedDict({
            'teams': self.settingsFrame.getConfig(),
            'team_aliases': self.aliasFrame.getConfig()
        })
        tieConfig = self.previewFrame.getTieConfig()
        if tieConfig is not None and isinstance(config['teams'], dict):
            config['teams']['ties'] = tieConfig
        orderConfig = self.previewFrame.getOrderConfig()
        if orderConfig:
            config['custom_final_order'] = orderConfig
        return config

    def setValues(self, config):
        self.settingsFrame.setValues(
            config['teams'] if 'teams' in config else [])
        self.aliasFrame.setValues(
            config['team_aliases'] if 'team_aliases' in config else {})
        self.previewFrame.setTieConfig(
            config['teams']['ties']
            if 'teams' in config and 'ties' in config['teams'] else [])
        self.previewFrame.setOrderConfig(
            config.get('custom_final_order', []))

    def getConfig(self):
        return self.collectConfig()

class MatchesTab(PlayoffTab):
    @property
    def title(self):
        return 'Mecze'

    def addPhase(self):
        phase = MatchPhaseFrame(
            self.phaseFrame, vertical=True, padx=10, pady=10)
        newPhase = max(self.phases.keys()) + 1 if len(self.phases) else 1
        self.phaseFrame.add(phase, text='Faza #%d' % (newPhase))
        self.phases[newPhase] = phase
        self.winfo_toplevel().event_generate(
            '<<MatchListChanged>>', when='tail')
        return newPhase

    def removePhase(self, phase=None):
        selected = self.phaseFrame.select() if phase is None \
            else self.phases[phase]
        if selected:
            self.phaseFrame.forget(selected)
            key_to_delete = None
            for key, tab in self.phases.iteritems():
                if str(selected) == str(tab):
                    key_to_delete = key
                    break
            if key_to_delete:
                self.phases.pop(key_to_delete)
        self.winfo_toplevel().event_generate(
            '<<MatchListChanged>>', when='tail')

    def _renameTabs(self, *args):
        for idx, tab in self.phases.iteritems():
            title = tab.name.get().strip()
            self.phaseFrame.tab(
                tab, text=title if len(title) else 'Faza #%d' % (idx))

    def renderContent(self, container):
        container.columnconfigure(1, weight=1)
        container.rowconfigure(2, weight=1)
        (ttk.Label(container, text='Fazy rozgrywek:')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W)
        (ttk.Button(
            container, text='+', command=self.addPhase, width=5)).grid(
                row=1, column=0, sticky=tk.W)
        (ttk.Button(
            container, text='-', command=self.removePhase, width=5)).grid(
                row=1, column=1, sticky=tk.W)
        self.phases = {}
        self.phaseFrame = ttk.Notebook(container)
        self.phaseFrame.grid(
            row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)

        self.winfo_toplevel().bind(
            '<<PhaseRenamed>>', self._renameTabs, add='+')

    def getMatches(self):
        matches = []
        for phase in self.phases.values():
            matches += [w for w in phase.matches.widgets
                        if isinstance(w, MatchSettingsFrame)]
        return matches

    def setValues(self, config):
        phases = config['phases'] if 'phases' in config else []
        for idx in self.phases.keys():
            self.removePhase(idx)
        for phase in phases:
            newPhase = self.addPhase()
            self.phases[newPhase].setValues(phase)
        for phase in self.phases.values():
            for match in phase.matches.widgets:
                if isinstance(match, MatchSettingsFrame) \
                   and match.getMatchID == 0:
                    match.matchID.set(
                        self.winfo_toplevel().getNewMatchID(match))

    def getConfig(self):
        return OrderedDict({
            'phases': [phase.getConfig() for phase in self.phases.values()]
        })

class SwissesTab(PlayoffTab):
    @property
    def title(self):
        return 'Swissy'

    def renderContent(self, container):
        self.swisses = SwissesFrame(container, vertical=True)
        self.swisses.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def setValues(self, config):
        self.swisses.setValues(config['swiss'] if 'swiss' in config else [])

    def getConfig(self):
        swisses = self.swisses.getValues()
        if len(swisses):
            return OrderedDict({
                'swiss': swisses
            })
        else:
            return None

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
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        self.mysqlFrame = MySQLConfigurationFrame(container)
        self.mysqlFrame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        self.goniecFrame = GoniecConfigurationFrame(container)
        self.goniecFrame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

        self.remoteFrame = RemoteConfigurationFrame(container, vertical=True)
        self.remoteFrame.grid(
            row=1, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)

        self._dbList = []
        self.dbFetchTimer = None
        self.winfo_toplevel().bind(
            '<<DBSettingsChanged>>', self._onDBSettingsChange, add='+')

    def setValues(self, config):
        self.mysqlFrame.setValues(
            config['database'] if 'database' in config else {})
        self.goniecFrame.setValues(
            config['goniec'] if 'goniec' in config else {})
        self.remoteFrame.setValues(
            config['remotes'] if 'remotes' in config else [])

    def getConfig(self):
        config = OrderedDict()
        mysql = self.getDB()
        if mysql is not None:
            config['database'] = mysql
        config['goniec'] = self.goniecFrame.getValues()
        remotes = self.remoteFrame.getValues()
        if len(remotes):
            config['remotes'] = remotes
        return config

class VisualTab(PlayoffTab):
    @property
    def title(self):
        return 'Wygląd'

    def renderContent(self, container):
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        self.settingsFrame = VisualSettingsFrame(container)
        self.settingsFrame.grid(row=0, column=0, sticky=tk.S+tk.N+tk.E+tk.W)

        self.positionFrame = BoxPositionsFrame(container, vertical=True)
        self.positionFrame.grid(row=1, column=0, sticky=tk.S+tk.N+tk.E+tk.W)

    def setValues(self, config):
        if 'page' in config:
            self.settingsFrame.setValues(config['page'])
        else:
            self.settingsFrame.setValues({})
        if 'canvas' in config and 'box_positioning' in config['canvas']:
            self.positionFrame.setValues(config['canvas']['box_positioning'])
        else:
            self.positionFrame.setValues({})

    def getConfig(self):
        config = OrderedDict({
            'page': self.settingsFrame.getValues()
        })
        boxConfig = self.positionFrame.getValues()
        if boxConfig:
            config['canvas'] = OrderedDict()
            config['canvas']['box_positioning'] = boxConfig
        return config

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

    def setValues(self, config):
        if 'canvas' in config:
            self.linesFrame.setValues(config['canvas'])
        else:
            self.linesFrame.setValues({})
        if 'position_styles' in config:
            self.positionStylesFrame.setValues(config['position_styles'])
        else:
            self.positionStylesFrame.setValues([])

    def getConfig(self):
        return OrderedDict({
            'canvas': self.linesFrame.getValues(),
            'position_styles': self.positionStylesFrame.getValues()
        })

class TranslationsTab(PlayoffTab):
    @property
    def title(self):
        return 'Tłumaczenia'

    def renderContent(self, container):
        self.translationsFrame = TranslationConfigurationFrame(
            container, vertical=True)
        self.translationsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def setValues(self, config):
        if 'i18n' in config:
            self.translationsFrame.setTranslations(config['i18n'])
        else:
            self.translationsFrame.setTranslations({})

    def getConfig(self):
        return OrderedDict({
            'i18n': self.translationsFrame.getTranslations()
        })

__all__ = ['MainSettingsTab', 'TeamsTab', 'MatchesTab', 'SwissesTab',
           'NetworkTab', 'VisualTab', 'StyleTab', 'TranslationsTab']
