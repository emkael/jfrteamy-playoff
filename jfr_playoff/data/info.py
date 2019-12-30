from jfr_playoff.logger import PlayoffLogger


class ResultInfo(object):
    def __init__(self, *args):
        self.clients = self.fill_client_list(*args)

    def fill_client_list(self, settings, database):
        return []

    def call_client(self, method, default, *args):
        PlayoffLogger.get('resultinfo').info(
            'calling %s on result info clients', method)
        for client in self.clients:
            try:
                ret = getattr(client, method)(*args)
                PlayoffLogger.get('resultinfo').info(
                    '%s method returned %s', method, ret)
                return ret
            except Exception as e:
                if type(e) in client.get_exceptions(method):
                    PlayoffLogger.get('resultinfo').warning(
                        '%s method raised %s(%s)',
                        method, type(e).__name__, str(e))
                else:
                    raise
        PlayoffLogger.get('resultinfo').info(
            '%s method returning default: %s', method, default)
        return default


from jfr_playoff.data.tournament.jfrdb import JFRDbTournamentInfo
from jfr_playoff.data.tournament.jfrhtml import JFRHtmlTournamentInfo
from jfr_playoff.data.tournament.tcjson import TCJsonTournamentInfo


class TournamentInfo(ResultInfo):
    def __init__(self, settings, database):
        self.settings = settings
        ResultInfo.__init__(self, settings, database)

    def fill_client_list(self, settings, database):
        clients = []
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
