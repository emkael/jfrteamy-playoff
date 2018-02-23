import glob
import json
import readline
import requests
import sys


def complete_filename(text, state):
    return (glob.glob(text+'*')+[None])[state]


class PlayoffSettings(object):

    def __init__(self, config_file):
        self.settings = None
        self.interactive = False
        self.settings_file = None
        if config_file is not None:
            self.settings_file = config_file.decode(
                sys.getfilesystemencoding())
        else:
            self.interactive = True

    def __merge_config(self, base_config,
                       new_config=None, remote_url=None,
                       overwrite=True):
        try:
            remote_config = new_config if new_config is not None else \
                            json.loads(requests.get(remote_url).text)
            for key, value in remote_config.iteritems():
                if (key not in base_config) or overwrite:
                    base_config[key] = value
        except Exception as e:
            print 'WARNING: unable to merge remote config: %s' % (str(e))
            if remote_url is not None:
                print 'Offending URL: %s' % (remote_url)
        return base_config

    def load(self):
        if self.settings_file is None:
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete_filename)
            self.settings_file = raw_input(
                'JSON settings file: ').decode(sys.stdin.encoding)

        if self.settings is None:
            self.settings = json.loads(
                open(unicode(self.settings_file)).read().decode('utf-8-sig'))
            if self.has_section('remotes'):
                remote_config = {}
                for remote in self.get('remotes'):
                    remote_config = self.__merge_config(
                        remote_config, remote_url=remote)
                self.settings = self.__merge_config(
                    self.settings, new_config=remote_config,
                    overwrite=False)

    def has_section(self, key):
        self.load()
        return key in self.settings

    def get(self, *keys):
        self.load()
        section = self.settings
        for key in keys:
            section = section[key]
        return section
