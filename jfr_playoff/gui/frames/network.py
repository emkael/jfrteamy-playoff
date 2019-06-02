#coding=utf-8

import tkinter as tk
from tkinter import ttk
import tkMessageBox as tkmb

from ...db import PlayoffDB
from ..frames import getIntVal

class MySQLConfigurationFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.renderContent(self)

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
        try:
            dbConfig = self.getConfig()
            if dbConfig is None:
                raise AttributeError('Database not configured')
            db = PlayoffDB(dbConfig)
            self.dbError = None
            self.dbTestLabel.configure(text='✓')
            self.dbTestLabel.configure(foreground='green')
        except Exception as e:
            self.dbError = unicode(e)
            self.dbTestLabel.configure(text='✗')
            self.dbTestLabel.configure(foreground='red')

    def _dbError(self, event):
        if self.dbError is not None:
            tkmb.showerror('Błąd połączenia z bazą danych', self.dbError)

    def renderContent(self, container):
        (ttk.Label(container, text='Ustawienia MySQL')).grid(
            row=0, column=0, columnspan=4, sticky=tk.E+tk.W)
        (ttk.Label(container, text='Host:')).grid(
            row=1, column=0, sticky=tk.E)
        self.host = tk.StringVar()
        (ttk.Entry(container, textvariable=self.host)).grid(
            row=1, column=1, sticky=tk.E+tk.W)
        (ttk.Label(container, text='Port:')).grid(
            row=1, column=2, sticky=tk.E)
        self.port = tk.StringVar()
        self.port.set(3306)
        (tk.Spinbox(
            container, textvariable=self.port, width=5,
            from_=0, to=65535)).grid(row=1, column=3, sticky=tk.W)
        (ttk.Label(container, text='Użytkownik:')).grid(
            row=2, column=0, sticky=tk.E)
        self.user = tk.StringVar()
        (ttk.Entry(container, textvariable=self.user)).grid(
            row=2, column=1, sticky=tk.E+tk.W)
        (ttk.Button(
            container, text='Testuj ustawienia', command=self._testDB)).grid(
                row=2, column=3)
        self.dbError = None
        self.dbTestLabel = ttk.Label(container)
        self.dbTestLabel.grid(row=2, column=4)
        self.dbTestLabel.bind('<Button-1>', self._dbError)
        (ttk.Label(container, text='Hasło:')).grid(
            row=3, column=0, sticky=tk.E)
        self.pass_ = tk.StringVar()
        (ttk.Entry(container, textvariable=self.pass_, show='*')).grid(
            row=3, column=1, sticky=tk.E+tk.W)

__all__ = ['MySQLConfigurationFrame']
