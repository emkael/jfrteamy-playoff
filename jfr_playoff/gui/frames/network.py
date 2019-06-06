#coding=utf-8

import socket

import tkinter as tk
from tkinter import ttk
import tkMessageBox as tkmb

from ...db import PlayoffDB
from ..frames import RepeatableEntry, WidgetRepeater
from ..frames import GuiFrame, ScrollableFrame, getIntVal

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
    def getConfig(self):
        if len(self.host.get().strip()):
            return {
                'host': self.host.get().strip(),
                'port': getIntVal(self.port, default=3306),
                'user': self.user.get().strip(),
                'pass': self.pass_.get().strip()
            }
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
        (ttk.Label(self, text='Ustawienia MySQL')).grid(
            row=0, column=0, columnspan=4, sticky=tk.E+tk.W)
        (ttk.Label(self, text='Host:')).grid(
            row=1, column=0, sticky=tk.E)
        self.host = tk.StringVar()
        self.host.trace('w', self._changeNotify)
        (ttk.Entry(self, textvariable=self.host)).grid(
            row=1, column=1, sticky=tk.E+tk.W)
        (ttk.Label(self, text='Port:')).grid(
            row=1, column=2, sticky=tk.E)
        self.port = tk.StringVar()
        self.port.set(3306)
        self.port.trace('w', self._changeNotify)
        (tk.Spinbox(
            self, textvariable=self.port, width=5,
            from_=0, to=65535)).grid(row=1, column=3, sticky=tk.W)
        (ttk.Label(self, text='Użytkownik:')).grid(
            row=2, column=0, sticky=tk.E)
        self.user = tk.StringVar()
        self.user.trace('w', self._changeNotify)
        (ttk.Entry(self, textvariable=self.user)).grid(
            row=2, column=1, sticky=tk.E+tk.W)
        (ttk.Button(
            self, text='Testuj ustawienia', command=self._testDB)).grid(
                row=2, column=3)
        self.dbError = None
        self.dbTestLabel = ttk.Label(self)
        self.dbTestLabel.grid(row=2, column=4)
        self.dbTestLabel.bind('<Button-1>', self._dbError)
        (ttk.Label(self, text='Hasło:')).grid(
            row=3, column=0, sticky=tk.E)
        self.pass_ = tk.StringVar()
        self.pass_.trace('w', self._changeNotify)
        (ttk.Entry(self, textvariable=self.pass_, show='*')).grid(
            row=3, column=1, sticky=tk.E+tk.W)

class GoniecConfigurationFrame(GuiFrame):
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8090

    def _enableWidgets(self):
        for field in [self.portField, self.hostField, self.testButton]:
            field.configure(
                state=tk.NORMAL if self.enable.get() else tk.DISABLED)

    def _test(self):
        def test():
            goniec = socket.socket()
            goniec.connect(
                (self.host.get().strip(), getIntVal(
                    self.port, self.DEFAULT_PORT)))
            goniec.close()
        self.testError = network_test(test, self.testLabel)

    def _testError(self, event):
        if self.testError is not None:
            tkmb.showerror('Błąd połączenia z Gońcem', self.testError)

    def renderContent(self):
        (ttk.Label(self, text='Konfiguracja Gońca:')).grid(
            row=0, column=0, columnspan=4, sticky=tk.W)
        self.enable = tk.IntVar()
        (ttk.Checkbutton(
            self, text='Włącz obsługę Gońca', variable=self.enable,
            command=self._enableWidgets)).grid(
                row=1, column=0, columnspan=2, sticky=tk.W)
        (ttk.Label(self, text='Host:')).grid(row=2, column=0)
        self.host = tk.StringVar()
        self.host.set(self.DEFAULT_HOST)
        self.hostField = ttk.Entry(self, textvariable=self.host)
        self.hostField.grid(row=2, column=1)
        (ttk.Label(self, text='Port:')).grid(row=2, column=2)
        self.port = tk.StringVar()
        self.port.set(self.DEFAULT_PORT)
        self.portField = tk.Spinbox(
            self, textvariable=self.port, width=5)
        self.portField.grid(row=2, column=3)
        self.testButton = ttk.Button(
            self, text='Testuj ustawienia', command=self._test)
        self.testButton.grid(row=3, column=1, sticky=tk.E)
        self.testError = None
        self.testLabel = ttk.Label(self)
        self.testLabel.grid(row=3, column=2, sticky=tk.W)
        self.testLabel.bind('<Button-1>', self._testError)
        self._enableWidgets()


class RemoteConfigurationFrame(ScrollableFrame):
    def renderContent(self, container):
        (ttk.Label(container, text='Zdalne pliki konfiguracyjne:')).pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)
        self.repeater = WidgetRepeater(
            container, RepeatableEntry, classParams={'width':100})
        self.repeater.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

__all__ = ['MySQLConfigurationFrame', 'GoniecConfigurationFrame', 'RemoteConfigurationFrame']
