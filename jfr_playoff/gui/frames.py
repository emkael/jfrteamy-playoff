#coding=utf-8

import tkinter as tk
from tkinter import ttk
import tkMessageBox

class WidgetRepeater(tk.Frame):
    def __init__(self, master, widgetClass, headers=None, *args, **kwargs):
        if not issubclass(widgetClass, RepeatableFrame):
            raise AttributeError(
                'WidgetRepeater widget must be a RepeatableFrame')
        tk.Frame.__init__(self, master, **kwargs)
        self.widgetClass = widgetClass
        self.widgets = []
        self.headers = headers
        self.addButton = ttk.Button(
            self, text='[+]', width=5, command=self._addWidget)
        self.renderContent()

    def _findWidget(self, row, column):
        for children in self.children.values():
            info = children.grid_info()
            if info['row'] == str(row) and info['column'] == str(column):
                return children
        return None

    def _addWidget(self):
        removeButton = ttk.Button(
            self, text='[-]', width=5,
            command=lambda i=len(self.widgets): self._removeWidget(i))
        removeButton.grid(row=len(self.widgets), column=0)
        widget = self.widgetClass(self)
        self.widgets.append(widget)
        self._updateGrid()

    def _removeWidget(self, idx):
        self.widgets.pop(idx).destroy()
        self._findWidget(row=len(self.widgets), column=0).destroy()
        self._updateGrid()

    def _updateGrid(self):
        for idx, widget in enumerate(self.widgets):
            widget.grid(row=idx, column=1, sticky=tk.W+tk.E)
        self.addButton.grid(
            row=len(self.widgets), column=0, columnspan=1, sticky=tk.W)

    def _renderHeader(self):
        if self.headers:
            headerFrame = tk.Frame(self)
            for idx, header in enumerate(self.headers):
                headerFrame.columnconfigure(idx, weight=1)
                widget = header[0](headerFrame, **header[1])
                widget.grid(row=0, column=idx, sticky=tk.W+tk.E)
            self.widgets.append(headerFrame)
            (tk.Label(self, text=' ')).grid(row=0, column=0, sticky=tk.W+tk.E)

    def renderContent(self):
        self.columnconfigure(1, weight=1)
        self._renderHeader()
        self._updateGrid()

class RepeatableFrame(tk.Frame):
    def getValue(self):
        pass

    def setValue(self, value):
        pass

class ManualTeamRow(RepeatableFrame):
    def __init__(self, *args, **kwargs):
        RepeatableFrame.__init__(self, *args, **kwargs)
        self.renderContent()

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
