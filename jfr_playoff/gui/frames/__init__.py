#coding=utf-8

import tkinter as tk
from tkinter import ttk

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
        removeButton.grid(row=len(self.widgets), column=0, sticky=tk.N)
        widget = self.widgetClass(self)
        self.widgets.append(widget)
        self._updateGrid()

    def _removeWidget(self, idx):
        self.widgets.pop(idx).destroy()
        self._findWidget(row=len(self.widgets), column=0).destroy()
        self._updateGrid()

    def _updateGrid(self):
        for idx, widget in enumerate(self.widgets):
            widget.grid(row=idx, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        self.addButton.grid(
            row=len(self.widgets), column=0, columnspan=1, sticky=tk.W+tk.N)

    def _renderHeader(self):
        if self.headers:
            headerFrame = tk.Frame(self)
            for idx, header in enumerate(self.headers):
                headerFrame.columnconfigure(idx, weight=1)
                widget = header[0](headerFrame, **header[1])
                widget.grid(row=0, column=idx, sticky=tk.W+tk.E+tk.N)
            self.widgets.append(headerFrame)
            (tk.Label(self, text=' ')).grid(
                row=0, column=0, sticky=tk.W+tk.E+tk.N)

    def renderContent(self):
        self.columnconfigure(1, weight=1)
        self._renderHeader()
        self._updateGrid()

class RepeatableFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent()

    def renderContent(self):
        pass

    def getValue(self):
        pass

    def setValue(self, value):
        pass

class RepeatableEntry(RepeatableFrame):
    def renderContent(self):
        self.value = tk.StringVar()
        self.field = ttk.Entry(self, textvariable=self.value)
        self.field.pack(expand=True, fill=tk.BOTH)

    def getValue(self):
        return self.value.get()

    def setValue(self, value):
        return self.value.set(value)
