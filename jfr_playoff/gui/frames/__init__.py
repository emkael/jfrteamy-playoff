#coding=utf-8

import tkinter as tk
from tkinter import ttk

def getIntVal(widget, default=0):
    try:
        return int(widget.get().strip())
    except ValueError:
        return default

def setPanelState(frame, state):
    for child in frame.winfo_children():
        if isinstance(child, tk.Frame):
            setPanelState(child, state)
        else:
            child.configure(state=state)

class WidgetRepeater(tk.Frame):
    def __init__(self, master, widgetClass, headers=None, classParams=None,
                 *args, **kwargs):
        if not issubclass(widgetClass, RepeatableFrame):
            raise AttributeError(
                'WidgetRepeater widget must be a RepeatableFrame')
        tk.Frame.__init__(self, master, **kwargs)
        self.widgetClass = widgetClass
        self.widgetClassParams = classParams
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
        if self.widgetClassParams is not None:
            widget.configureContent(**self.widgetClassParams)
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

    def getValue(self):
        return [widget.getValue() for widget in self.widgets
                if isinstance(widget, self.widgetClass)]

class RepeatableFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent()

    def renderContent(self):
        pass

    def configureContent(self, **kwargs):
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

    def configureContent(self, **kwargs):
        for param, value in kwargs.iteritems():
            self.field[param] = value

    def getValue(self):
        return self.value.get()

    def setValue(self, value):
        return self.value.set(value)

class ScrollableFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        vertical = False
        if 'vertical' in kwargs:
            vertical = kwargs['vertical']
            del kwargs['vertical']
        horizontal = False
        if 'horizontal' in kwargs:
            horizontal = kwargs['horizontal']
            del kwargs['horizontal']
        tk.Frame.__init__(self, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        if horizontal:
            hscroll = tk.Scrollbar(
                self, orient=tk.HORIZONTAL, command=canvas.xview)
            hscroll.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.configure(xscrollcommand=hscroll.set)
        if vertical:
            vscroll = tk.Scrollbar(
                self, orient=tk.VERTICAL, command=canvas.yview)
            vscroll.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=vscroll.set)
        frame = tk.Frame(canvas, borderwidth=0, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0,0), window=frame, anchor=tk.N+tk.W)
        frame.bind(
            '<Configure>',
            lambda ev: canvas.configure(scrollregion=canvas.bbox('all')))
        self.renderContent(frame)

    def renderContent(self, container):
        pass
