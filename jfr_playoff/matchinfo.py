from urlparse import urljoin

import mysql

import jfr_playoff.sql as p_sql
from jfr_playoff.dto import Match, Team

class MatchInfo:

    matches = {}

    def __init__(self, match_config, teams, database):
        self.config = match_config
        self.teams = teams
        self.database = database
        self.info = Match()
        self.__init_info()
        self.__fetch_match_link()

    def __init_info(self):
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
        self.info.teams = []

    def __get_link(self, suffix):
        try:
            row = self.database.fetch(
                self.config['database'], p_sql.PREFIX, ())
            if row is not None:
                if len(row) > 0:
                    return row[0] + suffix
        except mysql.connector.Error:
            return None
        return None

    def __fetch_match_link(self):
        if 'link' in self.config:
            self.info.link = self.config['link']
        else:
            self.info.link = self.__get_link(
                'runda%d.html' % (self.config['round']))

    def __get_predefined_scores(self):
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
                        teams[i].name = self.teams[team_no-1][0]
                    except ValueError:
                        teams[i].name = score
                    teams_fetched = True
                else:
                    teams[i].score = score
                i += 1
                if i == 2:
                    break
            scores_fetched = True
        return scores_fetched, teams_fetched, teams

    def __get_db_teams(self, teams, fetch_scores):
        row = self.database.fetch(
            self.config['database'], p_sql.MATCH_RESULTS,
            (self.config['table'], self.config['round']))
        teams[0].name = row[0]
        teams[1].name = row[1]
        if fetch_scores:
            teams[0].score = row[3] + row[5]
            teams[1].score = row[4] + row[6]
            if row[2] > 0:
                teams[0].score += row[2]
            else:
                teams[1].score -= row[2]
        return teams

    def __get_config_teams(self, teams):
        for i in range(0, 2):
            match_teams = []
            if isinstance(self.config['teams'][i], basestring):
                teams[i].name = self.config['teams'][i]
            elif isinstance(self.config['teams'][i], list):
                teams[i].name = '<br />'.join(self.config['teams'][i])
            else:
                if 'winner' in self.config['teams'][i]:
                    match_teams += [
                        MatchInfo.matches[winner_match].winner
                        for winner_match in self.config['teams'][i]['winner']]
                if 'loser' in self.config['teams'][i]:
                    match_teams += [
                        MatchInfo.matches[loser_match].loser
                        for loser_match in self.config['teams'][i]['loser']]
                if 'place' in self.config['teams'][i]:
                    match_teams += [
                        self.teams[place-1][0]
                        for place in self.config['teams'][i]['place']]
            known_teams = [team for team in match_teams if team is not None]
            if len(known_teams) > 0:
                teams[i].name = '<br />'.join([
                    team if team is not None
                    else '??' for team in match_teams])
            else:
                teams[i].name = ''
        return teams

    def __fetch_teams_with_scores(self):
        (scores_fetched, teams_fetched,
         self.info.teams) = self.__get_predefined_scores()
        if scores_fetched:
            self.info.running = -1
        if not teams_fetched:
            try:
                self.info.teams = self.__get_db_teams(self.info.teams, not scores_fetched)
            except (mysql.connector.Error, TypeError, IndexError):
                self.info.teams = self.__get_config_teams(self.info.teams)

    def __get_db_board_count(self):
        towels = self.database.fetch(
            self.config['database'], p_sql.TOWEL_COUNT,
            (self.config['table'], self.config['round']))
        row = [0 if r is None
               else r for r in
               self.database.fetch(
                   self.config['database'], p_sql.BOARD_COUNT,
                   (self.config['table'], self.config['round']))]
        boards_to_play = row[0]
        if row[1] > 0:
            boards_played = int(row[1])
        if boards_to_play > 0:
            boards_played += int(towels[0])
        return boards_played, boards_to_play

    def __fetch_board_count(self):
        boards_played = 0
        boards_to_play = 0
        try:
            boards_played, boards_to_play = self.__get_db_board_count()
        except (mysql.connector.Error, TypeError, KeyError):
            pass
        if boards_played > 0:
            self.info.running = -1 \
                                if boards_played >= boards_to_play \
                                   else boards_played
        else:
            self.info.running = 0


    def __determine_outcome(self):
        if (self.info.running == -1):
            if self.info.teams[0].score > self.info.teams[1].score:
                self.info.winner = self.info.teams[0].name
                self.info.loser = self.info.teams[1].name
            else:
                self.info.loser = self.info.teams[0].name
                self.info.winner = self.info.teams[1].name


    def set_phase_link(self, phase_link):
        if self.info.link is None:
            self.info.link = phase_link
        else:
            if self.info.link != '#':
                self.info.link = urljoin(phase_link, self.info.link)

    def get_info(self):
        self.__fetch_teams_with_scores()
        self.__fetch_board_count()
        self.__determine_outcome()
        return self.info
