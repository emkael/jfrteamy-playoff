from jfr_playoff.data.info import ResultInfoClient


class MatchInfoClient(ResultInfoClient):
    def get_match_link(self):
        raise NotImplementedError
