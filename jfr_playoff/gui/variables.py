#coding=utf-8

import tkinter as tk

class NotifyVar(tk.Variable):
    def __init__(self, *args, **kwargs):
        tk.Variable.__init__(self, *args, **kwargs)
        self._prevValue = self.get()
        self._root.after(0, self.trace, 'w', self._onChange)

    def _onChange(self, *args):
        if self._prevValue != self.get():
            self._root.event_generate('<<ValueChanged>>', when='tail')
        self._prevValue = self.get()

class NumericVar(tk.StringVar):
    def get(self, default=None):
        try:
            return int(str(tk.StringVar.get(self)).strip())
        except ValueError:
            return default

class NotifyStringVar(NotifyVar, tk.StringVar):
    pass

class NotifyIntVar(NotifyVar, tk.IntVar):
    pass

class NotifyNumericVar(NumericVar, NotifyVar):
    pass
