from cached_property import cached_property

from jfr_playoff.db import PlayoffDB
from jfr_playoff.dto import Phase
from jfr_playoff.data.info import TournamentInfo, MatchInfo
from jfr_playoff.logger import PlayoffLogger


class PlayoffData(object):
    def __init__(self, settings=None):
        if settings is not None:
            self.database = PlayoffDB(settings.get('database')) \
                if settings.has_section('database') else None
            if self.database is None:
                PlayoffLogger.get('db').warning(
                    PlayoffDB.DATABASE_NOT_CONFIGURED_WARNING)
            self.team_settings = settings.get('teams')
            self.custom_final_order = []
            if settings.has_section('custom_final_order'):
                self.custom_final_order = settings.get('custom_final_order')
            self.custom_final_order = [
                t for t in [
                    self.teams[i-1] if isinstance(i, int)
                    else self.get_team_data_by_name(i)
                    for i in self.custom_final_order]
                if t is not None]
            self.phases = settings.get('phases')
            self.swiss = []
            if settings.has_section('swiss'):
                self.swiss = settings.get('swiss')
            self.aliases = {}
            if settings.has_section('team_aliases'):
                self.aliases = settings.get('team_aliases')
        self.grid = []
        self.match_info = {}
        self.leaderboard = []

    def fetch_team_list(self, settings, db_interface):
        if isinstance(settings, list):
            PlayoffLogger.get('data').info(
                'team list pre-defined: %s', settings)
            return settings
        tournament_info = TournamentInfo(settings, db_interface)
        team_list = tournament_info.get_tournament_results()
        if len(team_list) == 0:
            PlayoffLogger.get('data').warning('team list is empty!')
        return team_list if 'max_teams' not in settings \
            else team_list[0:settings['max_teams']]

    @cached_property
    def teams(self):
        return self.fetch_team_list(self.team_settings, self.database)

    def generate_phases(self):
        self.grid = []
        for phase in self.phases:
            dummies = phase.get('dummies', [])
            phase_count = len(phase['matches']) + len(dummies)
            phase_object = Phase()
            phase_object.title = phase['title']
            phase_object.link = phase.get('link', None)
            phase_object.matches = [None] * phase_count
            phase_pos = 0
            for match in phase['matches']:
                while phase_pos in dummies:
                    phase_pos += 1
                phase_object.matches[phase_pos] = match['id']
                phase_pos += 1
            PlayoffLogger.get('data').info('phase object: %s', phase_object)
            self.grid.append(phase_object)
        return self.grid

    def fill_match_info(self):
        self.match_info = {}
        for phase in self.phases:
            for match in phase['matches']:
                match_info = MatchInfo(match, self.teams, self.database, self.aliases)
                if 'link' in phase:
                    match_info.set_phase_link(phase['link'])
                self.match_info[match['id']] = match_info.get_info()
                if self.match_info[match['id']].running > 0:
                    for phase_obj in self.grid:
                        if match['id'] in phase_obj.matches:
                            phase_obj.running = True
                PlayoffLogger.get('data').info(
                    'match object: %s', self.match_info[match['id']])
        return self.match_info

    def get_swiss_link(self, event):
        event_info = TournamentInfo(event, self.database)
        swiss_link = event_info.get_results_link()
        if event.get('relative_path', None):
            swiss_link = '%s/%s' % (event['relative_path'], swiss_link)
        PlayoffLogger.get('data').info('swiss link: %s', swiss_link)
        return swiss_link

    def prefill_leaderboard(self, teams):
        self.leaderboard = [None] * len(teams)
        for team in teams:
            if len(team) > 3 and team[3] is not None:
                self.leaderboard[team[3]-1] = team[0]
        self.fill_swiss_leaderboard(self.swiss, teams)
        PlayoffLogger.get('data').info('leaderboard pre-filled: %s', self.leaderboard)
        return self.leaderboard

    def fill_swiss_leaderboard(self, swiss, teams):
        teams = [team[0] for team in teams]
        for event in swiss:
            event['ties'] = teams
            event_info = TournamentInfo(event, self.database)
            if event_info.is_finished():
                swiss_position = event.get('swiss_position', 1)
                position_limit = event.get('position_to', 9999)
                place = 1
                swiss_results = event_info.get_tournament_results()
                for team in swiss_results:
                    if place >= swiss_position:
                        target_position = event['position'] \
                                          + place - swiss_position
                        if target_position <= min(
                                position_limit, len(self.leaderboard)):
                            self.leaderboard[
                                target_position - 1] = team[0]
                    place += 1
            PlayoffLogger.get('data').info(
                'leaderboard after %s swiss: %s', event, self.leaderboard)

    def fill_leaderboard(self):
        self.prefill_leaderboard(self.teams)
        leaderboard_teams = {}
        for phase in self.phases:
            for match in phase['matches']:
                if 'winner' in match:
                    winner_key = tuple(match['winner'])
                    if winner_key not in leaderboard_teams:
                        leaderboard_teams[winner_key] = []
                    leaderboard_teams[winner_key].append(
                        self.match_info[match['id']].winner)
                if 'loser' in match:
                    loser_key = tuple(match['loser'])
                    if loser_key not in leaderboard_teams:
                        leaderboard_teams[loser_key] = []
                    leaderboard_teams[loser_key].append(
                        self.match_info[match['id']].loser)
        final_order = self.custom_final_order + [
            t for t in self.teams if t not in self.custom_final_order]
        PlayoffLogger.get('data').info(
                'custom order for final positions: %s', self.custom_final_order)
        PlayoffLogger.get('data').info(
                'order of teams to fill leaderboard positions: %s',
                final_order)
        for positions, position_teams in leaderboard_teams.iteritems():
            positions = list(positions)
            PlayoffLogger.get('data').info(
                'filling leaderboard positions %s with teams %s',
                positions, position_teams)
            if len(positions) == len([
                    team for team in position_teams if team is not None]):
                for table_team in final_order:
                    if table_team[0] in position_teams:
                        position = positions.pop(0)
                        self.leaderboard[position-1] = table_team[0]
                        PlayoffLogger.get('data').info(
                            'team %s in position %d', table_team[0], position)
        PlayoffLogger.get('data').info(
            'leaderboard filled: %s', self.leaderboard)
        return self.leaderboard

    def get_swiss_info(self):
        swiss_info = [{
            'link': self.get_swiss_link(event),
            'position': event['position'],
            'label': event.get('label', None),
            'finished': TournamentInfo(event, self.database).is_finished()
        } for event in self.swiss]
        PlayoffLogger.get('data').info('swiss info: %s', swiss_info)
        return swiss_info

    def get_dimensions(self):
        dimensions = (
            len(self.phases),
            max([
                len(phase['matches']) + len(phase.get('dummies', []))
                for phase in self.phases
            ] or [0])
        )
        PlayoffLogger.get('data').info('grid dimensions: %s', dimensions)
        return dimensions

    def get_team_data_by_name(self, fullname):
        for team in self.teams:
            if team[0] == fullname:
                return team
        return None

    def get_shortname(self, fullname):
        for team in self.teams:
            if team[0] == fullname:
                return team[1]
        return fullname

    def get_team_image(self, fullname):
        for team in self.teams:
            if team[0] == fullname and len(team) > 2:
                return team[2]
        return None
