from jfr_playoff.logger import PlayoffLogger


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


class TournamentInfo:

    def __init__(self, settings, database):
        self.settings = settings
        from jfr_playoff.tournamentinfo.jfrdb import JFRDbTournamentInfo
        from jfr_playoff.tournamentinfo.jfrhtml import JFRHtmlTournamentInfo
        from jfr_playoff.tournamentinfo.tcjson import TCJsonTournamentInfo
        self.clients = []
        if (database is not None) and ('database' in self.settings):
            self.clients.append(JFRDbTournamentInfo(settings, database))
        if 'link' in self.settings:
            if self.settings['link'].endswith('leaderb.html'):
                self.clients.append(JFRHtmlTournamentInfo(settings))
            self.clients.append(TCJsonTournamentInfo(settings))

    def get_tournament_results(self):
        teams = self.__call_client('get_tournament_results', [])
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
        return self.__call_client('is_finished', True)

    def get_results_link(self, suffix='leaderb.html'):
        return self.__call_client('get_results_link', None, suffix)

    def __call_client(self, method, default, *args):
        PlayoffLogger.get('tournamentinfo').info(
            'calling %s on tournament info clients', method)
        for client in self.clients:
            try:
                ret = getattr(client, method)(*args)
                PlayoffLogger.get('tournamentinfo').info(
                    '%s method returned %s', method, ret)
                return ret
            except Exception as e:
                if type(e) in client.get_exceptions(method):
                    PlayoffLogger.get('tournamentinfo').warning(
                        '%s method raised %s(%s)',
                        method, type(e).__name__, str(e))
                else:
                    raise
        PlayoffLogger.get('tournamentinfo').info(
            '%s method returning default: %s', method, default)
        return default
