import mysql

import jfr_playoff.sql as p_sql
from jfr_playoff.remote import RemoteUrl as p_remote

SWISS_TIE_WARNING = 'WARNING: tie detected in swiss %s.' + \
                    ' Make sure to resolve the tie by arranging teams' + \
                    ' in configuration file.'


class TournamentInfo:

    def __init__(self, settings, database):
        self.settings = settings
        self.database = database

    def __get_html_results(self):
        return []

    def __get_db_results(self):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
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
        prev_result = None
        for team in swiss_results:
            if prev_result == team[1]:
                print SWISS_TIE_WARNING % (self.settings['database'])
            prev_result = team[1]
        db_teams = [[team[0], team[3], team[4]] for team in swiss_results]
        if 'final_positions' in self.settings:
            for position in self.settings['final_positions']:
                db_teams[position-1].append(position)
        return db_teams

    def __get_html_finished(self):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('unable to determine tournament status')
        leaderboard = p_remote.fetch(self.settings['link'])
        leaderb_heading = leaderboard.select('td.bdnl12')[0].text
        non_zero_scores = [imps.text for imps in leaderboard.select('td.bdc small') if imps.text != '0-0']
        return (not any(char.isdigit() for char in leaderb_heading)) and (len(non_zero_scores) > 0)

    def __get_db_finished(self):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        finished = self.database.fetch(
            self.settings['database'], p_sql.SWISS_ENDED, {})
        return (len(finished) > 0) and (finished[0] > 0)

    def __get_html_link(self, suffix='leaderb.html'):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('unable to determine html link')
        return re.sub(r'leaderb.html$', suffix, self.settings['link'])

    def __get_db_link(self, suffix='leaderb.html'):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        row = self.database.fetch(
            self.settings['database'], p_sql.PREFIX, ())
        if row is not None:
            if len(row) > 0:
                return row[0] + suffix
        raise ValueError('unable to fetch db link')

    def get_tournament_results(self):
        try:
            return self.__get_db_results()
        except (mysql.connector.Error, TypeError, IndexError, KeyError):
            try:
                return self.__get_html_results()
            except (TypeError, IndexError, KeyError, IOError, ValueError):
                pass
        return []

    def is_finished(self):
        try:
            return self.__get_db_finished()
        except (mysql.connector.Error, TypeError, IndexError, KeyError):
            try:
                return self.__get_html_finished()
            except (TypeError, IndexError, KeyError, IOError, ValueError):
                pass
        return True

    def get_results_link(self, suffix='leaderb.html'):
        try:
            return self.__get_db_link(suffix)
        except (mysql.connector.Error, TypeError, IndexError, KeyError):
            try:
                return self.__get_html_link(suffix)
            except (KeyError, ValueError):
                pass
        return None
