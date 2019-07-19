#coding=utf-8

from functools import partial
import types

import tkinter as tk
from tkinter import ttk
import tkMessageBox

from ..variables import NotifyStringVar, NotifyIntVar, NotifyNumericVar

def setPanelState(frame, state):
    for child in frame.winfo_children():
        if isinstance(child, tk.Frame):
            setPanelState(child, state)
        else:
            child.configure(state=state)

class WidgetRepeater(tk.Frame):
    def __init__(self, master, widgetClass, headers=None, classParams=None,
                 *args, **kwargs):
        widgetList = widgetClass
        if not isinstance(widgetClass, list):
            widgetList = [widgetClass]
        for widget in widgetList:
            if not issubclass(widget, RepeatableFrame):
                raise AttributeError(
                    'WidgetRepeater widget must be a RepeatableFrame')
        tk.Frame.__init__(self, master, **kwargs)
        self.widgetClass = widgetClass
        self.widgetClassParams = classParams
        self.widgets = []
        self.headers = headers
        self.headerFrame = None
        self.addButton = ttk.Button(
            self, text='[+]', width=5, command=self._addWidget)
        self.renderContent()

    def _findWidget(self, row, column):
        for children in self.children.values():
            info = children.grid_info()
            if info['row'] == str(row) and info['column'] == str(column):
                return children
        return None

    def _createWidget(self, widgetClass, widgetClassParams=None):
        headeridx = int(self.headerFrame is not None)
        removeButton = ttk.Button(
            self, text='[-]', width=5,
            command=lambda i=len(self.widgets): self._removeWidget(i))
        removeButton.grid(
            row=len(self.widgets)+headeridx, column=0, sticky=tk.N)
        widget = widgetClass(self)
        if widgetClassParams is not None:
            widget.configureContent(**widgetClassParams)
        self.widgets.append(widget)
        self._updateGrid()

    def _handleWidgetSelection(self, selected):
        if selected < len(self.widgetClass):
            params = None
            if isinstance(self.widgetClassParams, list) and \
               selected < len(self.widgetClassParams):
                params = self.widgetClassParams[selected]
            self._createWidget(self.widgetClass[selected], params)

    def _widgetSelectionDialog(self):
        dialog = tk.Toplevel(self)
        dialog.title('Wybór elementu do dodania')
        dialog.geometry('%dx%d' % (300, len(self.widgetClass) * 20 + 30))
        dialog.grab_set()
        dialog.focus_force()
        frame = WidgetSelectionFrame(
            dialog, vertical=True,
            widgets=self.widgetClass, callback=self._handleWidgetSelection)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _addWidget(self):
        if isinstance(self.widgetClass, list):
            self._widgetSelectionDialog()
        else:
            self._createWidget(self.widgetClass, self.widgetClassParams)

    def _removeWidget(self, idx):
        self.widgets.pop(idx).destroy()
        self._findWidget(row=len(self.widgets), column=0).destroy()
        self._updateGrid()

    def _updateGrid(self):
        headeridx = int(self.headerFrame is not None)
        for idx, widget in enumerate(self.widgets):
            widget.grid(
                row=idx+headeridx, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        if self.headerFrame is not None:
            self.headerFrame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        self.addButton.grid(
            row=len(self.widgets)+headeridx, column=0, columnspan=1,
            sticky=tk.W+tk.N)

    def _renderHeader(self):
        if self.headers:
            self.headerFrame = tk.Frame(self)
            for idx, header in enumerate(self.headers):
                self.headerFrame.columnconfigure(idx, weight=1)
                widget = header[0](self.headerFrame, **header[1])
                widget.grid(row=0, column=idx, sticky=tk.W+tk.E+tk.N)
            (tk.Label(self, text=' ')).grid(
                row=0, column=0, sticky=tk.W+tk.E+tk.N)

    def renderContent(self):
        self.columnconfigure(1, weight=1)
        self._renderHeader()
        self._updateGrid()

    def getValue(self):
        return [widget.getValue() for widget in self.widgets]

    def _getParamsForWidgetClass(self, widgetClass):
        if not isinstance(self.widgetClass, list):
            return self.widgetClassParams
        if not isinstance(self.widgetClassParams, list):
            return self.widgetClassParams
        for idx, widget in enumerate(self.widgetClass):
            if widget == widgetClass:
                return self.widgetClassParams[idx]
        return None

    def setValue(self, values):
        for i, value in enumerate(values):
            typedWidget = isinstance(value, tuple) \
                and isinstance(value[0], (types.TypeType, types.ClassType))
            if i >= len(self.widgets):
                if typedWidget:
                    self._createWidget(
                        value[0], self._getParamsForWidgetClass(value[0]))
                else:
                    self._addWidget()
            self.widgets[i].setValue(value[1] if typedWidget else value)
        for idx in range(len(values), len(self.widgets)):
            self._removeWidget(len(self.widgets)-1)


class GuiFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent()

    def renderContent(self):
        pass

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

    @classmethod
    def info(cls):
        return cls.__name__

class RepeatableEntry(RepeatableFrame):
    def renderContent(self):
        self.value = NotifyStringVar()
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
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        if horizontal:
            hscroll = tk.Scrollbar(
                self, orient=tk.HORIZONTAL, command=self.canvas.xview)
            hscroll.pack(side=tk.BOTTOM, fill=tk.X)
            self.canvas.configure(xscrollcommand=hscroll.set)
        if vertical:
            vscroll = tk.Scrollbar(
                self, orient=tk.VERTICAL, command=self.canvas.yview)
            vscroll.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=vscroll.set)
        frame = tk.Frame(self.canvas, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvasFrame = self.canvas.create_window(
            (0,0), window=frame, anchor=tk.N+tk.W)
        frame.bind('<Configure>', self._onFrameConfigure)
        self.canvas.bind('<Configure>', self._onCanvasConfigure)
        self.bind('<Enter>', partial(self._setScroll, value=True))
        self.bind('<Leave>', partial(self._setScroll, value=False))
        self.renderContent(frame)

    def _setScroll(self, event, value):
        if value:
            self.bind_all('<MouseWheel>', self._onVscroll)
            self.bind_all('<Shift-MouseWheel>', self._onHscroll)
        else:
            self.unbind_all('<MouseWheel>')
            self.unbind_all('<Shift-MouseWheel>')

    def _onHscroll(self, event):
        self._onScroll(tk.X, -1 if event.delta > 0 else 1)

    def _onVscroll(self, event):
        self._onScroll(tk.Y, -1 if event.delta > 0 else 1)

    def _onScroll(self, direction, delta):
        getattr(
            self.canvas, '%sview' % (direction))(tk.SCROLL, delta, tk.UNITS)

    def _onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _onCanvasConfigure(self, event):
        self.canvas.itemconfig(self.canvasFrame, width=event.width)

    def renderContent(self, container):
        pass

class WidgetSelectionFrame(ScrollableFrame):
    def __init__(self, *args, **kwargs):
        self.widgets = []
        self.callback = None
        for var in ['widgets', 'callback']:
            if var in kwargs:
                setattr(self, var, kwargs[var])
                del kwargs[var]
        ScrollableFrame.__init__(self, *args, **kwargs)
        addBtn = ttk.Button(
            self.master, text='Dodaj', command=self._onConfirm)
        addBtn.pack(side=tk.BOTTOM)

    def renderContent(self, container):
        self.value = NotifyIntVar()
        for idx, widget in enumerate(self.widgets):
            (ttk.Radiobutton(
                container, variable=self.value, value=idx,
                text=widget.info())).pack(side=tk.TOP, fill=tk.X, expand=True)

    def _onConfirm(self):
        if self.callback is not None:
            self.callback(self.value.get())
        self.winfo_toplevel().destroy()

class SelectionButton(ttk.Button):
    @property
    def defaultPrompt(self):
        pass

    @property
    def title(self):
        pass

    @property
    def errorMessage(self):
        pass

    def getOptions(self):
        pass

    def __init__(self, *args, **kwargs):
        for arg in ['callback', 'prompt', 'dialogclass']:
            setattr(self, arg, kwargs[arg] if arg in kwargs else None)
            if arg in kwargs:
                del kwargs[arg]
        kwargs['command'] = self._choosePositions
        if self.prompt is None:
            self.prompt = self.defaultPrompt
        ttk.Button.__init__(self, *args, **kwargs)
        self.setPositions([])

    def setPositions(self, values):
        self.selected = values
        self.configure(
            text='[wybrano: %d]' % (len(values)))
        if self.callback is not None:
            self.callback(values)

    def _choosePositions(self):
        options = self.getOptions()
        if not len(options):
            tkMessageBox.showerror(
                self.title, self.errorMessage)
            self.setPositions([])
        else:
            dialog = tk.Toplevel(self)
            dialog.title(self.title)
            dialog.grab_set()
            dialog.focus_force()
            selectionFrame = self.dialogclass(
                dialog, title=self.prompt,
                options=options,
                selected=self.selected,
                callback=self.setPositions, vertical=True)
            selectionFrame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

class SelectionFrame(ScrollableFrame):
    def __init__(self, master, title='', options=[],
                 selected=None, callback=None, *args, **kwargs):
        self.values = {}
        self.title = title
        self.options = options
        self.selected = selected
        self.callback = callback
        ScrollableFrame.__init__(self, master=master, *args, **kwargs)
        (ttk.Button(master, text='Zapisz', command=self._save)).pack(
            side=tk.BOTTOM, fill=tk.Y)

    def renderOption(self, container, option, idx):
        pass

    def _mapValue(self, idx, value):
        return idx + 1

    def _save(self):
        if self.callback:
            self.callback(
                [idx for idx, value
                 in self.values.iteritems() if value.get()])
        self.master.destroy()

    def renderHeader(self, container):
        container.columnconfigure(1, weight=1)
        (ttk.Label(container, text=self.title)).grid(
            row=0, column=0, columnspan=2)

    def renderContent(self, container):
        self.renderHeader(container)
        for idx, option in enumerate(self.options):
            key = self._mapValue(idx, option)
            self.values[key] = NotifyIntVar()
            self.renderOption(container, option, idx)
            if self.selected and key in self.selected:
                self.values[key].set(True)

class RefreshableOptionMenu(ttk.OptionMenu):
    def __init__(self, master, variable, *args, **kwargs):
        self._valueVariable = variable
        self._valueVariable.trace('w', self._valueSet)
        self._lastValue = variable.get()
        newVar = NotifyStringVar()
        ttk.OptionMenu.__init__(self, master, newVar, *args, **kwargs)
        self._valueLock = False
        self.refreshOptions()

    class _setit(tk._setit):
        def __init__(self, var, valVar, label, value, callback=None):
            tk._setit.__init__(self, var, label, callback)
            self._valueVariable = valVar
            self._properValue = value
        def __call__(self, *args):
            self.__var.set(self.__value)
            self._valueVariable.set(self._properValue)
            if self.__callback:
                self.__callback(self._valueVariable, *args)

    def refreshOptions(self, *args):
        try:
            options = self.getOptions()
            self['menu'].delete(0, tk.END)
            for label, option in options:
                self['menu'].add_command(
                    label=label,
                    command=self._setit(
                        self._variable, self._valueVariable,
                        label, option, self._callback))
            self._valueLock = True
            self._valueVariable.set(
                self._lastValue
                if self._lastValue in [option[1] for option in options]
                else '')
            self._valueLock = False
        except tk.TclError:
            # we're probably being destroyed, ignore
            pass

    def getOptions(self):
        return [
            (self.getLabel(value), self.getVarValue(value))
            for value in self.getValues()]

    def getLabel(self, value):
        pass

    def getValues(self):
        pass

    def getVarValue(self, value):
        return self.getLabel(value)

    def _valueSet(self, *args):
        if not self._valueLock:
            self._lastValue = self._valueVariable.get()
        options = self.getOptions()
        value = self._valueVariable.get()
        for label, val in options:
            if unicode(value) == unicode(val):
                tk._setit(self._variable, label)()
                return
        tk._setit(self._variable, '')()

class TraceableText(tk.Text):
    def __init__(self, *args, **kwargs):
        self._variable = None
        self._variableLock = False
        if 'variable' in kwargs:
            self._variable = kwargs['variable']
            del kwargs['variable']
        tk.Text.__init__(self, *args, **kwargs)
        if self._variable is not None:
            self._orig = self._w + '_orig'
            self.tk.call('rename', self._w, self._orig)
            self.tk.createcommand(self._w, self._proxy)
            self._variable.trace('w', self._fromVariable)

    def _fromVariable(self, *args):
        if not self._variableLock:
            self._variableLock = True
            self.delete('1.0', tk.END)
            self.insert(tk.END, self._variable.get())
            self._variableLock = False

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        if command in ('insert', 'delete', 'replace') and \
           not self._variableLock:
            text = self.get('1.0', tk.END).strip()
            self._variableLock = True
            self._variable.set(text)
            self._variableLock = False
        return result

class NumericSpinbox(tk.Spinbox):
    def __init__(self, *args, **kwargs):
        kwargs['justify'] = tk.RIGHT
        self._variable = None
        if 'textvariable' in kwargs:
            self._variable = kwargs['textvariable']
        self._default = kwargs['from_'] if 'from_' in kwargs else 0
        tk.Spinbox.__init__(self, *args, **kwargs)
        if self._variable is not None:
            if not isinstance(self._variable, NotifyNumericVar):
                raise AttributeError(
                    'NumericSpinbox variable must be NotifyNumericVar')
            self._variable.trace('w', self._onChange)

    def _onChange(self, *args):
        val = self._variable.get()
        if val is None:
            self._variable.set(self._default)
