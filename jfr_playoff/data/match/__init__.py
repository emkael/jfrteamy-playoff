from jfr_playoff.data.info import ResultInfoClient


class MatchInfoClient(ResultInfoClient):
    def get_match_link(self):
        raise NotImplementedError

    def fetch_teams(self, teams):
        raise NotImplementedError

    def board_count(self):
        raise NotImplementedError

    def running_link(self):
        raise NotImplementedError


CLIENTS = [
    'jfr_playoff.data.match.jfrdb',
    'jfr_playoff.data.match.jfrhtml',
    'jfr_playoff.data.match.tcjson'
]
