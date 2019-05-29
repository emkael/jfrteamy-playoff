#coding=utf-8

import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
import tkMessageBox

from ..frames import RepeatableFrame, WidgetRepeater, RepeatableEntry, getIntVal

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

class TeamManualSettingsFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent()

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

class TeamSelectionFrame(tk.Frame):
    def __init__(self, master, title='', teams=[],
                 selected=None, callback=None):
        tk.Frame.__init__(self, master=master)
        self.values = []
        self.renderContent(title, teams, selected)
        self.callback = callback

    def _save(self):
        if self.callback:
            self.callback(
                [idx+1 for idx, value
                 in enumerate(self.values) if value.get()])
        self.master.destroy()

    def renderContent(self, title, teams, selected):
        self.columnconfigure(1, weight=1)
        (ttk.Label(self, text=title)).grid(row=0, column=0, columnspan=2)
        row = 1
        for team in teams:
            (ttk.Label(self, text='[%d]' % (row))).grid(row=row, column=0)
            self.values.append(tk.IntVar())
            (ttk.Checkbutton(
                self, text=team[0],
                variable=self.values[row-1]
            )).grid(row=row, column=1, sticky=tk.W)
            if selected and selected(row-1, team):
                self.values[row-1].set(True)
            row += 1
        (ttk.Button(self, text='Zapisz', command=self._save)).grid(
            row=row, column=0, columnspan=2)


class TeamFetchSettingsFrame(tk.Frame):
    SOURCE_LINK = 0
    SOURCE_DB = 1

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent()

    def _changeNotify(self, *args):
        self.winfo_toplevel().event_generate(
            '<<TeamSettingsChanged>>', when='tail')

    def _setFinishingPositions(self, positions):
        self.finishingPositions = positions
        self.finishingPositionsBtn.configure(
            text='[wybrano: %d]' % (len(self.finishingPositions)))
        self._changeNotify(None)

    def _chooseFinishingPositions(self):
        if not self.master.teams:
            tkMessageBox.showerror(
                'Wybór teamów', 'W turnieju nie ma teamów do wyboru')
            self._setFinishingPositions([])
        else:
            dialog = tk.Toplevel(self)
            selectionFrame = TeamSelectionFrame(
                dialog, title='Wybierz teamy, które zakończyły rozgrywki ' + \
                'na swojej pozycji:',
                teams=self.master.teams,
                selected=lambda idx, team: idx+1 in self.finishingPositions,
                callback=self._setFinishingPositions)
            selectionFrame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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

    def renderContent(self):
        (ttk.Label(self, text=' ')).grid(row=0, column=0, rowspan=2)

        self.fetchSource = tk.IntVar()
        self.fetchSource.set(self.SOURCE_LINK)
        (ttk.Radiobutton(
            self, text='Baza danych',
            variable=self.fetchSource, value=self.SOURCE_DB)).grid(
                row=0, column=1, columnspan=2, sticky=tk.W)
        self.fetchDB = tk.StringVar()
        self.fetchDB.trace('w', self._changeNotify)
        (ttk.OptionMenu(self, self.fetchDB, '')).grid(
            row=0, column=3, sticky=tk.W+tk.E)

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
        self.finishingPositionsBtn = ttk.Button(
            self, command=self._chooseFinishingPositions)
        self.finishingPositionsBtn.grid(row=3, column=3, sticky=tk.W)
        self._setFinishingPositions([])

class TeamSettingsFrame(tk.Frame):
    FORMAT_FETCH = 0
    FORMAT_MANUAL = 1

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent()

    def _setPanelState(self, frame, state):
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame):
                self._setPanelState(child, state)
            else:
                child.configure(state=state)

    def _enablePanels(self, *args):
        panels = {self.FORMAT_FETCH: self.fetchSettingsFrame,
                  self.FORMAT_MANUAL: self.manualSettingsFrame}
        for value, panel in panels.iteritems():
            self._setPanelState(
                frame=panel,
                state=tk.NORMAL \
                if self.teamFormat.get()==value else tk.DISABLED)

    def _changeNotify(self, *args):
        self.winfo_toplevel().event_generate(
            '<<TeamSettingsChanged>>', when='tail')

    def setTeams(self, event):
        self.teams = self.winfo_toplevel().getTeams()

    def renderContent(self):
        self.teamFormat = tk.IntVar()
        self.teamFormat.trace('w', self._enablePanels)
        self.teamFormat.trace('w', self._changeNotify)

        (ttk.Radiobutton(
            self, text='Pobierz z JFR Teamy:',
            variable=self.teamFormat, value=self.FORMAT_FETCH)).grid(
                row=0, column=0, sticky=tk.W)

        self.fetchSettingsFrame = TeamFetchSettingsFrame(self)
        self.fetchSettingsFrame.grid(row=1, column=0, sticky=tk.W+tk.E)

        (ttk.Separator(
            self, orient=tk.HORIZONTAL)).grid(
                row=2, column=0, sticky=tk.W+tk.E)

        (ttk.Radiobutton(
            self, text='Ustaw ręcznie:',
            variable=self.teamFormat, value=self.FORMAT_MANUAL)).grid(
                row=3, column=0, sticky=tk.W+tk.E)

        self.manualSettingsFrame = TeamManualSettingsFrame(self)
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
        self.teamName.set('')
        self.teamList = ttk.OptionMenu(self, self.teamName, '', *options)
        self.teamList.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N)

    def getValue(self):
        return (
            self.teamName.get().strip(),
            [val.strip() for val in self.names.getValue()])

    def refreshTeams(self, event):
        oldName = self.teamName.get()
        options = [team[0] for team in self.winfo_toplevel().getTeams()]
        self.teamList.destroy()
        self._createList(options)
        if oldName in options:
            self.teamName.set(oldName)

class TeamAliasFrame(tk.Frame):
    def __init__(self, *args, **kwags):
        tk.Frame.__init__(self, *args, **kwags)
        self.renderContent()

    def renderContent(self):
        self.columnconfigure(0, weight=1)
        (ttk.Label(self, text='Aliasy teamów')).grid(
            row=0, column=0, sticky=tk.W+tk.E)
        self.repeater = WidgetRepeater(self, TeamAliasRow)
        self.repeater.grid(row=1, column=0, sticky=tk.W+tk.E)

    def getConfig(self):
        return {val[0]: val[1] for val in self.repeater.getValue() if val[0]}

class TeamPreviewFrame(tk.Frame):
    def __init__(self, *args, **kwags):
        tk.Frame.__init__(self, *args, **kwags)
        self.tieValues = []
        self.tieFields = []
        self.labels = []
        self.renderContent()
        self.winfo_toplevel().bind(
            '<<TeamListChanged>>', self.refreshTeams, add='+')

    def setTeams(self, teams):
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
            self.teamList.insert('', tk.END, values=team, tag=idx)
            if idx >= len(self.tieFields):
                self.tieValues.append(tk.StringVar())
                self.tieFields.append(
                    tk.Spinbox(
                        self, from_=0, to=9999, width=5, font=Font(size=10),
                        textvariable=self.tieValues[idx]))
                self.tieFields[idx].grid(
                    row=idx+2, column=1, sticky=tk.W+tk.E+tk.N)
                self.rowconfigure(idx+2, weight=0)
        self.labels.append(ttk.Label(self, text=' '))
        self.labels[-1].grid(row=1, column=1, pady=3)
        self.labels.append(ttk.Label(self, text=' '))
        self.labels[-1].grid(row=len(teams)+2, column=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(len(teams)+2, weight=1)
        self.labels.append(ttk.Label(
            self,
            text='Kolejność rozstrzygania remisów w klasyfikacji ' + \
            'pobranej z bazy JFR Teamy',
            anchor=tk.E))
        self.labels[-1].grid(row=len(teams)+3, column=0, sticky=tk.E)
        self.labels.append(ttk.Label(self, text='⬏', font=Font(size=20)))
        self.labels[-1].grid(
            row=len(teams)+3, column=1, sticky=tk.W+tk.N)
        self.rowconfigure(len(teams)+3, weight=1)

    def renderContent(self):
        self.columnconfigure(0, weight=1)
        (ttk.Label(self, text='Podgląd listy teamów')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W+tk.E)
        self.teamList = ttk.Treeview(
            self, show='headings',
            columns=['fullname','shortname','icon','position'],
            selectmode='browse')
        for col, heading in enumerate(
                [('Nazwa', 100), ('Skrócona nazwa', 100),
                 ('Ikona', 20), ('Poz. końc.', 20)]):
            self.teamList.heading(col, text=heading[0])
            if heading[1]:
                self.teamList.column(col, width=heading[1], stretch=True)

        self.setTeams([])

    def getTieConfig(self):
        ties = [getIntVal(val, 0) for val in self.tieValues]
        if len(ties) and max(ties) == 0:
            return None
        return ties

    def refreshTeams(self, event):
        self.setTeams(self.winfo_toplevel().getTeams())

__all__ = ['TeamSettingsFrame', 'TeamAliasFrame', 'TeamPreviewFrame']
