# -*- coding: utf-8 -*-

import re

from jfr_playoff.logger import PlayoffLogger

PLAYOFF_I18N_DEFAULTS = {
    'SCORE': u'wynik',
    'FINAL_STANDINGS': u'klasyfikacja końcowa',
    'STANDINGS_PLACE': u'miejsce',
    'STANDINGS_TEAM': u'drużyna',
    'STANDINGS_CAPTIONS': u'legenda',
    'FOOTER_GENERATED': u'strona wygenerowana',
    'SWISS_DEFAULT_LABEL': u'Turniej o&nbsp;%d.&nbsp;miejsce',
    'DETERMINED_TEAMS': u'Drużyny z pewnym miejscem w tej fazie:',
    'POSSIBLE_TEAMS': u'Drużyny z trwających meczów poprzedniej fazy:'
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
                translation = dictionary[string]
                PlayoffLogger.get('i18n').info(
                    'translation for %s: %s', string, translation)
                return translation
        PlayoffLogger.get('i18n').info(
            'translation for %s not found', string)
        return '{{%s}}' % (string)
