#coding=utf-8

from collections import OrderedDict

import tkinter as tk
from tkinter.font import Font
from tkinter import ttk

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, RepeatableEntry, NumericSpinbox
from ..frames import SelectionButton, SelectionFrame, RefreshableOptionMenu
from ..frames import setPanelState
from ..variables import NotifyStringVar, NotifyIntVar, NotifyNumericVar

class ManualTeamRow(RepeatableFrame):
    def renderContent(self):
        self.fullname = NotifyStringVar()
        self.shortname = NotifyStringVar()
        self.flag = NotifyStringVar()
        self.position = NotifyNumericVar()
        for var in [self.fullname, self.shortname, self.flag, self.position]:
            var.trace('w', self._changeNotify)

        fullnameField = ttk.Entry(self, width=20, textvariable=self.fullname)
        fullnameField.grid(row=0, column=0)
        shortnameField = ttk.Entry(self, width=20, textvariable=self.shortname)
        shortnameField.grid(row=0, column=1)
        flagField = ttk.Entry(self, width=10, textvariable=self.flag)
        flagField.grid(row=0, column=2)
        positionField = ttk.Entry(self, width=10, textvariable=self.position)
        positionField.grid(row=0, column=3)

        self._changeNotify(None)

    def getValue(self):
        flag = self.flag.get().strip()
        position = self.position.get()
        return [
            self.fullname.get().strip(), self.shortname.get().strip(),
            flag if len(flag) else None, position
        ]

    def setValue(self, value):
        self.fullname.set(value[0])
        self.shortname.set(value[1])
        if len(value) > 2:
            if value[2] is not None:
                self.flag.set(value[2])
        if len(value) > 3:
            if value[3] is not None:
                self.position.set(value[3])

    def _changeNotify(self, *args):
        self.winfo_toplevel().event_generate(
            '<<TeamSettingsChanged>>', when='tail')

class TeamManualSettingsFrame(GuiFrame):
    def renderContent(self):
        headers = [
            (ttk.Label, {'text': 'Pełna nazwa', 'width': 20}),
            (ttk.Label, {'text': 'Skrócona nazwa', 'width': 20}),
            (ttk.Label, {'text': 'Ikona', 'width': 10}),
            (ttk.Label, {'text': 'Poz. końc.', 'width': 10}),
        ]
        self.repeater = WidgetRepeater(self, ManualTeamRow, headers=headers)
        self.repeater.grid(row=1, column=0, columnspan=5)

    def getTeams(self):
        return [val for val in self.repeater.getValue() if len(val[0].strip())]

    def setValues(self, values):
        self.repeater.setValue(values)

class TeamSelectionFrame(SelectionFrame):
    def renderOption(self, container, option, idx):
        (ttk.Label(
            container, text='[%d]' % (self._mapValue(idx, option)))).grid(
                row=idx+1, column=0)
        (ttk.Checkbutton(
            container, text=option[0],
            variable=self.values[self._mapValue(idx, option)]
        )).grid(row=idx+1, column=1, sticky=tk.W)

class TeamSelectionButton(SelectionButton):
    @property
    def prompt(self):
        return 'Wybierz teamy:'

    @property
    def title(self):
        return 'Wybór teamów'

    @property
    def errorMessage(self):
        return 'W turnieju nie ma teamów do wyboru'

    def getOptions(self):
        return self.winfo_toplevel().getTeams()


class DBSelectionField(ttk.Entry):
    def __init__(self, master, variable, value, *options, **kwargs):
        kwargs['textvariable'] = variable
        ttk.Entry.__init__(self, master, **kwargs)
        self._variable = variable
        self._variable.set(value)
        self._optionDict = options if options is not None else []
        self._matches = []
        self._prevValue = None
        self._setOptions()
        self.bind('<KeyPress>', self._onPress)
        self.bind('<KeyRelease>', self._onChange)
        self.winfo_toplevel().bind(
            '<<DBListChanged>>', self._setOptions, add='+')

    def _setOptions(self, *args):
        try:
            self._optionDict = self.winfo_toplevel().getDBs()
        except:
            # some stuff may not be available yet
            # don't worry, the event will fire when it is
            self._optionDict = []

    def _onPress(self, event):
        if event.keysym == 'Tab':
            try:
                suggestion = self.selection_get()
                if len(suggestion) > 0:
                    prefix = self._variable.get()[0:-len(suggestion)]
                    phrase = prefix + suggestion
                    next_suggestion = self._matches[
                        (self._matches.index(phrase)+1) % len(self._matches)]
                    prev_suggestion = self._matches[
                        (self._matches.index(phrase)-1) % len(self._matches)]
                    new_suggestion = prev_suggestion if event.state & 1 \
                        else next_suggestion
                    self.delete(0, tk.END)
                    self.insert(0, new_suggestion)
                    self.selection_range(len(prefix), tk.END)
                    return 'break'
            except (tk.TclError, ValueError):
                # no text selection or selection was altered, ignore
                pass

    def _onChange(self, event):
        if self._prevValue == self._variable.get() or event.keysym == 'Tab':
            return
        self._prevValue = self._variable.get()
        prefix = self._variable.get()
        if len(prefix) > 0:
            matches = [d for d in self._optionDict if d.startswith(prefix)]
            if len(matches) > 0:
                self._matches = matches
                text_to_add = matches[0][len(prefix):]
                self.insert(tk.END, text_to_add)
                self.selection_range(len(prefix), tk.END)
                return
        self._matches = []

class TeamFetchSettingsFrame(GuiFrame):
    SOURCE_LINK = 0
    SOURCE_DB = 1

    def _setFinishingPositions(self, positions):
        self.finishingPositions = positions
        self._changeNotify(None)

    def _changeNotify(self, *args):
        self.winfo_toplevel().event_generate(
            '<<TeamSettingsChanged>>', when='tail')

    def getTeams(self):
        teams = OrderedDict()
        if self.fetchSource.get() == self.SOURCE_LINK:
            teams['link'] = self.fetchLink.get()
        elif self.fetchSource.get() == self.SOURCE_DB:
            teams['database'] = self.fetchDB.get()
        if len(self.finishingPositions):
            teams['final_positions'] = self.finishingPositions
        maxTeams = self.fetchLimit.get()
        if maxTeams:
            teams['max_teams'] = maxTeams
        return teams

    def _sourceChange(self, *args):
        self.fetchDBField.configure(state=tk.DISABLED)
        self.fetchLink.configure(state=tk.DISABLED)
        if self.fetchSource.get() == self.SOURCE_LINK:
            self.fetchLink.configure(state=tk.NORMAL)
        elif self.fetchSource.get() == self.SOURCE_DB:
            self.fetchDBField.configure(state=tk.NORMAL)

    def renderContent(self):
        self.fetchSource = NotifyIntVar()
        self.fetchSource.trace('w', self._sourceChange)
        self.fetchSource.trace('w', self._changeNotify)
        self.fetchDB = NotifyStringVar()
        self.fetchDB.trace('w', self._changeNotify)
        self.link = NotifyStringVar()
        self.link.trace('w', self._changeNotify)
        self.fetchLimit = NotifyNumericVar()
        self.fetchLimit.trace('w', self._changeNotify)

        self.columnconfigure(3, weight=1)

        (ttk.Label(self, text=' ')).grid(row=0, column=0, rowspan=2)

        (ttk.Radiobutton(
            self, text='Baza danych',
            variable=self.fetchSource, value=self.SOURCE_DB)).grid(
                row=0, column=1, columnspan=2, sticky=tk.W)
        self.fetchDBField = DBSelectionField(
            self, self.fetchDB, self.fetchDB.get())
        self.fetchDBField.grid(row=0, column=3, sticky=tk.W+tk.E)

        (ttk.Radiobutton(
            self, text='Strona wyników',
            variable=self.fetchSource, value=self.SOURCE_LINK)).grid(
                row=1, column=1, columnspan=2, sticky=tk.W)
        self.fetchLink = ttk.Entry(self, textvariable=self.link)
        self.fetchLink.grid(row=1, column=3, sticky=tk.W+tk.E)

        (ttk.Label(self, text='Pobierz do ')).grid(
            row=2, column=0, columnspan=2, sticky=tk.W)
        (NumericSpinbox(
            self, from_=0, to=9999, width=5, justify=tk.RIGHT,
            textvariable=self.fetchLimit)).grid(
                row=2, column=2, sticky=tk.W)
        (ttk.Label(self, text=' miejsca (0 = wszystkie)')).grid(
            row=2, column=3, sticky=tk.W+tk.E)

        (ttk.Label(self, text='Pozycje końcowe: ')).grid(
            row=3, column=0, columnspan=3, sticky=tk.W+tk.E)
        self.finishingPositionsBtn = TeamSelectionButton(
            self, callback=self._setFinishingPositions,
            prompt='Wybierz teamy, które zakończyły rozgrywki ' + \
            'na swojej pozycji:',
            dialogclass=TeamSelectionFrame)
        self.finishingPositionsBtn.grid(row=3, column=3, sticky=tk.W)
        self.finishingPositionsBtn.setPositions([])

    def setValues(self, values):
        if 'database' in values:
            self.fetchSource.set(self.SOURCE_DB)
            self.fetchDB.set(values['database'])
            self.link.set('')
        else:
            self.fetchSource.set(self.SOURCE_LINK)
            self.fetchDB.set('')
            self.link.set(values['link'] if 'link' in values else '')
        self.fetchLimit.set(
            values['max_teams'] if 'max_teams' in values else 0)
        self.finishingPositionsBtn.setPositions(
            values['final_positions'] if 'final_positions' in values else [])

class TeamSettingsFrame(ScrollableFrame):
    FORMAT_FETCH = 0
    FORMAT_MANUAL = 1

    def _enablePanels(self, *args):
        panels = {self.FORMAT_FETCH: self.fetchSettingsFrame,
                  self.FORMAT_MANUAL: self.manualSettingsFrame}
        for value, panel in panels.iteritems():
            setPanelState(
                frame=panel,
                state=tk.NORMAL \
                if self.teamFormat.get()==value else tk.DISABLED)

    def _changeNotify(self, *args):
        self.winfo_toplevel().event_generate(
            '<<TeamSettingsChanged>>', when='tail')

    def setTeams(self, event):
        self.teams = self.winfo_toplevel().getTeams()

    def renderContent(self, container):
        self.teamFormat = NotifyIntVar()
        self.teamFormat.trace('w', self._enablePanels)
        self.teamFormat.trace('w', self._changeNotify)

        container.columnconfigure(0, weight=1)

        (ttk.Radiobutton(
            container, text='Pobierz z:',
            variable=self.teamFormat, value=self.FORMAT_FETCH)).grid(
                row=0, column=0, sticky=tk.W)

        self.fetchSettingsFrame = TeamFetchSettingsFrame(container)
        self.fetchSettingsFrame.grid(row=1, column=0, sticky=tk.W+tk.E)

        (ttk.Separator(
            container, orient=tk.HORIZONTAL)).grid(
                row=2, column=0, sticky=tk.W+tk.E)

        (ttk.Radiobutton(
            container, text='Ustaw ręcznie:',
            variable=self.teamFormat, value=self.FORMAT_MANUAL)).grid(
                row=3, column=0, sticky=tk.W+tk.E)

        self.manualSettingsFrame = TeamManualSettingsFrame(container)
        self.manualSettingsFrame.grid(row=4, column=0, sticky=tk.W+tk.E)

        self.teams = []
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.setTeams, add='+')

    def getConfig(self):
        if self.teamFormat.get() == self.FORMAT_MANUAL:
            return self.manualSettingsFrame.getTeams()
        elif self.teamFormat.get() == self.FORMAT_FETCH:
            return self.fetchSettingsFrame.getTeams()
        return []

    def setValues(self, values):
        if isinstance(values, list):
            self.teamFormat.set(self.FORMAT_MANUAL)
            self.manualSettingsFrame.setValues(values)
            self.fetchSettingsFrame.setValues({})
        else:
            self.teamFormat.set(self.FORMAT_FETCH)
            self.manualSettingsFrame.setValues([])
            self.fetchSettingsFrame.setValues(values)

class TeamList(RefreshableOptionMenu):
    def __init__(self, *args, **kwargs):
        RefreshableOptionMenu.__init__(self, *args, **kwargs)
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.refreshOptions, add='+')
        self.configure(width=10)

    def getLabel(self, team):
        return team[0]

    def getValues(self):
        return self.winfo_toplevel().getTeams()


class TeamAliasRow(RepeatableFrame):
    def renderContent(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.teamName = NotifyStringVar()
        list = TeamList(self, self.teamName, self.teamName.get())
        list.configure(width=20)
        list.grid(
            row=0, column=0, sticky=tk.W+tk.E+tk.N)
        self.names = WidgetRepeater(self, RepeatableEntry)
        self.names.grid(row=0, column=1, sticky=tk.W+tk.E)

    def getValue(self):
        return (
            self.teamName.get().strip(),
            [val.strip() for val in self.names.getValue()])

    def setValue(self, value):
        self.teamName.set(value[0])
        self.names.setValue(value[1])


class TeamAliasFrame(ScrollableFrame):
    def renderContent(self, container):
        container.columnconfigure(0, weight=1)
        (ttk.Label(container, text='Aliasy teamów')).grid(
            row=0, column=0, sticky=tk.W+tk.E)
        self.repeater = WidgetRepeater(container, TeamAliasRow)
        self.repeater.grid(row=1, column=0, sticky=tk.W+tk.E)

    def getConfig(self):
        return OrderedDict(
            {val[0]: val[1] for val in self.repeater.getValue() if val[0]})

    def setValues(self, values):
        self.repeater.setValue(list(values.iteritems()))

class TeamPreviewFrame(ScrollableFrame):
    def __init__(self, *args, **kwags):
        self.tieValues = []
        self.tieFields = []
        self.orderValues = []
        self.orderFields = []
        self.labels = []
        ScrollableFrame.__init__(self, *args, **kwags)
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.refreshTeams, add='+')
        self.winfo_toplevel().bind(
            '<<TieConfigChanged>>', self._collectTieConfig, add='+')
        self._tieConfig = []
        self._lockTieValues = False
        self.winfo_toplevel().bind(
            '<<OrderConfigChanged>>', self._collectOrderConfig, add='+')
        self._orderConfig = []
        self._lockOrderValues = False

    def setTeams(self, container, teams):
        self.teamList.grid(
            row=1, column=0, rowspan=len(teams)+2, sticky=tk.W+tk.E+tk.N+tk.S)
        self.tieValues = self.tieValues[0:len(teams)]
        for idx in range(len(teams), len(self.tieFields)):
            self.tieFields[idx].destroy()
        self.tieFields = self.tieFields[0:len(teams)]
        self.orderValues = self.orderValues[0:len(teams)]
        for idx in range(len(teams), len(self.orderFields)):
            self.orderFields[idx].destroy()
        self.orderFields = self.orderFields[0:len(teams)]
        for label in self.labels:
            label.destroy()
        self.teamList.delete(*self.teamList.get_children())
        for idx, team in enumerate(teams):
            if len(team) > 2 and team[2] is None:
                team[2] = ''
            self.teamList.insert('', tk.END, values=team, tag=idx)
            if idx >= len(self.tieFields):
                self.tieValues.append(NotifyNumericVar())
                self.tieValues[idx].trace('w', self._tieValueChangeNotify)
                self.tieFields.append(
                    NumericSpinbox(
                        container, from_=0, to=9999,
                        width=5, font=Font(size=10),
                        textvariable=self.tieValues[idx]))
                self.tieFields[idx].grid(
                    row=idx+2, column=1, sticky=tk.W+tk.E+tk.N)
                container.rowconfigure(idx+2, weight=0)
            if idx >= len (self.orderFields):
                self.orderValues.append(NotifyNumericVar())
                self.orderValues[idx].trace('w', self._orderValueChangeNotify)
                self.orderFields.append(
                    NumericSpinbox(
                        container, from_=0, to=9999,
                        width=5, font=Font(size=10),
                        textvariable=self.orderValues[idx]))
                self.orderFields[idx].grid(
                    row=idx+2, column=2, sticky=tk.W+tk.E+tk.N)
                container.rowconfigure(idx+2, weight=0)
        self.labels.append(ttk.Label(container, text=' '))
        self.labels[-1].grid(row=1, column=1, pady=3)
        self.labels.append(ttk.Label(container, text=' '))
        self.labels[-1].grid(row=len(teams)+2, column=1)
        container.rowconfigure(1, weight=0)
        container.rowconfigure(len(teams)+2, weight=1)
        self.labels.append(ttk.Label(
            container,
            text='Kolejność rozstrzygania remisów w klasyfikacji ' + \
            'pobranej z bazy JFR Teamy',
            anchor=tk.E))
        self.labels[-1].grid(row=len(teams)+3, column=0, sticky=tk.N+tk.E)
        self.labels.append(ttk.Label(container, text='⬏', font=Font(size=20)))
        self.labels[-1].grid(
            row=len(teams)+3, column=1, sticky=tk.W+tk.N)
        container.rowconfigure(len(teams)+3, weight=1)
        self.labels.append(ttk.Label(
            container,
            text='Ręczne rozstrzyganie kolejności w klasyfikacji końcowej',
            anchor=tk.E))
        self.labels[-1].grid(row=len(teams)+4, column=0, columnspan=2, sticky=tk.N+tk.E)
        self.labels.append(ttk.Label(container, text='⬏', font=Font(size=20)))
        self.labels[-1].grid(
            row=len(teams)+4, column=2, sticky=tk.W+tk.N)
        container.rowconfigure(len(teams)+3, weight=1)

    def renderContent(self, container):
        container.columnconfigure(0, weight=1)
        (ttk.Label(container, text='Podgląd listy teamów')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W+tk.E)
        self.teamList = ttk.Treeview(
            container, show='headings',
            columns=['fullname','shortname','icon','position'],
            selectmode='browse')
        for col, heading in enumerate(
                [('Nazwa', 100), ('Skrócona nazwa', 100),
                 ('Ikona', 20), ('Poz. końc.', 20)]):
            self.teamList.heading(col, text=heading[0])
            if heading[1]:
                self.teamList.column(col, width=heading[1], stretch=True)
        self.container = container

    def _getTeams(self):
        return self.winfo_toplevel().getTeams()

    def getTieConfig(self):
        teams = self._getTeams()
        ties = [(teams[idx], val.get(default=0))
                for idx, val in enumerate(self.tieValues)]
        return [team[0][0] for team
                in sorted(ties, key=lambda t: t[1])
                if team[1] > 0]

    def setTieConfig(self, values):
        self._tieConfig = values
        self.refreshTeams(None)

    def _tieValueChangeNotify(self, *args):
        if not self._lockTieValues:
            self.winfo_toplevel().event_generate(
                '<<TieConfigChanged>>', when='tail')

    def _collectTieConfig(self, *args):
        if not self._lockTieValues:
            self._tieConfig = self.getTieConfig()

    def getOrderConfig(self):
        teams = self._getTeams()
        order = [(teams[idx], val.get(default=0))
                 for idx, val in enumerate(self.orderValues)]
        return [team[0][0] for team
                in sorted(order, key=lambda t: t[1])
                if team[1] > 0]

    def setOrderConfig(self, values):
        self._orderConfig = values
        self.refreshTeams(None)

    def _orderValueChangeNotify(self, *args):
        if not self._lockOrderValues:
            self.winfo_toplevel().event_generate(
                '<<OrderConfigChanged>>', when='tail')

    def _collectOrderConfig(self, *args):
        if not self._lockOrderValues:
            self._orderConfig = self.getOrderConfig()

    def refreshTeams(self, event):
        self._lockTieValues = True
        self._lockOrderValues = True
        teams = self._getTeams()
        self.setTeams(self.container, teams)
        for tidx, team in enumerate(teams):
            self.tieValues[tidx].set(0)
            for idx, tie in enumerate(self._tieConfig):
                if team[0] == tie:
                    self.tieValues[tidx].set(idx+1)
                    break
            for idx, order in enumerate(self._orderConfig):
                if isinstance(order, int):
                    if tidx+1 == order:
                        self.orderValues[tidx].set(idx+1)
                        break
                else:
                    if team[0] == order:
                        self.orderValues[tidx].set(idx+1)
                        break
        self._lockOrderValues = False
        self._lockTieValues = False


__all__ = ['TeamSettingsFrame', 'TeamAliasFrame', 'TeamPreviewFrame']
