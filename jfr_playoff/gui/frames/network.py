#coding=utf-8

import socket
from collections import OrderedDict

import tkinter as tk
from tkinter import ttk
import tkMessageBox as tkmb

from ...db import PlayoffDB
from ..frames import RepeatableEntry, WidgetRepeater, NumericSpinbox
from ..frames import GuiFrame, ScrollableFrame
from ..variables import NotifyStringVar, NotifyIntVar, NotifyNumericVar

def network_test(connFunction, testLabel):
    try:
        connFunction()
        testLabel.configure(text='✓')
        testLabel.configure(foreground='green')
        return None
    except Exception as e:
        testLabel.configure(text='✗')
        testLabel.configure(foreground='red')
        return unicode(str(e).decode('utf-8', errors='replace'))

class MySQLConfigurationFrame(GuiFrame):
    DEFAULT_PORT = 3306

    def getConfig(self):
        if len(self.host.get().strip()):
            return OrderedDict({
                'host': self.host.get().strip(),
                'port': self.port.get(default=3306),
                'user': self.user.get().strip(),
                'pass': self.pass_.get().strip()
            })
        return None

    def _testDB(self):
        def test():
            dbConfig = self.getConfig()
            if dbConfig is None:
                raise AttributeError('Database not configured')
            db = PlayoffDB(dbConfig)
        self.dbError = network_test(test, self.dbTestLabel)

    def _dbError(self, event):
        if self.dbError is not None:
            tkmb.showerror('Błąd połączenia z bazą danych', self.dbError)

    def _changeNotify(self, *args):
        self.winfo_toplevel().event_generate(
            '<<DBSettingsChanged>>', when='tail')

    def renderContent(self):
        self.host = NotifyStringVar()
        self.host.trace('w', self._changeNotify)
        self.port = NotifyNumericVar()
        self.port.trace('w', self._changeNotify)
        self.user = NotifyStringVar()
        self.user.trace('w', self._changeNotify)
        self.pass_ = NotifyStringVar()
        self.pass_.trace('w', self._changeNotify)

        self.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text='Ustawienia MySQL')
        frame.grid(row=0, column=0, columnspan=4, sticky=tk.E+tk.W+tk.N+tk.S)

        (ttk.Label(frame, text='Host:')).grid(
            row=0, column=0, sticky=tk.E)
        (ttk.Entry(frame, textvariable=self.host)).grid(
            row=0, column=1, sticky=tk.E+tk.W)

        (ttk.Label(frame, text='Port:')).grid(
            row=0, column=2, sticky=tk.E)
        (NumericSpinbox(
            frame, textvariable=self.port, width=5,
            from_=0, to=65535)).grid(row=0, column=3, sticky=tk.W)

        (ttk.Label(frame, text='Użytkownik:')).grid(
            row=1, column=0, sticky=tk.E)
        (ttk.Entry(frame, textvariable=self.user)).grid(
            row=1, column=1, sticky=tk.E+tk.W)

        (ttk.Button(
            frame, text='Testuj ustawienia', command=self._testDB)).grid(
                row=1, column=3)
        self.dbError = None
        self.dbTestLabel = ttk.Label(frame)
        self.dbTestLabel.grid(row=1, column=4)
        self.dbTestLabel.bind('<Button-1>', self._dbError)

        (ttk.Label(frame, text='Hasło:')).grid(
            row=2, column=0, sticky=tk.E)
        (ttk.Entry(frame, textvariable=self.pass_, show='*')).grid(
            row=2, column=1, sticky=tk.E+tk.W)

        self.setValues({})

    def setValues(self, values):
        self.host.set(values['host'] if 'host' in values else '')
        self.port.set(
            values['port'] if 'port' in values else self.DEFAULT_PORT)
        self.user.set(values['user'] if 'user' in values else '')
        self.pass_.set(values['pass'] if 'pass' in values else '')

class GoniecConfigurationFrame(GuiFrame):
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8090

    def _enableWidgets(self, *args):
        for field in [self.portField, self.hostField, self.testButton]:
            field.configure(
                state=tk.NORMAL if self.enable.get() else tk.DISABLED)

    def _test(self):
        def test():
            goniec = socket.socket()
            goniec.connect(
                (self.host.get().strip(),
                 self.port.get(default=self.DEFAULT_PORT)))
            goniec.close()
        self.testError = network_test(test, self.testLabel)

    def _testError(self, event):
        if self.testError is not None:
            tkmb.showerror('Błąd połączenia z Gońcem', self.testError)

    def renderContent(self):
        self.enable = NotifyIntVar()
        self.enable.trace('w', self._enableWidgets)
        self.host = NotifyStringVar()
        self.port = NotifyNumericVar()

        self.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text='Konfiguracja Gońca:')
        frame.grid(row=0, column=0, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S)
        (ttk.Checkbutton(
            frame, text='Włącz obsługę Gońca', variable=self.enable)).grid(
                row=0, column=0, columnspan=2, sticky=tk.W)

        (ttk.Label(frame, text='Host:')).grid(row=1, column=0)
        self.hostField = ttk.Entry(frame, textvariable=self.host)
        self.hostField.grid(row=1, column=1)

        (ttk.Label(frame, text='Port:')).grid(row=1, column=2)
        self.portField = NumericSpinbox(
            frame, textvariable=self.port, width=5)
        self.portField.grid(row=1, column=3)

        self.testButton = ttk.Button(
            frame, text='Testuj ustawienia', command=self._test)
        self.testButton.grid(row=2, column=1, sticky=tk.E)
        self.testError = None
        self.testLabel = ttk.Label(frame)
        self.testLabel.grid(row=2, column=2, sticky=tk.W)
        self.testLabel.bind('<Button-1>', self._testError)

        self.setValues({})

    def setValues(self, values):
        self.host.set(
            values['host'] if 'host' in values else self.DEFAULT_HOST)
        self.port.set(
            values['port'] if 'port' in values else self.DEFAULT_PORT)
        self.enable.set(values['enabled'] if 'enabled' in values else 0)

    def getValues(self):
        config = OrderedDict({
            'enabled': self.enable.get()
        })
        if self.enable.get():
            config['host'] = self.host.get()
            config['port'] = self.port.get()
        return config

class RemoteConfigurationFrame(ScrollableFrame):
    def renderContent(self, container):
        frame = ttk.LabelFrame(container, text='Zdalne pliki konfiguracyjne:')
        frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)
        self.repeater = WidgetRepeater(
            frame, RepeatableEntry, classParams={'width':100})
        self.repeater.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def setValues(self, values):
        self.repeater.setValue(values)

    def getValues(self):
        return self.repeater.getValue()

__all__ = ['MySQLConfigurationFrame', 'GoniecConfigurationFrame', 'RemoteConfigurationFrame']
