from jfr_playoff.logger import PlayoffLogger
from jfr_playoff.data import ResultInfo


class TournamentInfoClient(object):
    def __init__(self, settings, database=None):
        self.settings = settings
        self.database = database

    def get_results_link(self, suffix):
        pass

    def is_finished(self):
        pass

    def get_tournament_results(self):
        pass

    def get_exceptions(self, method):
        pass


class TournamentInfo(ResultInfo):
    def __init__(self, settings, database):
        self.settings = settings
        ResultInfo.__init__(self, settings, database)

    def fill_client_list(self, settings, database):
        clients = []
        from jfr_playoff.tournamentinfo.jfrdb import JFRDbTournamentInfo
        from jfr_playoff.tournamentinfo.jfrhtml import JFRHtmlTournamentInfo
        from jfr_playoff.tournamentinfo.tcjson import TCJsonTournamentInfo
        if (database is not None) and ('database' in settings):
            clients.append(JFRDbTournamentInfo(settings, database))
        if 'link' in settings:
            if settings['link'].endswith('leaderb.html'):
                clients.append(JFRHtmlTournamentInfo(settings))
            clients.append(TCJsonTournamentInfo(settings))
        return clients

    def get_tournament_results(self):
        teams = self.call_client('get_tournament_results', [])
        if self.is_finished():
            final_positions = self.settings.get('final_positions', [])
            PlayoffLogger.get('tournamentinfo').info(
                'setting final positions from tournament results: %s',
                final_positions)
            for position in final_positions:
                if len(teams) >= position:
                    teams[position-1] = (teams[position-1] + [None] * 4)[0:4]
                    teams[position-1][3] = position
        return teams

    def is_finished(self):
        return self.call_client('is_finished', True)

    def get_results_link(self, suffix='leaderb.html'):
        return self.call_client('get_results_link', None, suffix)
