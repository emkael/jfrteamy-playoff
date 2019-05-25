#coding=utf-8

import tkinter as tk
from tkinter import ttk
import tkMessageBox

from ..frames import RepeatableFrame, WidgetRepeater, RepeatableEntry

class ManualTeamRow(RepeatableFrame):
    def renderContent(self):
        self.fullname = ttk.Entry(self, width=20)
        self.fullname.grid(row=0, column=0)
        self.shortname = ttk.Entry(self, width=20)
        self.shortname.grid(row=0, column=1)
        self.flag = ttk.Entry(self, width=10)
        self.flag.grid(row=0, column=2)
        self.position = ttk.Entry(self, width=10)
        self.position.grid(row=0, column=3)

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
        (WidgetRepeater(self, ManualTeamRow, headers=headers)).grid(
            row=1, column=0, columnspan=5)

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

    def _setFinishingPositions(self, positions):
        self.finishingPositions = positions
        self.finishingPositionsBtn.configure(
            text='[wybrano: %d]' % (len(self.finishingPositions)))

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


    def renderContent(self):
        (ttk.Label(self, text=' ')).grid(row=0, column=0, rowspan=2)

        self.fetchSource = tk.IntVar()
        self.fetchSource.set(self.SOURCE_LINK)
        (ttk.Radiobutton(
            self, text='Baza danych',
            variable=self.fetchSource, value=self.SOURCE_DB)).grid(
                row=0, column=1, columnspan=2, sticky=tk.W)
        self.fetchDB = tk.StringVar()
        (ttk.OptionMenu(self, self.fetchDB, '')).grid(
            row=0, column=3, sticky=tk.W+tk.E)

        (ttk.Radiobutton(
            self, text='Strona wyników',
            variable=self.fetchSource, value=self.SOURCE_LINK)).grid(
                row=1, column=1, columnspan=2, sticky=tk.W)
        self.fetchLink = ttk.Entry(self, width=20)
        self.fetchLink.grid(row=1, column=3)

        (ttk.Label(self, text='Pobierz do ')).grid(
            row=2, column=0, columnspan=2, sticky=tk.W)
        self.fetchLimit = tk.Spinbox(self, from_=0, value=0,
                                     width=5, justify=tk.RIGHT)
        self.fetchLimit.grid(row=2, column=2, sticky=tk.W)
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

    def setTeams(self, teams):
        self.teams = teams
        # emit event or sth

    def renderContent(self):
        self.teamFormat = tk.IntVar()
        self.teamFormat.trace('w', self._enablePanels)

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
        self.setTeams([])

class TeamAliasRow(RepeatableFrame):
    def renderContent(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.teamName = tk.StringVar()
        (ttk.OptionMenu(self, self.teamName, '')).grid(
            row=0, column=0, sticky=tk.W+tk.E+tk.N)
        self.names = WidgetRepeater(self, RepeatableEntry)
        self.names.grid(row=0, column=1, sticky=tk.W+tk.E)

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

class TeamPreviewFrame(tk.Frame):
    pass

__all__ = ['TeamSettingsFrame', 'TeamAliasFrame', 'TeamPreviewFrame']
