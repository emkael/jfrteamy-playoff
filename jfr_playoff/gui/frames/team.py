#coding=utf-8

import tkinter as tk
from tkinter.font import Font
from tkinter import ttk

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, RepeatableEntry
from ..frames import SelectionButton, SelectionFrame, RefreshableOptionMenu
from ..frames import getIntVal, setPanelState

class ManualTeamRow(RepeatableFrame):
    def renderContent(self):
        self.fullname = tk.StringVar()
        fullnameField = ttk.Entry(self, width=20, textvariable=self.fullname)
        fullnameField.grid(row=0, column=0)
        self.shortname = tk.StringVar()
        shortnameField = ttk.Entry(self, width=20, textvariable=self.shortname)
        shortnameField.grid(row=0, column=1)
        self.flag = tk.StringVar()
        flagField = ttk.Entry(self, width=10, textvariable=self.flag)
        flagField.grid(row=0, column=2)
        self.position = tk.StringVar()
        positionField = ttk.Entry(self, width=10, textvariable=self.position)
        positionField.grid(row=0, column=3)
        for var in [self.fullname, self.shortname, self.flag, self.position]:
            var.trace('w', self._changeNotify)
        self._changeNotify(None)

    def getValue(self):
        flag = self.flag.get().strip()
        position = getIntVal(self.position, None)
        return [
            self.fullname.get().strip(), self.shortname.get().strip(),
            flag if len(flag) else None, position
        ]

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

class TeamSelectionFrame(SelectionFrame):
    def renderOption(self, container, option, idx):
        (ttk.Label(container, text='[%d]' % (idx+1))).grid(
            row=idx+1, column=0)
        (ttk.Checkbutton(
            container, text=option[0],
            variable=self.values[idx]
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
        teams = {}
        if self.fetchSource.get() == self.SOURCE_LINK:
            teams['link'] = self.fetchLink.get()
        elif self.fetchSource.get() == self.SOURCE_DB:
            teams['database'] = self.fetchDB.get()
        if len(self.finishingPositions):
            teams['final_positions'] = self.finishingPositions
        maxTeams = getIntVal(self.fetchLimit)
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
        (ttk.Label(self, text=' ')).grid(row=0, column=0, rowspan=2)

        self.fetchSource = tk.IntVar()
        self.fetchSource.set(self.SOURCE_LINK)
        self.fetchSource.trace('w', self._sourceChange)
        (ttk.Radiobutton(
            self, text='Baza danych',
            variable=self.fetchSource, value=self.SOURCE_DB)).grid(
                row=0, column=1, columnspan=2, sticky=tk.W)
        self.fetchDB = tk.StringVar()
        self.fetchDB.trace('w', self._changeNotify)
        self.fetchDBField = DBSelectionField(
            self, self.fetchDB, self.fetchDB.get())
        self.fetchDBField.grid(row=0, column=3, sticky=tk.W+tk.E)

        (ttk.Radiobutton(
            self, text='Strona wyników',
            variable=self.fetchSource, value=self.SOURCE_LINK)).grid(
                row=1, column=1, columnspan=2, sticky=tk.W)
        self.link = tk.StringVar()
        self.link.set('')
        self.link.trace('w', self._changeNotify)
        self.fetchLink = ttk.Entry(self, width=20, textvariable=self.link)
        self.fetchLink.grid(row=1, column=3)

        (ttk.Label(self, text='Pobierz do ')).grid(
            row=2, column=0, columnspan=2, sticky=tk.W)
        self.fetchLimit = tk.StringVar()
        self.fetchLimit.set(0)
        self.fetchLimit.trace('w', self._changeNotify)
        (tk.Spinbox(
            self, from_=0, to=9999, width=5, justify=tk.RIGHT,
            textvariable=self.fetchLimit)).grid(
                row=2, column=2, sticky=tk.W)
        (ttk.Label(self, text=' miejsca (0 = wszystkie)')).grid(
            row=2, column=3, sticky=tk.W+tk.E)

        (ttk.Label(self, text='Pozycje końcowe: ')).grid(
            row=3, column=0, columnspan=3, sticky=tk.W+tk.E)
        finishingPositionsBtn = TeamSelectionButton(
            self, callback=self._setFinishingPositions,
            prompt='Wybierz teamy, które zakończyły rozgrywki ' + \
            'na swojej pozycji:',
            dialogclass=TeamSelectionFrame)
        finishingPositionsBtn.grid(row=3, column=3, sticky=tk.W)
        finishingPositionsBtn.setPositions([])

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
        self.teamFormat = tk.IntVar()
        self.teamFormat.trace('w', self._enablePanels)
        self.teamFormat.trace('w', self._changeNotify)

        (ttk.Radiobutton(
            container, text='Pobierz z JFR Teamy:',
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

        self.teamFormat.set(self.FORMAT_MANUAL)
        self.teams = []
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.setTeams, add='+')

    def getConfig(self):
        if self.teamFormat.get() == self.FORMAT_MANUAL:
            return self.manualSettingsFrame.getTeams()
        elif self.teamFormat.get() == self.FORMAT_FETCH:
            return self.fetchSettingsFrame.getTeams()
        return []

class TeamList(RefreshableOptionMenu):
    def __init__(self, *args, **kwargs):
        RefreshableOptionMenu.__init__(self, *args, **kwargs)
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.refreshOptions, add='+')
        self.configure(width=10)

    def getOptions(self):
        return [team[0] for team in self.winfo_toplevel().getTeams()]

class TeamAliasRow(RepeatableFrame):
    def renderContent(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.teamName = tk.StringVar()
        (TeamList(self, self.teamName, self.teamName.get())).grid(
            row=0, column=0, sticky=tk.W+tk.E+tk.N)
        self.names = WidgetRepeater(self, RepeatableEntry)
        self.names.grid(row=0, column=1, sticky=tk.W+tk.E)

    def getValue(self):
        return (
            self.teamName.get().strip(),
            [val.strip() for val in self.names.getValue()])


class TeamAliasFrame(ScrollableFrame):
    def renderContent(self, container):
        container.columnconfigure(0, weight=1)
        (ttk.Label(container, text='Aliasy teamów')).grid(
            row=0, column=0, sticky=tk.W+tk.E)
        self.repeater = WidgetRepeater(container, TeamAliasRow)
        self.repeater.grid(row=1, column=0, sticky=tk.W+tk.E)

    def getConfig(self):
        return {val[0]: val[1] for val in self.repeater.getValue() if val[0]}

class TeamPreviewFrame(ScrollableFrame):
    def __init__(self, *args, **kwags):
        self.tieValues = []
        self.tieFields = []
        self.labels = []
        ScrollableFrame.__init__(self, *args, **kwags)
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.refreshTeams, add='+')

    def setTeams(self, container, teams):
        self.teamList.grid(
            row=1, column=0, rowspan=len(teams)+2, sticky=tk.W+tk.E+tk.N+tk.S)
        self.tieValues = self.tieValues[0:len(teams)]
        for idx in range(len(teams), len(self.tieFields)):
            self.tieFields[idx].destroy()
        self.tieFields = self.tieFields[0:len(teams)]
        for label in self.labels:
            label.destroy()
        self.teamList.delete(*self.teamList.get_children())
        for idx, team in enumerate(teams):
            if len(team) > 2 and team[2] is None:
                team[2] = ''
            self.teamList.insert('', tk.END, values=team, tag=idx)
            if idx >= len(self.tieFields):
                self.tieValues.append(tk.StringVar())
                self.tieFields.append(
                    tk.Spinbox(
                        container, from_=0, to=9999,
                        width=5, font=Font(size=10),
                        textvariable=self.tieValues[idx]))
                self.tieFields[idx].grid(
                    row=idx+2, column=1, sticky=tk.W+tk.E+tk.N)
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

        self.setTeams(self.container, [])

    def getTieConfig(self):
        ties = [getIntVal(val, 0) for val in self.tieValues]
        if len(ties) and max(ties) == 0:
            return None
        return ties

    def refreshTeams(self, event):
        self.setTeams(self.container, self.winfo_toplevel().getTeams())

__all__ = ['TeamSettingsFrame', 'TeamAliasFrame', 'TeamPreviewFrame']
