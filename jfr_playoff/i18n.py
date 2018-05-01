# -*- coding: utf-8 -*-

import re

PLAYOFF_I18N_DEFAULTS = {
    'SCORE': 'wynik',
    'FINAL_STANDINGS': 'klasyfikacja końcowa',
    'STANDINGS_PLACE': 'miejsce',
    'STANDINGS_TEAM': 'drużyna',
    'STANDINGS_CAPTIONS': 'legenda',
    'FOOTER_GENERATED': 'strona wygenerowana',
    'SWISS_DEFAULT_LABEL': 'Turniej o&nbsp;%d.&nbsp;miejsce'
}

class PlayoffI18N(object):

    def __init__(self, settings):
        self.settings = settings
        self.string_match = re.compile(r'{{(.*)}}')

    def localize(self, string):
        return re.sub(
            self.string_match,
            lambda x: self.__get_translation(x.group(1)),
            string)

    def __get_translation(self, string):
        for dictionary in [self.settings, PLAYOFF_I18N_DEFAULTS]:
            if string in dictionary:
                return dictionary[string].decode('utf8')
        return string
