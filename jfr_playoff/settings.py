import glob, json, os, readline, sys

def complete_filename(text, state):
    return (glob.glob(text+'*')+[None])[state]

class PlayoffSettings:

    def __init__(self):
        self.settings = None
        self.interactive = False
        self.settings_file = None
        if len(sys.argv) > 1:
            self.settings_file = sys.argv[1]
        else:
            self.interactive = True

    def load(self):
        if self.settings_file is None:
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete_filename)
            self.settings_file = raw_input('JSON settings file: ')

        if self.settings is None:
            self.settings = json.load(open(self.settings_file))

    def has_section(self, key):
        self.load()
        return key in self.settings

    def get(self, *keys):
        self.load()
        section = self.settings
        for key in keys:
            section = section[key]
        return section
