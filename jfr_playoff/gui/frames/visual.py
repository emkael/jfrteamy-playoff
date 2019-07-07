#coding=utf-8

import tkinter as tk
from tkinter import ttk
import tkColorChooser as tkcc

from ..frames import GuiFrame, RepeatableFrame, ScrollableFrame
from ..frames import WidgetRepeater, getIntVal
from ..frames import SelectionFrame, RefreshableOptionMenu
from ..frames.team import TeamSelectionButton

class VisualSettingsFrame(GuiFrame):
    DEFAULT_VALUES = {
        'width': 250,
        'height': 80,
        'margin': 60,
        'starting_position_indicators': 0,
        'finishing_position_indicators': 0,
        'team_boxes': {
            'label_length_limit': 25,
            'predict_teams': 1,
            'label_separator': ' / ',
            'label_placeholder': '??',
            'label_ellipsis': '(...)',
            'name_separator': '<br />',
            'name_prefix': '&nbsp;&nbsp;',
            'sort_eligible_first': 1
        }
    }

    def renderContent(self):
        self.startingPositionIndicators = tk.IntVar()
        self.finishingPositionIndicators = tk.IntVar()
        self.boxWidth = tk.IntVar()
        self.boxHeight = tk.IntVar()
        self.boxMargin = tk.IntVar()
        self.shortenTeamNames = tk.IntVar()
        self.teamNameLength = tk.IntVar()
        self.teamNameEllipsis = tk.StringVar()
        self.teamNamePredict = tk.IntVar()
        self.teamNamePlaceholder = tk.StringVar()
        self.teamNameSortPredictions = tk.IntVar()
        self.teamLabelSeparator = tk.StringVar()
        self.teamNameSeparator = tk.StringVar()
        self.teamNamePrefix = tk.StringVar()

        indicatorsFrame = ttk.LabelFrame(self, text='Znaczniki pozycji:')
        indicatorsFrame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        dimensionsFrame = ttk.LabelFrame(self, text='Wymiary tabelki meczu:')
        dimensionsFrame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        teamNamesFrame = ttk.LabelFrame(self, text='Nazwy teamów:')
        teamNamesFrame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        separatorsFrame = ttk.LabelFrame(self, text='Separatory nazw teamów:')
        separatorsFrame.grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

        self._fieldsToEnable = []

        (ttk.Checkbutton(
            indicatorsFrame, text='początkowych',
            variable=self.startingPositionIndicators)).grid(
                row=0, column=0, sticky=tk.W)
        (ttk.Checkbutton(
            indicatorsFrame, text='końcowych',
            variable=self.finishingPositionIndicators)).grid(
                row=1, column=0, sticky=tk.W)

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

        for var, fields in self._fieldsToEnable:
            var.trace('w', self._enableFields)
        self._enableFields()

        self.setValues({})

    def _enableFields(self, *args):
        for var, fields in self._fieldsToEnable:
            for field in fields:
                field.configure(state=tk.NORMAL if var.get() else tk.DISABLED)

    def setValues(self, values):
        default_values = self.DEFAULT_VALUES
        if 'team_boxes' in values:
            default_values['team_boxes'].update(values['team_boxes'])
            del values['team_boxes']
        default_values.update(values)
        values = default_values

        self.startingPositionIndicators.set(
            values['starting_position_indicators'])
        self.finishingPositionIndicators.set(
            values['finishing_position_indicators'])
        self.boxWidth.set(values['width'])
        self.boxHeight.set(values['height'])
        self.boxMargin.set(values['margin'])
        self.shortenTeamNames.set(
            values['team_boxes']['label_length_limit'] > 0)
        self.teamNameLength.set(values['team_boxes']['label_length_limit'])
        self.teamNameEllipsis.set(values['team_boxes']['label_ellipsis'])
        self.teamNamePredict.set(values['team_boxes']['predict_teams'])
        self.teamNamePlaceholder.set(values['team_boxes']['label_placeholder'])
        self.teamNameSortPredictions.set(
            values['team_boxes']['sort_eligible_first'])
        self.teamLabelSeparator.set(values['team_boxes']['label_separator'])
        self.teamNameSeparator.set(values['team_boxes']['name_separator'])
        self.teamNamePrefix.set(values['team_boxes']['name_prefix'])


class MatchList(RefreshableOptionMenu):
    def __init__(self, *args, **kwargs):
        RefreshableOptionMenu.__init__(self, *args, **kwargs)
        self.winfo_toplevel().bind(
            '<<MatchListChanged>>', self.refreshOptions, add='+')
        self.configure(width=10)

    def getLabel(self, match):
        return match.label

    def getValues(self):
        return self.winfo_toplevel().getMatches()

    def getVarValue(self, match):
        return unicode(match.getMatchID())


class BoxPositionFrame(RepeatableFrame):
    def renderContent(self):
        self.match = tk.StringVar()
        self.vertical = tk.IntVar()
        self.horizontal = tk.IntVar()
        self.matchBox = MatchList(self, self.match)
        self.matchBox.configure(width=20)
        self.matchBox.grid(row=0, column=0)
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
        self.setValue([])

    def setValue(self, value):
        if len(value) > 1:
            self.match.set(value[0])
            self.vertical.set(value[1])
            if len(value) > 2:
                self.horizontal.set(value[2])
            else:
                self.horizontal.set(-1)
        else:
            self.match.set('')
            self.vertical.set(0)
            self.horizontal.set(-1)

class BoxPositionsFrame(ScrollableFrame):
    def renderContent(self, container):
        (ttk.Label(container, text='Pozycje tabelek meczów:')).pack(
            side=tk.TOP, anchor=tk.W)
        self.positions = WidgetRepeater(container, BoxPositionFrame)
        self.positions.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

    def setValues(self, values):
        values = sorted(list(values.iteritems()), key=lambda v: int(v[0]))
        values_to_set = []
        for idx, val in enumerate(values):
            value = [val[0]]
            if isinstance(val[1], list):
                value += val[1]
            else:
                value.append(val[1])
            values_to_set.append(value)
        self.positions.setValue(values_to_set)

class LineStyle(GuiFrame):
    def _selectColour(self):
        colour = tkcc.askcolor(self._getColour())
        if colour is not None:
            self._setColour(colour[1])

    def _getColour(self):
        return self.colourBtn.cget('bg')

    def _setColour(self, colour):
        self.colourBtn.configure(bg=colour)

    def renderContent(self):
        (ttk.Label(self, text='kolor:')).grid(row=0, column=0)
        self.colourBtn = tk.Button(self, width=2, command=self._selectColour)
        self.colourBtn.grid(row=0, column=1)
        (ttk.Label(self, text='margines w poziomie:')).grid(row=0, column=2)
        self.hOffset = tk.StringVar()
        (tk.Spinbox(
            self, textvariable=self.hOffset, from_=-50, to=50,
            width=5, justify=tk.RIGHT)).grid(row=0, column=3)
        (ttk.Label(self, text='margines w pionie:')).grid(row=0, column=4)
        self.vOffset = tk.StringVar()
        (tk.Spinbox(
            self, textvariable=self.vOffset, from_=-50, to=50,
            width=5, justify=tk.RIGHT)).grid(row=0, column=5)

    def setValue(self, value):
        self._setColour(value[0])
        self.hOffset.set(value[1])
        self.vOffset.set(value[2])

class LineStylesFrame(GuiFrame):
    DEFAULT_VALUES = [
        ('winner', ('#00ff00', 5, -10),
         'Zwycięzcy meczów: '),
        ('loser', ('#ff0000', 20, 10),
         'Przegrani meczów: '),
        ('place_winner', ('#00dddd', 10, 2),
         'Pozycje startowe (wybierający): '),
        ('place_loser', ('#dddd00', 15, 9),
         'Pozycje startowe (wybierani): '),
        ('finish_winner', ('#00ff00', 5, -10),
         'Zwycięzcy meczów kończący rozgrywki: '),
        ('finish_loser', ('#ff0000', 20, 10),
         'Przegrani meczów kończący rozgrywki: ')
    ]

    def renderContent(self):
        self.lines = {}
        for idx, line in enumerate(self.DEFAULT_VALUES):
            self.lines[line[0]] = LineStyle(self)
            self.lines[line[0]].grid(row=idx+1, column=1, sticky=tk.W)
            (ttk.Label(self, text=line[2])).grid(
                row=idx+1, column=0, sticky=tk.E)
        (ttk.Label(self, text='Kolory linii')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W)

    def setValues(self, values):
        for line in self.DEFAULT_VALUES:
            value = list(line[1])
            for idx, key in enumerate(['colour', 'h_offset', 'v_offset']):
                key = '%s_%s' % (line[0], key)
                if key in values:
                    value[idx] = values[key]
            self.lines[line[0]].setValue(value)


class PositionsSelectionFrame(SelectionFrame):
    COLUMN_COUNT=10

    def __init__(self, *args, **kwargs):
        SelectionFrame.__init__(self, *args, **kwargs)
        self.winfo_toplevel().geometry(
            '%dx%d' % (
                self.COLUMN_COUNT * 40,
                (len(self.options) / self.COLUMN_COUNT + 2) * 25 + 30
            ))

    def renderHeader(self, container):
        (ttk.Label(container, text=self.title)).grid(
            row=0, column=0, columnspan=self.COLUMN_COUNT, sticky=tk.W)

    def renderOption(self, container, option, idx):
        (ttk.Checkbutton(
            container, text=str(self._mapValue(idx, option)),
            variable=self.values[self._mapValue(idx, option)]
        )).grid(
            row=(idx/self.COLUMN_COUNT)+1, column=idx%self.COLUMN_COUNT,
            sticky=tk.W)

class PositionStyleFrame(RepeatableFrame):
    def _setPositions(self, values):
        self.positions = values

    def renderContent(self):
        self.name = tk.StringVar()
        self.description = tk.StringVar()

        self.columnconfigure(1, weight=1)
        self.columnconfigure(5, weight=1)

        (ttk.Label(self, text='Styl:')).grid(row=0, column=0)
        (ttk.Entry(self, textvariable=self.name)).grid(
            row=0, column=1, sticky=tk.W+tk.E)

        (ttk.Label(self, text='Pozycje końcowe:')).grid(row=0, column=2)
        self.positionBtn = TeamSelectionButton(
            self, prompt='Wybierz pozycje końcowe:',
            dialogclass=PositionsSelectionFrame,
            callback=self._setPositions)
        self.positionBtn.grid(row=0, column=3)

        (ttk.Label(self, text='Opis w legendzie:')).grid(row=0, column=4)
        (ttk.Entry(self, textvariable=self.description)).grid(
            row=0, column=5, sticky=tk.W+tk.E)

        self.setValue({})

    def setValue(self, value):
        self.name.set(value['class'] if 'class' in value else '')
        self.positionBtn.setPositions(
            value['positions'] if 'positions' in value else [])
        self.description.set(value['caption'] if 'caption' in value else '')


class PositionStylesFrame(ScrollableFrame):
    def renderContent(self, container):
        (ttk.Label(container, text='Klasyfikacja końcowa')).pack(
            side=tk.TOP, anchor=tk.W)
        self.styles = WidgetRepeater(container, PositionStyleFrame)
        self.styles.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def setValues(self, values):
        self.styles.setValue(values)

__all__ = ['VisualSettingsFrame', 'BoxPositionsFrame', 'LineStylesFrame', 'PositionStylesFrame']
