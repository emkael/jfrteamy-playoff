from urlparse import urljoin

import mysql

import jfr_playoff.sql as p_sql
from jfr_playoff.db import PlayoffDB
from jfr_playoff.dto import Match, Phase, Team


class PlayoffData(object):
    def __init__(self, settings):
        self.settings = settings
        self.database = PlayoffDB(self.settings.get('database'))
        self.phases = self.settings.get('phases')
        self.teams = self.settings.get('teams')
        self.grid = []
        self.match_info = {}
        self.leaderboard = []

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
                self.match_info[match['id']] = self.get_match_info(match)
                if self.match_info[match['id']].running > 0:
                    for phase_obj in self.grid:
                        if match['id'] in phase_obj.matches:
                            phase_obj.running = True
                if self.match_info[match['id']].link is None:
                    self.match_info[match['id']].link = phase['link']
                else:
                    self.match_info[match['id']].link = urljoin(
                        phase['link'], self.match_info[match['id']].link
                    )
        return self.match_info

    def get_match_link(self, match):
        try:
            row = self.database.fetch(match['database'], p_sql.PREFIX, ())
            if row is not None:
                if len(row) > 0:
                    return '%srunda%d.html' % (row[0], match['round'])
        except mysql.connector.Error:
            return None
        return None

    def get_db_match_teams(self, match):
        teams = [Team(), Team()]
        row = self.database.fetch(
            match['database'], p_sql.MATCH_RESULTS,
            (match['table'], match['round'])
        )
        teams[0].name = row[0]
        teams[1].name = row[1]
        teams[0].score = row[3] + row[5]
        teams[1].score = row[4] + row[6]
        if row[2] > 0:
            teams[0].score += row[2]
        else:
            teams[1].score -= row[2]
        return teams

    def get_config_match_teams(self, match):
        teams = [Team(), Team()]
        for i in range(0, 2):
            if isinstance(match['teams'][i], basestring):
                teams[i].name = match['teams'][i]
            elif isinstance(match['teams'][i], list):
                teams[i].name = '<br />'.join(match['teams'][i])
            else:
                match_teams = []
                if 'winner' in match['teams'][i]:
                    match_teams += [
                        self.match_info[winner_match].winner
                        for winner_match in match['teams'][i]['winner']
                    ]
                if 'loser' in match['teams'][i]:
                    match_teams += [
                        self.match_info[loser_match].loser
                        for loser_match in match['teams'][i]['loser']
                    ]
                if 'place' in match['teams'][i]:
                    match_teams += [
                        self.teams[place-1][0]
                        for place in match['teams'][i]['place']
                    ]
            known_teams = [team for team in match_teams if team is not None]
            if len(known_teams) > 0:
                teams[i].name = '<br />'.join([
                    team if team is not None else '??' for team in match_teams])
            else:
                teams[i].name = ''
        return teams


    def get_match_info(self, match):
        info = Match()
        info.id = match['id']
        info.winner_matches = []
        info.loser_matches = []
        for i in range(0, 2):
            if 'winner' in match['teams'][i]:
                info.winner_matches += match['teams'][i]['winner']
            if 'loser' in match['teams'][i]:
                info.loser_matches += match['teams'][i]['loser']
        info.winner_matches = list(set(info.winner_matches))
        info.loser_matches = list(set(info.loser_matches))
        info.link = self.get_match_link(match)
        try:
            info.teams = self.get_db_match_teams(match)
        except (mysql.connector.Error, TypeError, IndexError):
            info.teams = self.get_config_match_teams(match)
        try:
            towels = self.database.fetch(
                match['database'], p_sql.TOWEL_COUNT,
                (match['table'], match['round'])
            )
            row = [0 if r is None
                   else r for r in
                   self.database.fetch(
                       match['database'], p_sql.BOARD_COUNT,
                       (match['table'], match['round'])
                   )]
            if row[1] > 0:
                info.running = int(row[1])
            if row[1] >= row[0] - towels[0]:
                info.running = 0
                if info.teams[0].score > info.teams[1].score:
                    info.winner = info.teams[0].name
                    info.loser = info.teams[1].name
                else:
                    info.loser = info.teams[0].name
                    info.winner = info.teams[1].name
        except (mysql.connector.Error, TypeError, KeyError):
            pass
        return info

    def prefill_leaderboard(self, teams):
        self.leaderboard = [None] * len(teams)
        for team in teams:
            if len(team) > 3:
                self.leaderboard[team[3]-1] = team[0]
        return self.leaderboard

    def fill_leaderboard(self):
        self.prefill_leaderboard(self.teams)
        leaderboard_teams = {}
        for phase in self.phases:
            for match in phase['matches']:
                if 'winner' in match:
                    winner_key = tuple(match['winner'])
                    if winner_key not in leaderboard_teams:
                        leaderboard_teams[winner_key] = []
                    leaderboard_teams[winner_key].append(self.match_info[match['id']].winner)
                if 'loser' in match:
                    loser_key = tuple(match['loser'])
                    if loser_key not in leaderboard_teams:
                        leaderboard_teams[loser_key] = []
                    leaderboard_teams[loser_key].append(self.match_info[match['id']].loser)
        for positions, position_teams in leaderboard_teams.iteritems():
            positions = list(positions)
            if len(positions) == len([team for team in position_teams if team is not None]):
                for table_team in self.teams:
                    if table_team[0] in position_teams:
                        position = positions.pop(0)
                        self.leaderboard[position-1] = table_team[0]
        return self.leaderboard

    def get_dimensions(self):
        return (
            len(self.phases),
            max([
                len(phase['matches']) + len(phase['dummies'])
                if 'dummies' in phase
                else len(phase['matches'])
                for phase in self.phases
            ])
        )

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
