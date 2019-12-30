from jfr_playoff.data import TournamentInfo
from jfr_playoff.data.match import MatchInfoClient
from jfr_playoff.logger import PlayoffLogger


class JFRDbMatchInfo(MatchInfoClient):
    @property
    def priority(self):
        return 50

    def is_capable(self):
        return (self.database is not None) and ('database' in self.settings)

    def get_exceptions(self, method):
        return (IOError, TypeError, IndexError, KeyError)

    def get_match_link(self):
        if 'link' in self.settings:
            raise NotImplementedError(
                'link specified in config, skipping lookup')
        if 'round' not in self.settings:
            raise IndexError('round number not specified in match config')
        event_info = TournamentInfo(self.settings, self.database)
        link = event_info.get_results_link(
            'runda%d.html' % (self.settings['round']))
        PlayoffLogger.get('match.jfrdb').info(
            'match #%d link fetched: %s', self.settings['id'], link)
        return link
