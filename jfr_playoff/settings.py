import glob, json, os, readline, sys

def complete_filename(text, state):
    return (glob.glob(text+'*')+[None])[state]

class PlayoffSettings:

    def __init__(self):
        self.interactive = False
        if len(sys.argv) > 1:
            settings_file = sys.argv[1]
        else:
            self.interactive = True
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete_filename)
            settings_file = raw_input('JSON settings file: ')

        if not os.path.exists(settings_file):
            raise IOError('Settings file %s not found' % settings_file)

        self.settings = json.load(open(settings_file))

    def has_section(self, key):
        return key in self.settings

    def get(self, *keys):
        section = self.settings
        for key in keys:
            section = section[key]
        return section
