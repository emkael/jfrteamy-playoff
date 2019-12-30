import urlparse

from jfr_playoff.data.match import MatchInfoClient
from jfr_playoff.logger import PlayoffLogger


class TCJsonMatchInfo(MatchInfoClient):
    @property
    def priority(self):
        return 20

    def is_capable(self):
        return ('link' in self.settings) and ('#' in self.settings['link'])

    def get_exceptions(self, method):
        return (TypeError, IndexError, KeyError, IOError, ValueError)

    def _get_round_from_link(self, link):
        fragment = urlparse.urlparse(link).fragment
        return fragment[11:14], fragment[14:17]

    def get_match_link(self):
        PlayoffLogger.get('match.tcjson').info(
            'match #%d link pre-defined: %s',
            self.settings['id'], self.settings['link'])
        return self.settings['link']
