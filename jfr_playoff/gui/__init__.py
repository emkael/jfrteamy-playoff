#coding=utf-8

import codecs, copy, json, os, shutil, sys, tempfile, threading, traceback, webbrowser
from collections import OrderedDict
import logging as log

import Tkinter as tk
import ttk
import tkFileDialog as tkfd
import tkMessageBox as tkmb

from jfr_playoff.filemanager import PlayoffFileManager
from jfr_playoff.generator import PlayoffGenerator
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.settings import PlayoffSettings

from .tabs import *
from .icons import GuiImage
from .frames import LabelButton, NumericSpinbox
from .variables import NumericVar
from .logframe import LogWindow

class PlayoffGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        ttk.Style().configure('TLabelframe.Label', foreground='black')
        ttk.Style().configure('TLabelframe', padding=5)
        self.geometry('920x640')
        self._setWindowIcon(self, GuiImage.get_icon('playoff'))
        self.tabs = {}
        self.logWindow = LogWindow(self)
        self.logWindow.title('Dziennik komunikatów')
        self._setWindowIcon(self.logWindow, GuiImage.get_icon('playoff'))
        self._buildMenu()
        self.newFileIndex = 0
        self._title = tk.StringVar()
        self._title.trace('w', self._setTitle)
        self._dirty = tk.BooleanVar()
        self._dirty.trace('w', self._setTitle)
        self._dirty.trace('w', self._setMenuButtons)
        self._runTimer = None
        self._runtimeError = None
        self._filepath = None
        self._bindKeyboardShortcuts()
        self.protocol('WM_DELETE_WINDOW', self.onClose)

    def run(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        for tab in tabs.__all__:
            self.tabs[tab] = globals()[tab](self.notebook)
            self.notebook.add(self.tabs[tab], text=self.tabs[tab].title)
        if len(sys.argv) > 1:
            self.openFile(sys.argv[1])
        else:
            self.newFile()
        self.bind('<<ValueChanged>>', self._onFileChange, add='+')
        self.bind('<<BracketGenerated>>', self._onBracketGenerated, add='+')
        self.bind('<<BracketError>>', self._onBracketError, add='+')
        self.mainloop()

    def _setWindowIcon(self, window, icon):
        try:
            self.tk.call('wm', 'iconphoto', window._w, icon)
        except tk.TclError:
            pass # sometimes it fails on Linux, just ignore

    def _onFileChange(self, *args):
        self._dirty.set(True)

    def _checkSave(self):
        if self._dirty.get():
            if tkmb.askyesno(
                    'Zapisz zmiany',
                    'Czy chcesz zapisać zmiany w bieżącej drabince?'):
                self.onSave()

    def _setTitle(self, *args):
        self.title('%s - %s%s' % (
            'TeamyPlayOff',
            self._title.get(),
            ' *' if self._dirty.get() else ''
        ))

    def _setMenuButtons(self, *args):
        self.menuButtons['save'].configure(
            state=tk.NORMAL if self._dirty.get() else tk.DISABLED)

    def _setValues(self, config):
        for tab in self.tabs.values():
            tab.setValues(config)

    def _resetValues(self):
        self._setValues({})

    def _buildMenu(self):
        menu = tk.Frame(self)
        menu.pack(side=tk.TOP, fill=tk.X)
        statusBar = ttk.Label(menu)
        statusBar.pack(side=tk.RIGHT)
        self.menuButtons = {}
        for icon, command, tooltip in [
                ('new', self.onNewFile, 'Nowa drabinka...'),
                ('open', self.onFileOpen, 'Otwórz drabinkę...'),
                ('save', self.onSave, 'Zapisz'),
                ('saveas', self.onSaveAs, 'Zapisz jako...')]:
            self.menuButtons[icon] = LabelButton(
                menu, image=GuiImage.get_icon(icon), command=command,
                tooltip=tooltip, label=statusBar)
            self.menuButtons[icon].pack(side=tk.LEFT)
        (ttk.Separator(menu, orient=tk.VERTICAL)).pack(
            side=tk.LEFT, fill=tk.Y, padx=3, pady=1)
        for icon, command, tooltip in [
                ('run-once', self.onRunOnce, 'Wygeneruj')]:
            self.menuButtons[icon] = LabelButton(
                menu, image=GuiImage.get_icon(icon), command=command,
                tooltip=tooltip, label=statusBar)
            self.menuButtons[icon].pack(side=tk.LEFT)
        self.runningLabel = ttk.Label(menu, width=10, text='')
        self.runningLabel.pack(side=tk.LEFT)
        (ttk.Separator(menu, orient=tk.VERTICAL)).pack(
            side=tk.LEFT, fill=tk.Y, padx=3, pady=1)
        for icon, command, tooltip in [
                ('run-timed', self.onRunTimed, 'Generuj co X sekund')]:
            self.menuButtons[icon] = LabelButton(
                menu, image=GuiImage.get_icon(icon), command=command,
                tooltip=tooltip, label=statusBar)
            self.menuButtons[icon].pack(side=tk.LEFT)
        self.interval = NumericVar()
        self.intervalField = NumericSpinbox(
            menu, width=5,
            textvariable=self.interval, from_=30, to=3600)
        self.intervalField.pack(side=tk.LEFT)
        self.intervalLabel = ttk.Label(menu, text='sekund')
        self.intervalLabel.pack(side=tk.LEFT)
        (ttk.Separator(menu, orient=tk.VERTICAL)).pack(
            side=tk.LEFT, fill=tk.Y, padx=3, pady=1)
        for icon, command, tooltip in [
                ('log', self.onLogWindowOpen, 'Dziennik komunikatów')]:
            self.menuButtons[icon] = LabelButton(
                menu, image=GuiImage.get_icon(icon), command=command,
                tooltip=tooltip, label=statusBar)
            self.menuButtons[icon].pack(side=tk.LEFT)

    def _bindKeyboardShortcuts(self):
        self.bind('<Control-n>', self.onNewFile)
        self.bind('<Control-s>', self.onSave)
        self.bind('<Control-S>', self.onSaveAs)
        self.bind('<Control-o>', self.onFileOpen)
        self.bind('<Control-q>', self.onClose)
        self.bind('<F9>', self.onRunOnce)

    def onNewFile(self, *args):
        self._checkSave()
        self.newFile()

    def onFileOpen(self, *args):
        self._checkSave()
        filename = tkfd.askopenfilename(
            title='Wybierz plik drabniki',
            filetypes=(('JFR Teamy Play-Off files', '*.jtpo'),
                       ('JSON files', '*.json'),))
        if filename:
            self.openFile(filename)

    def onSave(self, *args):
        if self._filepath is not None:
            self.saveFile(self._filepath)
        else:
            self.onSaveAs()

    def onSaveAs(self, *args):
        filename = tkfd.asksaveasfilename(
            title='Wybierz plik drabniki',
            filetypes=(('JFR Teamy Play-Off files', '*.jtpo'),
                       ('JSON files', '*.json'),))
        if filename:
            if not filename.lower().endswith('.jtpo'):
                filename = filename + '.jtpo'
            self.saveFile(filename)

    def onClose(self, *args):
        self._checkSave()
        self.destroy()

    def _run(self, config, interactive=True):
        self._interactive = interactive
        try:
            self._tempPath = None
            if not len(config.get('output', '')):
                tempDir = tempfile.mkdtemp(prefix='jfrplayoff-')
                self._tempPath = os.path.join(
                    tempDir, next(tempfile._get_candidate_names()))
                config['output'] = self._tempPath + '.html'
            p_remote.clear_cache()
            settings = PlayoffSettings(config_obj=config)
            generator = PlayoffGenerator(settings)
            content = generator.generate_content()
            file_manager = PlayoffFileManager(settings)
            self._outputPath = file_manager.write_content(content)
            file_manager.copy_scripts()
            file_manager.copy_styles()
            file_manager.send_files()
            self.event_generate('<<BracketGenerated>>', when='tail')
        except Exception as e:
            log.getLogger().error(str(e))
            traceback.print_exc()
            if interactive:
                self._runtimeError = e
                self.event_generate('<<BracketError>>', when='tail')

    def _onBracketGenerated(self, *args):
        self._setRunWidgetState(tk.NORMAL)
        if self._interactive:
            if tkmb.askyesno(
                    'Otwórz drabinkę',
                    'Otworzyć drabinkę w domyślnej przeglądarce?'):
                webbrowser.open(os.path.realpath(self._outputPath))
            else:
                if self._tempPath is not None:
                    shutil.rmtree(os.path.dirname(self._outputPath))

    def _onBracketError(self, *args):
        tkmb.showerror('Błąd generowania drabinki', str(self._runtimeError))
        self._setRunWidgetState(tk.NORMAL)
        self._runtimeError = None

    def _setRunWidgetState(self, state):
        self.menuButtons['run-once'].configure(state=state)
        self.runningLabel.configure(
            text='' if state == tk.NORMAL else 'pracuję...')

    def _setTimerWidgetState(self, state):
        for widget in [self.intervalField, self.intervalLabel]:
            widget.configure(state=state)
        self.menuButtons['run-timed'].configure(
            image=GuiImage.get_icon('run-timed')
            if state == tk.NORMAL else GuiImage.get_icon('stop-timed'))

    def onRunOnce(self, interactive=True):
        self._setRunWidgetState(tk.DISABLED)
        if not interactive:
            self._runTimer = self.after(
                1000 * self.interval.get(default=30), self.onRunOnce, False)
        config = self.getConfig()
        thread = threading.Thread(
            target=self._run, args=(config, interactive,))
        thread.start()

    def onRunTimed(self):
        if self._runTimer is None:
            self.after(100, self.onRunOnce, False)
            self._setTimerWidgetState(tk.DISABLED)
        else:
            self.after_cancel(self._runTimer)
            self._runTimer = None
            self._setTimerWidgetState(tk.NORMAL)

    def onLogWindowOpen(self):
        self.logWindow.update()
        self.logWindow.deiconify()

    def newFile(self):
        self._filepath = None
        self.newFileIndex += 1
        self._title.set('Nowa drabinka %d' % (self.newFileIndex))
        self._resetValues()
        self.after(0, self._dirty.set, False)

    def openFile(self, filepath):
        self._filepath = filepath
        self._title.set(os.path.basename(filepath))
        self._setValues(json.load(open(filepath)))
        self.after(0, self._dirty.set, False)

    def saveFile(self, filepath):
        json.dump(
            self.getConfig(), codecs.open(filepath, 'w', encoding='utf8'),
            indent=4, ensure_ascii=False)
        self._filepath = filepath
        self._title.set(os.path.basename(filepath))
        self.after(0, self._dirty.set, False)

    def getConfig(self):
        config = OrderedDict()
        for tab in self.tabs.values():
            tabConfig = tab.getConfig()
            if tabConfig is not None:
                config = self._mergeConfig(config, tab.getConfig())
        return config

    def _mergeConfig(self, base, update):
        result = copy.copy(base)
        for key, value in update.iteritems():
            if key in result:
                if isinstance(result[key], dict):
                    result[key] = self._mergeConfig(
                        result[key], update[key])
                else:
                    result[key] = update[key]
            else:
                result[key] = value
        return result

    def getDbConfig(self):
        return self.tabs['NetworkTab'].getDB()

    def getTeams(self):
        return self.tabs['TeamsTab'].getTeams()

    def getDBs(self):
        return self.tabs['NetworkTab'].getDBList()

    def getMatches(self):
        return self.tabs['MatchesTab'].getMatches()

    def getNewMatchID(self, match):
        matches = self.tabs['MatchesTab'].getMatches()
        if len(matches) > 0:
            return max([m.getMatchID() for m in matches]) + 1
        return 1
