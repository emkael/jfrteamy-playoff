import mysql
from cached_property import cached_property

import jfr_playoff.sql as p_sql
from jfr_playoff.db import PlayoffDB
from jfr_playoff.dto import Phase
from jfr_playoff.matchinfo import MatchInfo

SWISS_TIE_WARNING = 'WARNING: tie detected in swiss %s.' + \
                    ' Make sure to resolve the tie by arranging teams' + \
                    ' in configuration file.'


class PlayoffData(object):
    def __init__(self, settings):
        self.database = PlayoffDB(settings.get('database')) if settings.has_section('database') else None
        if self.database is None:
            print PlayoffDB.DATABASE_NOT_CONFIGURED_WARNING
        self.team_settings = settings.get('teams')
        self.phases = settings.get('phases')
        self.swiss = []
        if settings.has_section('swiss'):
            self.swiss = settings.get('swiss')
        self.grid = []
        self.match_info = {}
        self.leaderboard = []

    @cached_property
    def teams(self):
        if isinstance(self.team_settings, list):
            return self.team_settings
        db_teams = self.get_swiss_results(
            self.team_settings['database'],
            self.team_settings['ties'] if 'ties' in self.team_settings else [])
        if 'final_positions' in self.team_settings:
            for position in self.team_settings['final_positions']:
                db_teams[position-1].append(position)
        return db_teams

    def generate_phases(self):
        self.grid = []
        for phase in self.phases:
            phase_count = len(phase['matches'])
            if 'dummies' in phase:
                phase_count += len(phase['dummies'])
            phase_object = Phase()
            phase_object.title = phase['title']
            phase_object.link = phase['link']
            phase_object.matches = [None] * phase_count
            phase_pos = 0
            for match in phase['matches']:
                if 'dummies' in phase:
                    while phase_pos in phase['dummies']:
                        phase_pos += 1
                phase_object.matches[phase_pos] = match['id']
                phase_pos += 1
            self.grid.append(phase_object)
        return self.grid

    def fill_match_info(self):
        self.match_info = {}
        for phase in self.phases:
            for match in phase['matches']:
                match_info = MatchInfo(match, self.teams, self.database)
                match_info.set_phase_link(phase['link'])
                self.match_info[match['id']] = match_info.get_info()
                if self.match_info[match['id']].running > 0:
                    for phase_obj in self.grid:
                        if match['id'] in phase_obj.matches:
                            phase_obj.running = True
        return self.match_info

    def get_leaderboard_link(self, database):
        return self.__get_link(database, 'leaderb.html')

    def get_swiss_link(self, event):
        swiss_link = self.get_leaderboard_link(event['database'])
        if ('relative_path' in event) and (
                event['relative_path'] is not None):
            swiss_link = '%s/%s' % (event['relative_path'], swiss_link)
        return swiss_link

    def prefill_leaderboard(self, teams):
        self.leaderboard = [None] * len(teams)
        for team in teams:
            if len(team) > 3:
                self.leaderboard[team[3]-1] = team[0]
        self.fill_swiss_leaderboard(self.swiss, teams)
        return self.leaderboard

    def fill_swiss_leaderboard(self, swiss, teams):
        teams = [team[0] for team in teams]
        if self.database is None:
            return
        for event in swiss:
            swiss_finished = self.database.fetch(
                event['database'], p_sql.SWISS_ENDED, {})
            if len(swiss_finished) > 0:
                if swiss_finished[0] > 0:
                    swiss_position = (
                        event['swiss_position']
                        if 'swiss_position' in event
                        else 1
                    )
                    position_limit = (
                        event['position_to']
                        if 'position_to' in event
                        else 9999
                    )
                    place = 1
                    swiss_results = self.get_swiss_results(
                        event['database'], teams)
                    for team in swiss_results:
                        if place >= swiss_position:
                            target_position = event['position'] \
                                              + place - swiss_position
                            if target_position <= min(
                                    position_limit, len(self.leaderboard)):
                                self.leaderboard[
                                    target_position - 1] = team[0]
                        place += 1

    def get_swiss_results(self, swiss, ties=None):
        if ties is None:
            ties = []
        if self.database is None:
            return []
        swiss_teams = self.database.fetch_all(
            swiss, p_sql.SWISS_RESULTS, {})
        swiss_results = sorted(
            swiss_teams,
            key=lambda t: ties.index(t[0]) if t[0] in ties else -1)
        swiss_results = sorted(
            swiss_results, key=lambda t: t[1], reverse=True)
        swiss_results = sorted(swiss_results, key=lambda team: team[2])
        prev_result = None
        for team in swiss_results:
            if prev_result == team[1]:
                print SWISS_TIE_WARNING % (swiss)
            prev_result = team[1]
        return [[team[0], team[3], team[4]] for team in swiss_results]

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
        for positions, position_teams in leaderboard_teams.iteritems():
            positions = list(positions)
            if len(positions) == len([
                    team for team in position_teams if team is not None]):
                for table_team in self.teams:
                    if table_team[0] in position_teams:
                        position = positions.pop(0)
                        self.leaderboard[position-1] = table_team[0]
        return self.leaderboard

    def get_swiss_info(self):
        return [{
            'link': self.get_swiss_link(event),
            'position': event['position'],
            'label': event['label'] if 'label' in event else None
        } for event in self.swiss]

    def get_dimensions(self):
        return (
            len(self.phases),
            max([
                len(phase['matches']) + len(phase['dummies'])
                if 'dummies' in phase
                else len(phase['matches'])
                for phase in self.phases]))

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
