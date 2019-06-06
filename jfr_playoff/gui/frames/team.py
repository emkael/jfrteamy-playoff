#coding=utf-8

import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
import tkMessageBox

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, RepeatableEntry
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

class TeamSelectionFrame(ScrollableFrame):
    def __init__(self, master, title='', teams=[],
                 selected=None, callback=None, *args, **kwargs):
        self.values = []
        self.title = title
        self.teams = teams
        self.selected = selected
        self.callback = callback
        ScrollableFrame.__init__(self, master=master, *args, **kwargs)
        (ttk.Button(master, text='Zapisz', command=self._save)).pack(
            side=tk.BOTTOM, fill=tk.Y)

    def _save(self):
        if self.callback:
            self.callback(
                [idx+1 for idx, value
                 in enumerate(self.values) if value.get()])
        self.master.destroy()

    def renderHeader(self, container):
        container.columnconfigure(1, weight=1)
        (ttk.Label(container, text=self.title)).grid(
            row=0, column=0, columnspan=2)

    def renderTeam(self, container, team, idx):
        (ttk.Label(container, text='[%d]' % (idx+1))).grid(
            row=idx+1, column=0)
        (ttk.Checkbutton(
            container, text=team[0],
            variable=self.values[idx]
        )).grid(row=idx+1, column=1, sticky=tk.W)

    def renderContent(self, container):
        self.renderHeader(container)
        for idx, team in enumerate(self.teams):
            self.values.append(tk.IntVar())
            self.renderTeam(container, team, idx)
            if self.selected and self.selected(idx, team):
                self.values[idx].set(True)

class TeamSelectionButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        for arg in ['callback', 'prompt', 'dialogclass']:
            setattr(self, arg, kwargs[arg] if arg in kwargs else None)
            if arg in kwargs:
                del kwargs[arg]
        kwargs['command'] = self._choosePositions
        if self.dialogclass is None:
            self.dialogclass = TeamSelectionFrame
        if self.prompt is None:
            self.prompt = 'Wybierz teamy:'
        ttk.Button.__init__(self, *args, **kwargs)
        self.setPositions([])

    def setPositions(self, values):
        self.selected = values
        self.configure(
            text='[wybrano: %d]' % (len(values)))
        if self.callback is not None:
            self.callback(values)

    def _choosePositions(self):
        teams = self.winfo_toplevel().getTeams()
        if not len(teams):
            tkMessageBox.showerror(
                'Wybór teamów', 'W turnieju nie ma teamów do wyboru')
            self._setFinishingPositions([])
        else:
            dialog = tk.Toplevel(self)
            dialog.title('Wybór teamów')
            selectionFrame = self.dialogclass(
                dialog, title=self.prompt,
                teams=teams,
                selected=lambda idx, team: idx+1 in self.selected,
                callback=self.setPositions, vertical=True)
            selectionFrame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


class DBSelectionField(ttk.OptionMenu):
    def setOptions(self, values):
        if self._variable.get() not in values:
            self._variable.set('')
        menu = self['menu']
        menu.delete(0, tk.END)
        for item in values:
            menu.add_command(
                label=item, command=tk._setit(self._variable, item))

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

    def _onDBListChange(self, *args):
        self.fetchDBField.setOptions(self.winfo_toplevel().getDBs())

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
        self.winfo_toplevel().bind(
            '<<DBListChanged>>', self._onDBListChange, add='+')
        self.fetchDBField.setOptions([])

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
            'na swojej pozycji:')
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

class TeamAliasRow(RepeatableFrame):
    def renderContent(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.teamName = tk.StringVar()
        self._createList([])
        self.names = WidgetRepeater(self, RepeatableEntry)
        self.names.grid(row=0, column=1, sticky=tk.W+tk.E)
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.refreshTeams, add='+')
        self.refreshTeams(None)

    def _createList(self, options):
        if self.teamName.get() not in options:
            self.teamName.set('')
        self.teamList = ttk.OptionMenu(
            self, self.teamName, self.teamName.get(), *options)
        self.teamList.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N)

    def getValue(self):
        return (
            self.teamName.get().strip(),
            [val.strip() for val in self.names.getValue()])

    def refreshTeams(self, event):
        options = [team[0] for team in self.winfo_toplevel().getTeams()]
        self.teamList.destroy()
        self._createList(options)

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
            if team[2] is None:
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
