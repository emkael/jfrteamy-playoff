#coding=utf-8

import datetime
import logging as log
from collections import OrderedDict

import Tkinter as tk
import ttk
import tkFileDialog as tkfd

class LogWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        self.renderContents()
        self._records = []
        self._counter = -1
        self._registerLogging()

    def renderContents(self):
        columns = [
            ('level', 'Poziom komunikatu', 150),
            ('category', 'Moduł', 150),
            ('message', 'Komunikat', None)]
        self.logList = ttk.Treeview(
            self, show='headings',
            columns=[c[0] for c in columns],
            selectmode='browse')
        for column, heading, width in columns:
            self.logList.heading(column, text=heading)
            if width is not None:
                self.logList.column(column, width=width, stretch=False)
            else:
                self.logList.column(column, stretch=True)
        self.logList.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        btnFrame = tk.Frame(self)
        btnFrame.pack(side=tk.BOTTOM)
        (ttk.Button(
            btnFrame, text='Zapisz dziennik...',
            command=self.onRecordsSave)).pack(side=tk.LEFT)
        (ttk.Button(
            btnFrame, text='Wyczyść dziennik',
            command=self.resetRecords)).pack(side=tk.LEFT)

    def _getGUIHandler(self):
        return LogHandler(log.INFO, window=self)

    def _getConsoleHandler(self):
        consoleHandler = log.StreamHandler()
        consoleHandler.setFormatter(
            log.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        return consoleHandler

    def _registerLogging(self):
        logger = log.getLogger()
        logger.setLevel(log.INFO)
        for handler in [self._getConsoleHandler, self._getGUIHandler]:
            logger.addHandler(handler())

    def addRecord(self, record):
        self._counter += 1
        self._records.append((record, datetime.datetime.now()))
        if not isinstance(record.message, unicode):
            record.message = unicode(record.message, errors='replace')
        self.logList.insert(
            '', tk.END, tag=self._counter, values=[
                record.levelname, record.name, record.message
            ])
        self.logList.yview_moveto(1)

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
                fileObj.write((
                    u'%s\t%s\t%s\t%s\n' % (
                        timestamp,
                        record.levelname, record.name, record.message)).encode(
                            'utf8'))


class LogHandler(log.Handler):
    def __init__(self, *args, **kwargs):
        self._window = kwargs['window']
        del kwargs['window']
        log.Handler.__init__(self, *args, **kwargs)

    def handle(self, record):
        self.format(record)
        self._window.addRecord(record)
