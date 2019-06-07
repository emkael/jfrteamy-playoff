#coding=utf-8

import tkinter as tk
from tkinter.font import Font
from tkinter import ttk

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, RepeatableEntry, getIntVal
from ..frames.team import DBSelectionField

class SwissSettingsFrame(RepeatableFrame):
    SOURCE_LINK = 0
    SOURCE_DB = 1

    def _onDBListChange(self, *args):
        self.fetchDBField.setOptions(self.winfo_toplevel().getDBs())

    def _setPositionInfo(self, *args):
        tournamentFrom = getIntVal(self.setFrom, default=1)
        tournamentTo = min(
            getIntVal(self.setTo, default=1) \
            if self.setToEnabled.get() else 9999,
            len(self.winfo_toplevel().getTeams()))
        swissFrom = getIntVal(self.fetchFrom, default=1)
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
        (ttk.Label(self, text='Źródło danych:')).grid(
            row=0, column=0, sticky=tk.W)
        self.source = tk.IntVar()
        (ttk.Radiobutton(
            self, text='Baza danych',
            variable=self.source, value=self.SOURCE_DB)).grid(
                row=1, column=0, sticky=tk.W)
        self.fetchDB = tk.StringVar()
        self.fetchDBField = DBSelectionField(
            self, self.fetchDB, self.fetchDB.get())
        self.fetchDBField.grid(row=1, column=1, sticky=tk.W+tk.E)
        self.winfo_toplevel().bind(
            '<<DBListChanged>>', self._onDBListChange, add='+')
        (ttk.Radiobutton(
            self, text='Strona turnieju',
            variable=self.source, value=self.SOURCE_LINK)).grid(
                row=2, column=0, sticky=tk.W)
        self.fetchLink = tk.StringVar()
        (ttk.Entry(self, textvariable=self.fetchLink, width=20)).grid(
            row=2, column=1, sticky=tk.W+tk.E)

        (ttk.Separator(self, orient=tk.HORIZONTAL)).grid(
            row=3, column=0, columnspan=6, sticky=tk.E+tk.W)

        (ttk.Label(
            self, text='Ustaw od miejsca: ')).grid(
                row=4, column=0, sticky=tk.E)
        self.setFrom = tk.StringVar()
        (tk.Spinbox(
            self, textvariable=self.setFrom,
            from_=1, to=999, width=5)).grid(
                row=4, column=1, sticky=tk.W)
        self.setToEnabled = tk.IntVar()
        (ttk.Checkbutton(
            self, variable=self.setToEnabled,
            text='Ustaw do miejsca: ')).grid(
                row=5, column=0, sticky=tk.E)
        self.setTo = tk.StringVar()
        (tk.Spinbox(
            self, textvariable=self.setTo,
            from_=1, to=999, width=5)).grid(
                row=5, column=1, sticky=tk.W)
        self.fetchFromEnabled = tk.IntVar()
        (ttk.Checkbutton(
            self, variable=self.fetchFromEnabled,
            text='Pobierz od miejsca: ')).grid(
                row=6, column=0, sticky=tk.E)
        self.fetchFrom = tk.StringVar()
        (tk.Spinbox(
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
        self.linkLabel = tk.StringVar()
        (ttk.Entry(self, textvariable=self.linkLabel, width=20)).grid(
            row=8, column=1, sticky=tk.W)
        (ttk.Label(self, text='(domyślnie: "Turniej o #. miejsce")')).grid(
            row=8, column=2, sticky=tk.W)

        (ttk.Label(self, text='Względna ścieżka linku do swissa:')).grid(
            row=1, column=2)
        self.linkRelPath = tk.StringVar()
        (ttk.Entry(self, textvariable=self.linkRelPath, width=20)).grid(
            row=1, column=3)

        (ttk.Separator(self, orient=tk.HORIZONTAL)).grid(
            row=7, column=0, columnspan=6, sticky=tk.E+tk.W)
        (ttk.Separator(self, orient=tk.HORIZONTAL)).grid(
            row=9, column=0, columnspan=6, sticky=tk.E+tk.W)

        self._onDBListChange()
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


class SwissesFrame(ScrollableFrame):
    def renderContent(self, container):
        self.swisses = WidgetRepeater(container, SwissSettingsFrame)
        self.swisses.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

__all__ = ['SwissesFrame']
