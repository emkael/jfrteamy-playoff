import jfr_playoff.sql as p_sql
from jfr_playoff.logger import PlayoffLogger
from jfr_playoff.data.tournament import TournamentInfoClient

SWISS_TIE_WARNING = 'tie detected in swiss %s.' + \
                    ' Make sure to resolve the tie by arranging teams' + \
                    ' in configuration file.'


class JFRDbTournamentInfo(TournamentInfoClient):
    @property
    def priority(self):
        return 50

    def is_capable(self):
        return (self.database is not None) and ('database' in self.settings)

    def get_exceptions(self, method):
        return (IOError, TypeError, IndexError, KeyError)

    def get_results_link(self, suffix='leaderb.html'):
        row = self.database.fetch(
            self.settings['database'], p_sql.PREFIX, ())
        if row is not None:
            if len(row) > 0:
                link = row[0] + suffix
                PlayoffLogger.get('tournament.jfrdb').info(
                    'generating tournament-specific link from DB %s prefix: %s -> %s',
                    self.settings['database'], suffix, link)
                return link
        raise ValueError('unable to fetch db link')

    def is_finished(self):
        finished = self.database.fetch(
            self.settings['database'], p_sql.SWISS_ENDED, {})
        PlayoffLogger.get('tournament.jfrdb').info(
            'fetching tournament finished status from DB %s: %s',
            self.settings['database'], finished)
        return (len(finished) > 0) and (finished[0] > 0)

    def get_tournament_results(self):
        if 'ties' not in self.settings:
            self.settings['ties'] = []
        swiss_teams = self.database.fetch_all(
            self.settings['database'], p_sql.SWISS_RESULTS, {})
        swiss_results = sorted(
            swiss_teams,
            key=lambda t: self.settings['ties'].index(t[0]) \
            if t[0] in self.settings['ties'] else -1)
        swiss_results = sorted(
            swiss_results, key=lambda t: t[1], reverse=True)
        swiss_results = sorted(swiss_results, key=lambda team: team[2])
        PlayoffLogger.get('tournament.jfrdb').info(
            'fetched tournament results from database %s: %s',
            self.settings['database'], swiss_results)
        prev_result = None
        for team in swiss_results:
            if prev_result == team[1]:
                PlayoffLogger.get('tournament.jfrdb').warning(
                    SWISS_TIE_WARNING, self.settings['database'])
            prev_result = team[1]
        db_teams = [[team[0], team[3], team[4]] for team in swiss_results]
        PlayoffLogger.get('tournament.jfrdb').info(
            'fetched team list from database %s: %s',
            self.settings['database'], db_teams)
        return db_teams
