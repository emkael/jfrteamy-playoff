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
