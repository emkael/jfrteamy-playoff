import mysql

import jfr_playoff.sql as p_sql

SWISS_TIE_WARNING = 'WARNING: tie detected in swiss %s.' + \
                    ' Make sure to resolve the tie by arranging teams' + \
                    ' in configuration file.'


class TournamentInfo:

    def __init__(self, settings, database):
        self.settings = settings
        self.database = database

    def get_tournament_results(self):
        if self.database is None:
            return []
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

    def is_finished(self):
        finished = self.database.fetch(
            self.settings['database'], p_sql.SWISS_ENDED, {})
        return (len(finished) > 0) and (finished[0] > 0)

    def get_results_link(self, suffix='leaderb.html'):
        if self.database is None:
            return None
        try:
            row = self.database.fetch(
                self.settings['database'], p_sql.PREFIX, ())
            if row is not None:
                if len(row) > 0:
                    return row[0] + suffix
        except mysql.connector.Error:
            return None
        return None
