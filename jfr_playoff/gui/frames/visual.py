#coding=utf-8

import tkinter as tk
from tkinter import ttk

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, getIntVal

class VisualSettingsFrame(GuiFrame):
    def renderContent(self):
        (ttk.Label(self, text='Znaczniki pozycji:')).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        (ttk.Label(self, text='Wymiary tabelki meczu:')).grid(
            row=0, column=1, sticky=tk.W, pady=5)
        indicatorsFrame = tk.Frame(self)
        indicatorsFrame.grid(row=1, column=0, sticky=tk.W+tk.N, padx=10)
        dimensionsFrame = tk.Frame(self)
        dimensionsFrame.grid(row=1, column=1, sticky=tk.W+tk.N, padx=10)
        (ttk.Label(self, text='Nazwy teamów:')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        (ttk.Label(self, text='Separatory nazw teamów:')).grid(
            row=2, column=1, sticky=tk.W, pady=5)
        teamNamesFrame = tk.Frame(self)
        teamNamesFrame.grid(row=3, column=0, sticky=tk.W+tk.N, padx=10)
        separatorsFrame = tk.Frame(self)
        separatorsFrame.grid(row=3, column=1, sticky=tk.W+tk.N, padx=10)

        self._fieldsToEnable = []

        self.startingPositionIndicators = tk.IntVar()
        self.finishingPositionIndicators = tk.IntVar()
        (ttk.Checkbutton(
            indicatorsFrame, text='początkowych',
            variable=self.startingPositionIndicators)).grid(
                row=0, column=0, sticky=tk.W)
        (ttk.Checkbutton(
            indicatorsFrame, text='końcowych',
            variable=self.finishingPositionIndicators)).grid(
                row=1, column=0, sticky=tk.W)

        self.boxWidth = tk.IntVar()
        self.boxHeight = tk.IntVar()
        self.boxMargin = tk.IntVar()
        (tk.Spinbox(
            dimensionsFrame, width=5, justify=tk.RIGHT, from_=1, to=999,
            textvariable=self.boxWidth)).grid(
                row=0, column=0, sticky=tk.W)
        (ttk.Label(dimensionsFrame, text='x')).grid(row=0, column=1)
        (tk.Spinbox(
            dimensionsFrame, width=5, justify=tk.RIGHT, from_=1, to=999,
            textvariable=self.boxHeight)).grid(
                row=0, column=2, sticky=tk.W)
        (ttk.Label(dimensionsFrame, text='odstępy')).grid(
            row=1, column=0, columnspan=2, sticky=tk.E)
        (tk.Spinbox(
            dimensionsFrame, width=5, justify=tk.RIGHT, from_=1, to=999,
            textvariable=self.boxMargin)).grid(
                row=1, column=2, sticky=tk.W)

        self.shortenTeamNames = tk.IntVar()
        self.teamNameLength = tk.IntVar()
        self.teamNameEllipsis = tk.StringVar()
        self.teamNamePredict = tk.IntVar()
        self.teamNamePlaceholder = tk.StringVar()
        self.teamNameSortPredictions = tk.IntVar()
        (ttk.Checkbutton(
            teamNamesFrame, text='skracaj do',
            variable=self.shortenTeamNames)).grid(
                row=0, column=0, columnspan=2)
        nameLength = tk.Spinbox(
            teamNamesFrame, width=5, justify=tk.RIGHT, from_=1, to=999,
            textvariable=self.teamNameLength)
        nameLength.grid(row=0, column=2, sticky=tk.W)
        lengthLabel = ttk.Label(teamNamesFrame, text='znaków')
        lengthLabel.grid(row=0, column=3, sticky=tk.W)
        ellipsisLabel = ttk.Label(teamNamesFrame, text='znacznik:')
        ellipsisLabel.grid(row=1, column=0, columnspan=2, sticky=tk.E)
        nameEllipsis = ttk.Entry(
            teamNamesFrame, width=5,
            textvariable=self.teamNameEllipsis)
        nameEllipsis.grid(row=1, column=2, sticky=tk.W)
        (ttk.Checkbutton(
            teamNamesFrame,
            text='przewiduj na podstawie trwających meczów',
            variable=self.teamNamePredict)).grid(
                row=2, column=0, columnspan=5)
        placeholderLabel = ttk.Label(
            teamNamesFrame, text='etykieta nieznanych teamów')
        placeholderLabel.grid(row=3, column=1, columnspan=3, sticky=tk.W)
        namePlaceholder = ttk.Entry(
            teamNamesFrame, width=5,
            textvariable=self.teamNamePlaceholder)
        namePlaceholder.grid(row=3, column=4, sticky=tk.W)
        predictSort = ttk.Checkbutton(
            teamNamesFrame, text='wyświetlaj najpierw pewne teamy',
            variable=self.teamNameSortPredictions)
        predictSort.grid(row=4, column=1, columnspan=4, sticky=tk.W)
        self._fieldsToEnable.append(
            (self.shortenTeamNames,
             [nameLength, nameEllipsis, lengthLabel, ellipsisLabel]))
        self._fieldsToEnable.append(
            (self.teamNamePredict,
             [namePlaceholder, placeholderLabel, predictSort]))

        self.teamLabelSeparator = tk.StringVar()
        self.teamNameSeparator = tk.StringVar()
        self.teamNamePrefix = tk.StringVar()
        (ttk.Label(separatorsFrame, text=' ')).grid(row=0, column=0)
        (ttk.Label(separatorsFrame, text='w drabince (skrócone nazwy)')).grid(
            row=0, column=1, sticky=tk.E)
        (ttk.Entry(
            separatorsFrame, width=8,
            textvariable=self.teamLabelSeparator)).grid(
                row=0, column=2, sticky=tk.W)
        (ttk.Label(separatorsFrame, text='w "dymkach" (pełne nazwy)')).grid(
            row=1, column=1, sticky=tk.E)
        (ttk.Entry(
            separatorsFrame, width=8,
            textvariable=self.teamNameSeparator)).grid(
                row=1, column=2, sticky=tk.W)
        (ttk.Label(separatorsFrame, text='prefiks pełnych nazw')).grid(
            row=2, column=1, sticky=tk.E)
        (ttk.Entry(
            separatorsFrame, width=8,
            textvariable=self.teamNamePrefix)).grid(
                row=2, column=2, sticky=tk.W)

        self.boxWidth.set(250)
        self.boxHeight.set(80)
        self.boxMargin.set(60)
        self.teamNameLength.set(25)
        self.teamNameEllipsis.set('(...)')
        self.teamNamePlaceholder.set('??')
        self.teamNameSortPredictions.set(1)
        self.teamLabelSeparator.set(' / ')
        self.teamNameSeparator.set('<br />')
        self.teamNamePrefix.set('&nbsp;')

        for var, fields in self._fieldsToEnable:
            var.trace('w', self._enableFields)
        self._enableFields()

    def _enableFields(self, *args):
        for var, fields in self._fieldsToEnable:
            for field in fields:
                field.configure(state=tk.NORMAL if var.get() else tk.DISABLED)


class BoxPositionFrame(RepeatableFrame):
    def renderContent(self):
        self.match = tk.StringVar()
        self.vertical = tk.IntVar()
        self.horizontal = tk.IntVar()
        self.horizontal.set(-1)
        (ttk.OptionMenu(self, self.match)).grid(row=0, column=0)
        (ttk.Label(self, text=' w pionie:')).grid(row=0, column=1)
        (tk.Spinbox(
            self, textvariable=self.vertical, from_=0, to=9999,
            width=5, justify=tk.RIGHT)).grid(
                row=0, column=2)
        (ttk.Label(self, text=' w poziomie (-1 = automatyczna):')).grid(
                row=0, column=3)
        (tk.Spinbox(
            self, textvariable=self.horizontal, from_=-1, to=9999,
            width=5, justify=tk.RIGHT)).grid(
                row=0, column=4)

class BoxPositionsFrame(ScrollableFrame):
    def renderContent(self, container):
        (ttk.Label(container, text='Pozycje tabelek meczów:')).pack(
            side=tk.TOP, anchor=tk.W)
        (WidgetRepeater(container, BoxPositionFrame)).pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

__all__ = ['VisualSettingsFrame', 'BoxPositionsFrame']
