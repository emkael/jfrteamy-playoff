from jfr_playoff.data.match import MatchInfoClient
from jfr_playoff.logger import PlayoffLogger


class JFRHtmlMatchInfo(MatchInfoClient):
    @property
    def priority(self):
        return 30

    def is_capable(self):
        return ('link' in self.settings) and ('#' not in self.settings['link'])

    def get_exceptions(self, method):
        return (TypeError, IndexError, KeyError, IOError, ValueError)

    def get_match_link(self):
        PlayoffLogger.get('match.jfrhtml').info(
            'match #%d link pre-defined: %s',
            self.settings['id'], self.settings['link'])
        return self.settings['link']
