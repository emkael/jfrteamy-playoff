#coding=utf-8

import datetime
import logging as log
from collections import OrderedDict

import tkinter as tk
from tkinter import ttk
import tkFileDialog as tkfd

class LogWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        self.renderContents()
        self._registerLogging()
        self._records = []
        self._counter = -1

    def renderContents(self):
        columns = OrderedDict([
            ('level', 'Poziom komunikatu'),
            ('category', 'Moduł'),
            ('message', 'Komunikat')])
        self.logList = ttk.Treeview(
            self, show='headings',
            columns=columns.keys(),
            selectmode='browse')
        for column, heading in columns.iteritems():
            self.logList.heading(column, text=heading)
        self.logList.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        btnFrame = tk.Frame(self)
        btnFrame.pack(side=tk.BOTTOM)
        (ttk.Button(
            btnFrame, text='Zapisz dziennik...',
            command=self.onRecordsSave)).pack(side=tk.LEFT)
        (ttk.Button(
            btnFrame, text='Wyczyść dziennik',
            command=self.resetRecords)).pack(side=tk.LEFT)

    def _registerLogging(self):
        logHandler = LogHandler(log.INFO, window=self)
        logger = log.getLogger()
        logger.setLevel(log.INFO)
        logger.addHandler(logHandler)

    def addRecord(self, record):
        self._counter += 1
        self._records.append((record, datetime.datetime.now()))
        self.logList.insert(
            '', tk.END, tag=self._counter, values=[
                record.levelname, record.name, record.message
            ])

    def resetRecords(self):
        self._records = []
        self.logList.delete(*self.logList.get_children())

    def onRecordsSave(self, *args):
        filename = tkfd.asksaveasfilename(
            title='Wybierz plik dziennika',
            filetypes=(('Log files', '*.log'),))
        if filename:
            if not filename.lower().endswith('.log'):
                filename = filename + '.log'
            self._saveRecords(filename)

    def _saveRecords(self, filename):
        with open(filename, 'w') as fileObj:
            for record, timestamp in self._records:
                fileObj.write('%s\t%s\t%s\t%s' % (
                    timestamp, record.levelname, record.name, record.message))


class LogHandler(log.Handler):
    def __init__(self, *args, **kwargs):
        self._window = kwargs['window']
        del kwargs['window']
        log.Handler.__init__(self, *args, **kwargs)

    def handle(self, record):
        self.format(record)
        self._window.addRecord(record)
