#coding=utf-8

import tkinter as tk

class NotifyVar(tk.Variable):
    def __init__(self, *args, **kwargs):
        tk.Variable.__init__(self, *args, **kwargs)
        self.trace('w', self._onChange)

    def _onChange(self, *args):
        self._root.event_generate('<<ValueChanged>>', when='tail')

class NotifyStringVar(NotifyVar, tk.StringVar):
    pass

class NotifyIntVar(NotifyVar, tk.IntVar):
    pass

class NotifyNumericVar(NotifyStringVar):
    def get(self, default=None):
        try:
            return int(str(NotifyStringVar.get(self)).strip())
        except ValueError:
            return default
