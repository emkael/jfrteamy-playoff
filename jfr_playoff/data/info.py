import copy
from decimal import Decimal
import inspect
from urlparse import urljoin

from jfr_playoff.dto import Match, Team
from jfr_playoff.logger import PlayoffLogger


class ResultInfoClient(object):
    def __init__(self, settings, database=None):
        self.settings = settings
        self.database = database

    @property
    def priority(self):
        return 0

    def is_capable(self):
        return False

    def get_exceptions(self, method):
        pass


class ResultInfo(object):
    def __init__(self, *args):
        self.clients = self._fill_client_list(*args)

    @property
    def submodule_path(self):
        raise NotImplementedError()

    @property
    def _client_classes(self):
        module = __import__(self.submodule_path, fromlist=[''])
        for submodule_path in module.CLIENTS:
            submodule = __import__(submodule_path, fromlist=[''])
            for member in inspect.getmembers(submodule, inspect.isclass):
                if member[1].__module__ == submodule_path:
                    yield member[1]

    def _fill_client_list(self, *args):
        all_clients = [c(*args) for c in self._client_classes]
        clients = [c for c in all_clients if c.is_capable()]
        return sorted(clients, key=lambda c: c.priority, reverse=True)

    def call_client(self, method, default, *args):
        PlayoffLogger.get('resultinfo').info(
            'calling %s on result info clients', method)
        for client in self.clients:
            try:
                ret = getattr(client, method)(*args)
                PlayoffLogger.get('resultinfo').info(
                    '%s.%s method returned %s',
                    client.__class__.__name__, method, ret)
                return ret
            except Exception as e:
                if type(e) \
                   in client.get_exceptions(method) + (NotImplementedError,):
                    PlayoffLogger.get('resultinfo').warning(
                        '%s.%s method raised %s(%s)',
                        client.__class__.__name__, method,
                        type(e).__name__, str(e))
                else:
                    raise
        PlayoffLogger.get('resultinfo').info(
            '%s method returning default: %s', method, default)
        return default


class TournamentInfo(ResultInfo):
    def __init__(self, settings, database):
        ResultInfo.__init__(self, settings, database)
        self.final_positions = settings.get('final_positions', [])

    @property
    def submodule_path(self):
        return 'jfr_playoff.data.tournament'

    def get_tournament_results(self):
        teams = self.call_client('get_tournament_results', [])
        if self.is_finished():
            PlayoffLogger.get('tournamentinfo').info(
                'setting final positions from tournament results: %s',
                self.final_positions)
            for position in self.final_positions:
                if len(teams) >= position:
                    teams[position-1] = (teams[position-1] + [None] * 4)[0:4]
                    teams[position-1][3] = position
        return teams

    def is_finished(self):
        return self.call_client('is_finished', True)

    def get_results_link(self, suffix='leaderb.html'):
        return self.call_client('get_results_link', None, suffix)


class MatchInfo(ResultInfo):

    matches = {}

    def __init__(self, match_config, teams, database,
                 aliases=None, starting_positions_certain=True, auto_carryover=False):
        ResultInfo.__init__(self, match_config, database)
        self.config = match_config
        self.teams = teams
        self.teams_by_name = { team[0]: team for team in self.teams }
        self.database = database
        self.aliases = {}
        if aliases:
            for team, team_aliases in aliases.iteritems():
                for alias in team_aliases:
                    self.aliases[alias] = team
        self._starting_positions_certain = starting_positions_certain
        self._auto_carryover = auto_carryover
        self.info = Match()
        self._init_info()
        self._fetch_match_link()

    @property
    def submodule_path(self):
        return 'jfr_playoff.data.match'

    def _init_info(self):
        self.info.id = self.config['id']
        MatchInfo.matches[self.info.id] = self.info
        self.info.running = 0
        self.info.winner_matches = []
        self.info.loser_matches = []
        for i in range(0, 2):
            if 'winner' in self.config['teams'][i]:
                self.info.winner_matches += self.config['teams'][i]['winner']
            if 'loser' in self.config['teams'][i]:
                self.info.loser_matches += self.config['teams'][i]['loser']
        self.info.winner_matches = list(set(self.info.winner_matches))
        self.info.loser_matches = list(set(self.info.loser_matches))
        self.info.winner_place = self.config.get('winner', [])
        self.info.loser_place = self.config.get('loser', [])
        self.info.teams = []

    def _fetch_match_link(self):
        link = self.call_client('get_match_link', None)
        if link is not None:
            self.info.link = link
        else:
            PlayoffLogger.get('matchinfo').info(
                'match #%d link empty', self.info.id)

    def _get_predefined_scores(self):
        teams = [Team(), Team()]
        scores_fetched = False
        teams_fetched = False
        if 'score' in self.config:
            i = 0
            for score in self.config['score']:
                if isinstance(self.config['score'], dict):
                    teams[i].score = self.config['score'][score]
                    try:
                        team_no = int(score)
                        teams[i].name = [self.teams[team_no-1][0]]
                    except ValueError:
                        teams[i].name = [score]
                    teams_fetched = True
                else:
                    teams[i].score = score
                i += 1
                if i == 2:
                    break
            scores_fetched = True
            PlayoffLogger.get('matchinfo').info(
                'pre-defined scores for match #%d: %s',
                self.info.id, teams)
        return scores_fetched, teams_fetched, teams

    def _get_config_teams(self, teams):
        for i in range(0, 2):
            match_teams = []
            possible_teams = []
            if isinstance(self.config['teams'][i], basestring):
                match_teams = [self.config['teams'][i]]
            elif isinstance(self.config['teams'][i], list):
                match_teams = self.config['teams'][i]
            else:
                if 'winner' in self.config['teams'][i]:
                    match_teams += [
                        MatchInfo.matches[winner_match].winner
                        for winner_match in self.config['teams'][i]['winner']]
                    possible_teams += [
                        MatchInfo.matches[winner_match].possible_winner
                        for winner_match in self.config['teams'][i]['winner']]
                if 'loser' in self.config['teams'][i]:
                    match_teams += [
                        MatchInfo.matches[loser_match].loser
                        for loser_match in self.config['teams'][i]['loser']]
                    possible_teams += [
                        MatchInfo.matches[loser_match].possible_loser
                        for loser_match in self.config['teams'][i]['loser']]
                if 'place' in self.config['teams'][i]:
                    placed_teams = [
                        self.teams[place-1][0]
                        for place in self.config['teams'][i]['place']]
                    if self._starting_positions_certain:
                        match_teams += placed_teams
                        possible_teams += [None] * len(placed_teams)
                    else:
                        possible_teams += placed_teams
                        match_teams += [None] * len(placed_teams)
            teams[i].name = match_teams
            teams[i].possible_name = possible_teams
            teams[i].unknown_teams = len([team for team in match_teams if team is None])
            teams[i].selected_team = -1
            if 'selected_teams' in self.config \
               and not teams[i].unknown_teams:
                teams[i].selected_team = self.config['selected_teams'][i]
            teams[i].known_teams = 1 if teams[i].selected_team >= 0 else len([
                team for team in match_teams if team is not None])
        PlayoffLogger.get('matchinfo').info(
            'config scores for match #%d: %s',
            self.info.id, teams)
        return teams

    def _resolve_team_aliases(self, teams):
        return [
            self.aliases[team]
            if team in self.aliases
            else team
            for team in teams]

    def _fetch_teams_with_scores(self):
        (scores_fetched, teams_fetched, self.info.teams) = \
            self._get_predefined_scores()
        if scores_fetched:
            self.info.running = int(self.config.get('running', -1))
        if not teams_fetched:
            teams = self.call_client(
                'fetch_teams', None,
                copy.deepcopy(self.info.teams))
            if teams is None:
                PlayoffLogger.get('matchinfo').warning(
                    'fetching teams for match #%d failed, reverting to config',
                    self.info.id)
                self.info.teams = self._get_config_teams(self.info.teams)
            else:
                self.info.teams = teams
        for team in range(0, len(self.info.teams)):
            if isinstance(self.config['teams'][team], dict):
                self.info.teams[team].place = self.config['teams'][team].get(
                    'place', self.info.teams[team].place)
            self.info.teams[team].name = self._resolve_team_aliases(
                self.info.teams[team].name)
            PlayoffLogger.get('matchinfo').info(
                'team list after resolving aliases: %s',
                self.info.teams[team].name)
            self.info.teams[team].possible_name = self._resolve_team_aliases(
                self.info.teams[team].possible_name)
            PlayoffLogger.get('matchinfo').info(
                'predicted team list after resolving aliases: %s',
                self.info.teams[team].possible_name)

    def _fetch_board_count(self):
        boards_played, boards_to_play = self.call_client(
            'board_count', (0, 0))
        if boards_played > 0:
            self.info.running = -1 \
                if boards_played >= boards_to_play \
                   else boards_played

    def _determine_outcome(self):
        if (self.info.teams[0].known_teams == 1) \
           and (self.info.teams[1].known_teams == 1) \
           and (self.info.teams[0].unknown_teams == 0) \
           and (self.info.teams[1].unknown_teams == 0):
            teams = [
                team.selected_name
                for team in self.info.teams
            ]
            if self.info.running == -1:
                if self.info.teams[0].score > self.info.teams[1].score:
                    self.info.winner = teams[0]
                    self.info.loser = teams[1]
                else:
                    self.info.loser = teams[0]
                    self.info.winner = teams[1]
            elif self.info.running > 0:
                if self.info.teams[0].score > self.info.teams[1].score:
                    self.info.possible_winner = teams[0]
                    self.info.possible_loser = teams[1]
                elif self.info.teams[0].score < self.info.teams[1].score:
                    self.info.possible_loser = teams[0]
                    self.info.possible_winner = teams[1]
            elif self.info.running == 0:
                if self._auto_carryover:
                    team_data = [self.teams_by_name.get(team, []) for team in teams]
                    if len(team_data[0]) > 4 and len(team_data[1]) > 4:
                        carry_over = self._auto_carryover / Decimal(100.0) * Decimal(team_data[0][4] - team_data[1][4])
                        if carry_over > 0:
                            self.info.teams[0].score = carry_over
                            self.info.teams[1].score = 0.0
                        else:
                            self.info.teams[0].score = 0.0
                            self.info.teams[1].score = -carry_over
                        PlayoffLogger.get('matchinfo').info(
                            'calculated carry-over for match #%d: %s, team data: %s',
                            self.info.id, carry_over, self.info.teams)


    def _determine_running_link(self):
        if self.info.link is None:
            return
        self.info.link = self.call_client('running_link', self.info.link)

    def set_phase_link(self, phase_link):
        prev_link = self.info.link
        if self.info.link is None:
            self.info.link = phase_link
        else:
            if self.info.link != '#':
                self.info.link = urljoin(phase_link, self.info.link)
        PlayoffLogger.get('matchinfo').info(
            'applying phase link %s to match #%d: %s',
            phase_link, self.info.id, self.info.link)
        # re-init result info clients
        if (prev_link != self.info.link) and (self.info.link is not None):
            PlayoffLogger.get('matchinfo').info(
                'config link changed, re-initializing result info client list')
            self.config['link'] = self.info.link
            ResultInfo.__init__(self, self.config, self.database)

    def get_info(self):
        self._fetch_teams_with_scores()
        self._fetch_board_count()
        self._determine_outcome()
        if self.info.running > 0:
            self._determine_running_link()
        return self.info
