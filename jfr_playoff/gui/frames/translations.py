#coding=utf-8

import copy

import tkinter as tk
from tkinter import ttk

from ..frames import RepeatableFrame, WidgetRepeater, ScrollableFrame
from ...i18n import PLAYOFF_I18N_DEFAULTS

class TranslationRow(RepeatableFrame):
    def renderContent(self):
        self.key = tk.StringVar()
        (ttk.Entry(self, textvariable=self.key, width=40)).pack(
            side=tk.LEFT)
        self.value = tk.StringVar()
        (ttk.Entry(self, textvariable=self.value, width=80)).pack(
            side=tk.RIGHT)

    def setValue(self, value):
        self.key.set(value[0])
        self.value.set(value[1])

class TranslationConfigurationFrame(ScrollableFrame):

    def setTranslations(self, translations):
        translations = copy.copy(PLAYOFF_I18N_DEFAULTS)
        translations.update(translations)
        values = []
        for value in translations.iteritems():
            values.append(value)
        self.repeater.setValue(values)

    def renderContent(self, container):
        self.repeater = WidgetRepeater(container, TranslationRow)
        self.repeater.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.setTranslations({})

__all__ = ['TranslationConfigurationFrame']
