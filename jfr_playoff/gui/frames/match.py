#coding=utf-8

import tkinter as tk
from tkinter.font import Font
from tkinter import ttk

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, RepeatableEntry, NumericSpinbox
from ..frames import SelectionFrame, SelectionButton, RefreshableOptionMenu
from ..frames.team import DBSelectionField, TeamSelectionFrame
from ..frames.team import TeamSelectionButton
from ..frames.visual import PositionsSelectionFrame
from ..variables import NotifyStringVar, NotifyIntVar, NotifyNumericVar

class SwissSettingsFrame(RepeatableFrame):
    SOURCE_LINK = 0
    SOURCE_DB = 1

    def _setPositionInfo(self, *args):
        tournamentFrom = self.setFrom.get(default=1)
        tournamentTo = min(
            self.setTo.get(default=1) \
            if self.setToEnabled.get() else 9999,
            len(self.winfo_toplevel().getTeams()))
        swissFrom = self.fetchFrom.get(default=1)
        swissTo = swissFrom + tournamentTo - tournamentFrom
        if tournamentTo < tournamentFrom:
            self.positionsInfo.configure(text='brak miejsc do ustawienia')
        else:
            self.positionsInfo.configure(text='%d-%d -> %d-%d' % (
                swissFrom, swissTo, tournamentFrom, tournamentTo))

    def _setFields(self, *args):
        checkFields = [self.setToEnabled, self.fetchFromEnabled]
        for child in self.winfo_children():
            info = child.grid_info()
            row = int(info['row'])
            if row in [1, 2] and not isinstance(child, ttk.Radiobutton):
                child.configure(
                    state=tk.NORMAL if self.source.get() == 2 - row \
                    else tk.DISABLED)
            elif row in [5, 6] and isinstance(child, tk.Spinbox):
                child.configure(
                    state=tk.NORMAL if checkFields[row-5].get() \
                    else tk.DISABLED)

    def renderContent(self):
        self.source = NotifyIntVar()
        self.fetchDB = NotifyStringVar()
        self.fetchLink = NotifyStringVar()
        self.setFrom = NotifyNumericVar()
        self.setToEnabled = NotifyIntVar()
        self.setTo = NotifyNumericVar()
        self.fetchFromEnabled = NotifyIntVar()
        self.fetchFrom = NotifyNumericVar()
        self.linkLabel = NotifyStringVar()
        self.linkRelPath = NotifyStringVar()

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        (ttk.Label(self, text='Źródło danych:')).grid(
            row=0, column=0, sticky=tk.W)
        (ttk.Radiobutton(
            self, text='Baza danych',
            variable=self.source, value=self.SOURCE_DB)).grid(
                row=1, column=0, sticky=tk.W)
        self.fetchDBField = DBSelectionField(
            self, self.fetchDB, self.fetchDB.get())
        self.fetchDBField.grid(row=1, column=1, sticky=tk.W+tk.E)
        (ttk.Radiobutton(
            self, text='Strona turnieju',
            variable=self.source, value=self.SOURCE_LINK)).grid(
                row=2, column=0, sticky=tk.W)
        (ttk.Entry(self, textvariable=self.fetchLink, width=20)).grid(
            row=2, column=1, sticky=tk.W+tk.E)

        (ttk.Separator(self, orient=tk.HORIZONTAL)).grid(
            row=3, column=0, columnspan=6, sticky=tk.E+tk.W)

        (ttk.Label(
            self, text='Ustaw od miejsca: ')).grid(
                row=4, column=0, sticky=tk.W, padx=18)
        (NumericSpinbox(
            self, textvariable=self.setFrom,
            from_=1, to=999, width=5)).grid(
                row=4, column=1, sticky=tk.W)
        (ttk.Checkbutton(
            self, variable=self.setToEnabled,
            text='Ustaw do miejsca: ')).grid(
                row=5, column=0, sticky=tk.W)
        (NumericSpinbox(
            self, textvariable=self.setTo,
            from_=1, to=999, width=5)).grid(
                row=5, column=1, sticky=tk.W)
        (ttk.Checkbutton(
            self, variable=self.fetchFromEnabled,
            text='Pobierz od miejsca: ')).grid(
                row=6, column=0, sticky=tk.W)
        (NumericSpinbox(
            self, textvariable=self.fetchFrom,
            from_=1, to=999, width=5)).grid(
                row=6, column=1, sticky=tk.W)

        (ttk.Label(self, text='Miejsca w swissie')).grid(
            row=4, column=2)
        (ttk.Label(self, text='Miejsca w klasyfikacji')).grid(
            row=4, column=3)
        self.positionsInfo = ttk.Label(self, text=' -> ', font=Font(size=16))
        self.positionsInfo.grid(row=5, column=2, columnspan=2, rowspan=2)

        (ttk.Label(self, text='Etykieta linku:')).grid(
            row=8, column=0, sticky=tk.E)
        (ttk.Entry(self, textvariable=self.linkLabel, width=20)).grid(
            row=8, column=1, sticky=tk.W+tk.E)
        (ttk.Label(self, text='(domyślnie: "Turniej o #. miejsce")')).grid(
            row=8, column=2, sticky=tk.W)

        (ttk.Label(self, text='Względna ścieżka linku do swissa:')).grid(
            row=1, column=2, sticky=tk.E)
        (ttk.Entry(self, textvariable=self.linkRelPath, width=20)).grid(
            row=1, column=3, sticky=tk.W+tk.E)

        (ttk.Separator(self, orient=tk.HORIZONTAL)).grid(
            row=7, column=0, columnspan=6, sticky=tk.E+tk.W)
        (ttk.Separator(self, orient=tk.HORIZONTAL)).grid(
            row=9, column=0, columnspan=6, sticky=tk.E+tk.W)

        self._setFields()
        self._setPositionInfo()

        self.fetchFromEnabled.trace('w', self._setFields)
        self.setToEnabled.trace('w', self._setFields)
        self.source.trace('w', self._setFields)
        self.setFrom.trace('w', self._setPositionInfo)
        self.setTo.trace('w', self._setPositionInfo)
        self.fetchFrom.trace('w', self._setPositionInfo)
        self.fetchFromEnabled.trace('w', self._setPositionInfo)
        self.setToEnabled.trace('w', self._setPositionInfo)
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self._setPositionInfo, add='+')

    def setValue(self, value):
        if 'database' in value:
            self.source.set(self.SOURCE_DB)
            self.fetchDB.set(value['database'])
            self.fetchLink.set('')
        else:
            self.source.set(self.SOURCE_LINK)
            self.fetchDB.set('')
            if 'link' in value:
                self.fetchLink.set(value['link'])
            else:
                self.fetchLink.set('')
        self.setFrom.set(value['position'] if 'position' in value else 1)
        if 'position_to' in value:
            self.setToEnabled.set(1)
            self.setTo.set(value['position_to'])
        else:
            self.setToEnabled.set(0)
            self.setTo.set(1)
        if 'swiss_position' in value:
            self.fetchFromEnabled.set(1)
            self.fetchFrom.set(value['swiss_position'])
        else:
            self.fetchFromEnabled.set(0)
            self.fetchFrom.set(1)
        self.linkLabel.set(value['label'] if 'label' in value else '')
        self.linkRelPath.set(
            value['relative_path'] if 'relative_path' in value else '')

    def getValue(self):
        config = {}
        if self.source.get() == self.SOURCE_DB:
            config['database'] = self.fetchDB.get()
            if self.linkRelPath.get():
                config['relative_path'] = self.linkRelPath.get()
        if self.source.get() == self.SOURCE_LINK:
            config['link'] = self.fetchLink.get()
        if self.linkLabel.get():
            config['label'] = self.linkLabel.get()
        config['position'] = self.setFrom.get()
        if self.setToEnabled.get():
            config['position_to'] = self.setTo.get()
        if self.fetchFromEnabled.get():
            config['swiss_position'] = self.fetchFrom.get()
        return config

class SwissesFrame(ScrollableFrame):
    def renderContent(self, container):
        self.swisses = WidgetRepeater(container, SwissSettingsFrame)
        self.swisses.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def setValues(self, values):
        self.swisses.setValue(values)

    def getValues(self):
        return self.swisses.getValue()

class MatchSelectionButton(SelectionButton):
    @property
    def defaultPrompt(self):
        return 'Wybierz mecze:'

    @property
    def title(self):
        return 'Wybór meczów'

    @property
    def errorMessage(self):
        return 'W turnieju nie zdefiniowano żadnych meczów'

    def getOptions(self):
        return self.winfo_toplevel().getMatches()


class MatchSelectionFrame(SelectionFrame):
    def renderOption(self, container, option, idx):
        (ttk.Label(
            container, text='[%d]' % (self._mapValue(idx, option)))).grid(
                row=idx+1, column=0)
        (ttk.Checkbutton(
            container, text=option.label,
            variable=self.values[self._mapValue(idx, option)]
        )).grid(row=idx+1, column=1, sticky=tk.W)

    def _mapValue(self, idx, value):
        return self.options[idx].getMatchID()


class SelectedTeamList(RefreshableOptionMenu):
    VALUE_LABELS = {
        'none': u'%s',
        'winner': u'Zwycięzca meczu %d',
        'loser': u'Przegrany meczu %d',
        'place': u'Drużyna z miejsca %d'
    }

    def __init__(self, *args, **kwargs):
        RefreshableOptionMenu.__init__(self, *args, **kwargs)
        self.master.bind(
            '<<BracketConfigChanged>>', self.refreshOptions, add='+')

    def getValues(self):
        config = self.master.getConfig()
        values = [('none', '')]
        if isinstance(config, dict):
            for key in ['winner', 'loser', 'place']:
                if key in config:
                    for value in config[key]:
                        values.append((key, value))
        return values

    def getLabel(self, value):
        return self.VALUE_LABELS[value[0]] % (value[1])

    def getVarValue(self, value):
        return unicode(value)


class BracketMatchSettingsFrame(GuiFrame):
    SOURCE_TEAM=0
    SOURCE_BRACKET=1
    LIST_WIDGETS = {'place': 5, 'winner': 1, 'loser': 3}

    def _enablePanels(self, *args):
        for widget in self.teamWidgets:
            widget.configure(
                state=tk.NORMAL if self.source.get() == self.SOURCE_TEAM
                else tk.DISABLED)
        for widget in self.bracketWidgets:
            widget.configure(
                state=tk.NORMAL if self.source.get() == self.SOURCE_BRACKET
                else tk.DISABLED)
            if self.source.get() == self.SOURCE_BRACKET \
               and isinstance(widget, SelectedTeamList) \
               and not self.selected.get():
                widget.configure(state=tk.DISABLED)

    def _configChangeNotify(self, *args):
        self.event_generate('<<BracketConfigChanged>>', when='tail')

    def _setPositions(self, positions):
        self.positions = positions
        self._configChangeNotify()

    def _setLosers(self, matches):
        self.losers = matches
        self._configChangeNotify()

    def _setWinners(self, matches):
        self.winners = matches
        self._configChangeNotify()

    def _setTeams(self, teams):
        if not self._lockTeams:
            allTeams = [team[0] for team in self.teamWidgets[0].getOptions()]
            self.teams = [allTeams[idx-1] for idx in teams]

    def renderContent(self):
        self.source = NotifyIntVar()
        self.source.trace('w', self._enablePanels)
        self.source.trace('w', self._configChangeNotify)
        self.selected = NotifyIntVar()
        self.selected.trace('w', self._enablePanels)
        self.selectedIndex = NotifyStringVar()
        self.positions = []
        self.winners = []
        self.losers = []
        self.teams = []
        self._lockTeams = True
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self._onTeamListChange, add='+')
        self.winfo_toplevel().bind(
            '<<MatchListChanged>>', self._onMatchListChange, add='+')

        buttons = [
            ttk.Radiobutton(
                self, variable=self.source, value=self.SOURCE_TEAM,
                text='Konkretne teamy'),
            ttk.Radiobutton(
                self, variable=self.source, value=self.SOURCE_BRACKET,
                text='Z drabinki')]
        self.teamWidgets = [
            TeamSelectionButton(
                self, prompt='Wybierz drużyny:',
                dialogclass=TeamSelectionFrame,
                callback=self._setTeams)]
        self.bracketWidgets = [
            ttk.Label(self, text='Zwycięzcy meczów:'),
            MatchSelectionButton(
                self, prompt='Wybierz mecze:',
                dialogclass=MatchSelectionFrame,
                callback=self._setWinners),
            ttk.Label(self, text='Przegrani meczów:'),
            MatchSelectionButton(
                self, prompt='Wybierz mecze:',
                dialogclass=MatchSelectionFrame,
                callback=self._setLosers),
            ttk.Label(self, text='Pozycje początkowe:'),
            TeamSelectionButton(
                self, prompt='Wybierz pozycje początkowe:',
                dialogclass=PositionsSelectionFrame,
                callback=self._setPositions),
            ttk.Checkbutton(
                self, text='Uczestnik został wybrany:',
                variable=self.selected),
            SelectedTeamList(self, self.selectedIndex)
        ]

        for idx, button in enumerate(buttons):
            button.grid(row=idx, column=0, sticky=tk.W)
        self.teamWidgets[0].grid(row=0, column=1, sticky=tk.W)
        for idx, widget in enumerate(self.bracketWidgets):
            widget.grid(row=1+idx/2, column=1+idx%2, sticky=tk.W)

        self._lockTeams = False

    def _onTeamListChange(self, *args):
        teamsToSet = []
        teams = [team[0] for team in self.teamWidgets[0].getOptions()]
        for team in self.teams:
            try:
                teamsToSet.append(teams.index(team)+1)
            except ValueError:
                pass
        self._lockTeams = True
        self.teamWidgets[0].setPositions(teamsToSet)
        self._lockTeams = False

    def _onMatchListChange(self, *args):
        try:
            matches = [
                match.getMatchID() for match
                in self.bracketWidgets[
                    self.LIST_WIDGETS['winner']].getOptions()]
            self.bracketWidgets[self.LIST_WIDGETS['winner']].setPositions([
                winner for winner in self.winners if winner in matches])
            self.bracketWidgets[self.LIST_WIDGETS['loser']].setPositions([
                loser for loser in self.losers if loser in matches])
        except tk.TclError as e:
            # we're probably trying to update our widget when
            # WE'RE the match that's being destroyed
            pass

    def setValue(self, value):
        if isinstance(value, (str, unicode)):
            value = [value]
        if isinstance(value, list):
            self.source.set(self.SOURCE_TEAM)
            self.teams = list(set(value))
            for idx in self.LIST_WIDGETS.values():
                self.bracketWidgets[idx].setPositions([])
        else:
            self.source.set(self.SOURCE_BRACKET)
            self.teams = []
            for key, idx in self.LIST_WIDGETS.iteritems():
                self.bracketWidgets[idx].setPositions(
                    value[key]
                    if key in value and isinstance(value[key], list)
                    else [])

    def setSelectedTeam(self, team):
        if team > -1:
            self.selectedIndex.set(self.bracketWidgets[7].getValues()[team+1])
            self.selected.set(1)
        else:
            self.selectedIndex.set(('none', ''))
            self.selected.set(0)

    def getSelectedTeam(self):
        if self.selected.get():
            try:
                return self.bracketWidgets[7].getValues().index(
                    self.selectedIndex.get())
            except ValueError:
                return -1
        else:
            return -1

    def getConfig(self):
        if self.source.get() == self.SOURCE_TEAM:
            return self.teams
        else:
            config = {}
            lists = {
                5: self.positions,
                1: self.winners,
                3: self.losers
            }
            for key, idx in self.LIST_WIDGETS.iteritems():
                values = lists[idx]
                if len(values) > 0:
                    config[key] = values
            return config

    def getValue(self):
        return self.getConfig()

class MatchSettingsFrame(RepeatableFrame):
    SCORE_SOURCE_DB = 0
    SCORE_SOURCE_LINK = 1
    SCORE_SOURCE_CUSTOM = 2

    def destroy(self, *args, **kwargs):
        self.winfo_toplevel().event_generate(
            '<<MatchListChanged>>', when='tail')
        RepeatableFrame.destroy(self, *args, **kwargs)

    def _enablePanels(self, *args):
        for val, fields in self.scoreWidgets.iteritems():
            for field in fields:
                field.configure(
                    state=tk.NORMAL if self.source.get() == val
                    else tk.DISABLED)
        if not self.scoreNotFinished.get():
            self.scoreWidgets[self.SCORE_SOURCE_CUSTOM][-2].configure(
                state=tk.DISABLED)

    def _updateName(self, *args):
        self.nameLabel.configure(text=self.label)

    def _setWinnerPositions(self, values):
        self.winnerPositions = values

    def _setLoserPositions(self, values):
        self.loserPositions = values

    def renderContent(self):
        self.nameLabel = ttk.Label(self)
        self.matchID = NotifyIntVar()
        self.matchID.trace('w', self._updateName)
        self.matchID.set(self.winfo_toplevel().getNewMatchID(self))
        self.winfo_toplevel().bind(
            '<<PhaseRenamed>>', self._updateName, add='+')
        self.link = NotifyStringVar()

        self.source = NotifyIntVar()
        self.source.trace('w', self._enablePanels)

        self.scoreDB = NotifyStringVar()
        self.scoreRound = NotifyNumericVar()
        self.scoreTable = NotifyNumericVar()
        self.scoreCustom = [NotifyStringVar(), NotifyStringVar()]
        self.scoreNotFinished = NotifyIntVar()
        self.scoreNotFinished.trace('w', self._enablePanels)
        self.scoreBoards = NotifyNumericVar()

        self.winnerPositions = []
        self.loserPositions = []

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.nameLabel.grid(row=0, column=0, sticky=tk.W)
        (ttk.Label(self, text='Link:')).grid(row=0, column=1, sticky=tk.E)
        (ttk.Entry(self, textvariable=self.link)).grid(
            row=0, column=2, sticky=tk.W+tk.E)

        bracketGroup = ttk.LabelFrame(self, text='Dane drabinki')
        bracketGroup.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E)

        bracketGroup.columnconfigure(0, weight=1)
        bracketGroup.columnconfigure(1, weight=1)

        homeTeam = ttk.LabelFrame(bracketGroup, text='Team gospodarzy')
        homeTeam.grid(row=0, column=0, sticky=tk.W+tk.E)
        awayTeam = ttk.LabelFrame(bracketGroup, text='Team gości')
        awayTeam.grid(row=0, column=1, sticky=tk.W+tk.E)

        teamFrames = [homeTeam, awayTeam]
        self.bracketSettings = []
        for frame in teamFrames:
            bracket = BracketMatchSettingsFrame(frame)
            bracket.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
            self.bracketSettings.append(bracket)

        scoreGroup = ttk.LabelFrame(self, text='Dane wyniku meczu')
        scoreGroup.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E)

        scoreGroup.columnconfigure(1, weight=1)
        scoreGroup.columnconfigure(3, weight=1)

        self.scoreWidgets = {
            self.SCORE_SOURCE_DB: [
                DBSelectionField(scoreGroup, self.scoreDB, self.scoreDB.get()),
                ttk.Label(scoreGroup, text='Runda:'),
                NumericSpinbox(
                    scoreGroup, width=3,
                    textvariable=self.scoreRound, from_=1, to=999),
                ttk.Label(scoreGroup, text='Stół:'),
                NumericSpinbox(
                    scoreGroup, width=3,
                    textvariable=self.scoreTable, from_=1, to=999)
            ],
            self.SCORE_SOURCE_LINK: [
                ttk.Entry(scoreGroup, textvariable=self.link),
                # TODO: TC support (Round/Session)
                #ttk.Label(scoreGroup, text='Sesja:'),
                #NumericSpinbox(
                #    scoreGroup,
                #textvariable=self.scoreSession, from_=1, to=999),
                #ttk.Label(scoreGroup, text='Runda:'),
                #NumericSpinbox(
                #    scoreGroup,
                #textvariable=self.scoreRound, from_=1, to=999),
                ttk.Label(scoreGroup, text='Stół:'),
                NumericSpinbox(
                    scoreGroup, width=3,
                    textvariable=self.scoreTable, from_=1, to=999)
            ],
            self.SCORE_SOURCE_CUSTOM: [
                ttk.Entry(
                    scoreGroup, textvariable=self.scoreCustom[0],
                    width=10, justify=tk.RIGHT),
                ttk.Label(scoreGroup, text=':'),
                ttk.Entry(
                    scoreGroup, textvariable=self.scoreCustom[1],
                    width=10, justify=tk.RIGHT),
                ttk.Checkbutton(
                    scoreGroup, variable=self.scoreNotFinished,
                    text='mecz nie został zakończony, rozegrano:'),
                NumericSpinbox(
                    scoreGroup, width=3,
                    textvariable=self.scoreBoards, from_=0, to=999),
                ttk.Label(scoreGroup, text='rozdań')
            ]
        }

        (ttk.Radiobutton(
            scoreGroup, variable=self.source, value=self.SCORE_SOURCE_DB,
            text='Baza danych')).grid(row=0, column=0, sticky=tk.W)
        self.scoreWidgets[self.SCORE_SOURCE_DB][0].grid(
            row=0, column=1, columnspan=3, sticky=tk.W+tk.E)
        for idx in range(1, 5):
            self.scoreWidgets[self.SCORE_SOURCE_DB][idx].grid(
                row=0, column=idx+3)
        (ttk.Radiobutton(
            scoreGroup, variable=self.source, value=self.SCORE_SOURCE_LINK,
            text='Strona z wynikami')).grid(row=1, column=0, sticky=tk.W)
        self.scoreWidgets[self.SCORE_SOURCE_LINK][0].grid(
            row=1, column=1, columnspan=3, sticky=tk.W+tk.E)
        self.scoreWidgets[self.SCORE_SOURCE_LINK][1].grid(
            row=1, column=4)
        self.scoreWidgets[self.SCORE_SOURCE_LINK][2].grid(
            row=1, column=5)
        (ttk.Radiobutton(
            scoreGroup, variable=self.source, value=self.SCORE_SOURCE_CUSTOM,
            text='Ustaw ręcznie')).grid(row=2, column=0, sticky=tk.W)
        for idx in range(0, 3):
            self.scoreWidgets[self.SCORE_SOURCE_CUSTOM][idx].grid(
                row=2, column=idx+1, sticky=tk.E if idx == 0 else tk.W)
        self.scoreWidgets[self.SCORE_SOURCE_CUSTOM][3].grid(
            row=2, column=4, columnspan=4)
        for idx in range(4, 6):
            self.scoreWidgets[self.SCORE_SOURCE_CUSTOM][idx].grid(
                row=2, column=idx+5)

        (ttk.Label(bracketGroup, text='Zwycięzca zajmie miejsca:')).grid(
            row=1, column=0, sticky=tk.E)
        self.winnerPositionsBtn = TeamSelectionButton(
            bracketGroup, prompt='Wybierz pozycje końcowe:',
            dialogclass=PositionsSelectionFrame,
            callback=self._setWinnerPositions)
        self.winnerPositionsBtn.grid(row=1, column=1, sticky=tk.W)
        (ttk.Label(bracketGroup, text='Przegrany zajmie miejsca:')).grid(
            row=2, column=0, sticky=tk.E)
        self.loserPositionsBtn = TeamSelectionButton(
            bracketGroup, prompt='Wybierz pozycje końcowe:',
            dialogclass=PositionsSelectionFrame,
            callback=self._setLoserPositions)
        self.loserPositionsBtn.grid(row=2, column=1, sticky=tk.W)

        self.winfo_toplevel().event_generate(
            '<<MatchListChanged>>', when='tail')

    @classmethod
    def info(cls):
        return 'Nowy mecz'

    def getMatchID(self):
        return self.matchID.get()

    def _getPhase(self):
        obj = self
        while not isinstance(obj, MatchPhaseFrame):
            obj = obj.master
            if obj is None:
                break
        return obj

    @property
    def label(self):
        try:
            phase = self._getPhase()
            return 'Mecz #%d (%s)' % (
                self.getMatchID(),
                phase.master.tab(phase)['text'] if phase is not None else '')
        except tk.TclError:
            # we're probably just being created, ignore
            return ''

    def setValue(self, value):
        self.matchID.set(value['id'] if 'id' in value else 0)
        self.link.set(value['link'] if 'link' in value else '')

        self.scoreDB.set(value['database'] if 'database' in value else '')
        self.scoreRound.set(value['round'] if 'round' in value else 1)
        self.scoreTable.set(value['table'] if 'table' in value else 1)

        if 'score' in value:
            for idx in range(0, 2):
                self.scoreCustom[idx].set(
                    value['score'][idx]
                    if isinstance(value['score'], list)
                    and len(value['score']) > 1
                    else 0)
                self.scoreNotFinished.set(
                    'running' in value and value['running'] >= 0)
                self.scoreBoards.set(
                    value['running'] if 'running' in value
                    and value['running'] >= 0 else 0)
        else:
            self.scoreNotFinished.set(0)
            self.scoreBoards.set(0)

        self.source.set(
            self.SCORE_SOURCE_DB if 'database' in value else (
                self.SCORE_SOURCE_CUSTOM if 'table' not in value
                else self.SCORE_SOURCE_LINK
        ))

        if 'teams' in value and isinstance(value['teams'], list):
            for idx, val in enumerate(value['teams']):
                if idx < 2:
                    self.bracketSettings[idx].setValue(val)
        else:
            for idx in range(0, 2):
                self.bracketSettings[idx].setValue({})

        self.winnerPositionsBtn.setPositions(
            value['winner']
            if 'winner' in value and isinstance(value['winner'], list)
            else [])
        self.loserPositionsBtn.setPositions(
            value['loser']
            if 'loser' in value and isinstance(value['loser'], list)
            else [])

        if 'selected_teams' in value \
           and isinstance(value['selected_teams'], list):
            for idx, val in enumerate(value['selected_teams']):
                if idx < 2:
                    self.bracketSettings[idx].setSelectedTeam(val)
        else:
            for idx in range(0, 2):
                self.bracketSettings[idx].setSelectedTeam(-1)

    def getValue(self):
        config = {}
        config['id'] = self.matchID.get()
        if self.link.get():
            config['link'] = self.link.get()

        config['teams'] = [bracket.getValue()
                           for bracket in self.bracketSettings]

        if len(self.winnerPositions):
            config['winner'] = self.winnerPositions
        if len(self.loserPositions):
            config['loser'] = self.loserPositions

        selected = [bracket.getSelectedTeam()
                    for bracket in self.bracketSettings]
        if len([s for s in selected if s > -1]):
            config['selected_teams'] = selected

        if self.source.get() == self.SCORE_SOURCE_DB:
            config['database'] = self.scoreDB.get()
            config['round'] = self.scoreRound.get()
        if self.source.get() != self.SCORE_SOURCE_CUSTOM:
            config['table'] = self.scoreTable.get()

        if self.source.get() == self.SCORE_SOURCE_CUSTOM:
            config['score'] = []
            for score in self.scoreCustom:
                try:
                    config['score'].append(float(score.get()))
                except ValueError:
                    config['score'].append(0.0)
            if self.scoreNotFinished.get():
                config['running'] = self.scoreBoards.get()

        return config

        if 'selected_teams' in value \
           and isinstance(value['selected_teams'], list):
            for idx, val in enumerate(value['selected_teams']):
                if idx < 2:
                    self.bracketSettings[idx].setSelectedTeam(val)
        else:
            for idx in range(0, 2):
                self.bracketSettings[idx].setSelectedTeam(-1)



class MatchSeparator(RepeatableFrame):
    def renderContent(self):
        (ttk.Separator(self, orient=tk.HORIZONTAL)).pack(
            side=tk.TOP, fill=tk.X, expand=True)

    @classmethod
    def info(cls):
        return 'Odstęp między meczami'


class MatchPhaseFrame(ScrollableFrame):
    def _updateLinks(self, *args):
        for match in self.matches.widgets:
            if isinstance(match, MatchSettingsFrame):
                match_link = match.link.get()
                if not len(match_link) or match_link == self.previousLink:
                    match.link.set(self.link.get())
        self.previousLink = self.link.get()

    def _signalPhaseRename(self, *args):
        self.winfo_toplevel().event_generate('<<PhaseRenamed>>', when='tail')

    def renderContent(self, container):
        self.name = NotifyStringVar()
        self.link = NotifyStringVar()
        self.previousLink = ''

        headerFrame = tk.Frame(container)
        headerFrame.pack(side=tk.TOP, fill=tk.X, expand=True)
        (ttk.Label(headerFrame, text='Nazwa:')).pack(side=tk.LEFT)
        (ttk.Entry(headerFrame, textvariable=self.name)).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        (ttk.Label(headerFrame, text='Link:')).pack(side=tk.LEFT)
        (ttk.Entry(headerFrame, textvariable=self.link)).pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        self.matches = WidgetRepeater(
            container, [MatchSettingsFrame, MatchSeparator])
        self.matches.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.link.trace('w', self._updateLinks)
        self.name.trace('w', self._signalPhaseRename)

    def setValues(self, values):
        matches = values['matches'] if 'matches' in values else []
        dummies = values['dummies'] if 'dummies' in values else []
        objects = [(MatchSeparator, None)] * (len(matches) + len(dummies))
        idx = 0
        for match in matches:
            while idx in dummies:
                idx += 1
            objects[idx] = (MatchSettingsFrame, match)
            idx += 1
        self.matches.setValue(objects)
        self.link.set(values['link'] if 'link' in values else '')
        self.name.set(values['title'] if 'title' in values else '')
        self.winfo_toplevel().event_generate(
            '<<MatchListChanged>>', when='tail')

    def getConfig(self):
        config = {}
        if self.name.get():
            config['title'] = self.name.get()
        if self.link.get():
            config['link'] = self.link.get()
        values = self.matches.getValue()
        dummies = []
        matches = []
        for idx, value in enumerate(values):
            if value is None:
                dummies.append(idx)
            else:
                matches.append(value)
        if len(dummies):
            config['dummies'] = dummies
        config['matches'] = matches
        return config


__all__ = ['SwissesFrame', 'MatchPhaseFrame', 'MatchSettingsFrame']
