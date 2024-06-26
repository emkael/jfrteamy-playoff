import glob
import json
import readline
import requests
import sys

from jfr_playoff.logger import PlayoffLogger, log_encoding


def complete_filename(text, state):
    return (glob.glob(text+'*')+[None])[state]


class PlayoffSettings(object):

    def __init__(self, config_file=None, config_obj=None):
        self.settings = None
        self.interactive = False
        self.settings_file = None
        if config_file is not None:
            self.settings_file = config_file.decode(
                sys.getfilesystemencoding())
        else:
            if config_obj is not None:
                self.settings = config_obj
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
            PlayoffLogger.get('settings').warning(
                'unable to merge remote config %s: %s(%s)',
                remote_url, type(e).__name__, str(e))
        return base_config

    def load(self):
        if self.interactive:
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete_filename)
            self.settings_file = raw_input(
                'JSON settings file: ').decode(log_encoding())

        if self.settings is None:
            PlayoffLogger.get('settings').info(
                'loading config file: %s', unicode(self.settings_file))
            self.settings = json.loads(
                open(unicode(self.settings_file)).read().decode('utf-8-sig'))
            if self.has_section('remotes'):
                remote_config = {}
                for remote in self.get('remotes'):
                    PlayoffLogger.get('settings').info(
                        'merging remote config: %s', remote)
                    remote_config = self.__merge_config(
                        remote_config, remote_url=remote)
                    PlayoffLogger.get('settings').debug(
                        'remote config: %s', remote_config)
                self.settings = self.__merge_config(
                    self.settings, new_config=remote_config,
                    overwrite=False)
            PlayoffLogger.get('settings').debug(
                'parsed config: %s', self.settings)

    def has_section(self, key):
        self.load()
        return key in self.settings

    def get(self, *keys):
        self.load()
        section = self.settings
        for key in keys:
            section = section[key]
        return section
