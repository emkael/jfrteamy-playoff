from jfr_playoff.data.info import ResultInfoClient


class TournamentInfoClient(ResultInfoClient):
    def get_results_link(self, suffix):
        raise NotImplementedError

    def is_finished(self):
        raise NotImplementedError

    def get_tournament_results(self):
        raise NotImplementedError


CLIENTS = [
    'jfr_playoff.data.tournament.jfrdb',
    'jfr_playoff.data.tournament.jfrhtml',
    'jfr_playoff.data.tournament.tcjson'
]
