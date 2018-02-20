import re
from urlparse import urljoin

import mysql

import jfr_playoff.sql as p_sql
from jfr_playoff.dto import Match, Team
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.tournamentinfo import TournamentInfo

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

    def __fetch_match_link(self):
        if 'link' in self.config:
            self.info.link = self.config['link']
        elif ('round' in self.config) and ('database' in self.config):
            event_info = TournamentInfo(self.config, self.database)
            self.info.link = event_info.get_results_link(
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

    def __find_table_row(self, url):
        html_content = p_remote.fetch(url)
        for row in html_content.select('tr tr'):
            for cell in row.select('td.t1'):
                if cell.text.strip() == str(self.config['table']):
                    return row
        return None

    def __get_html_teams(self, teams, fetch_score):
        row = self.__find_table_row(self.info.link)
        if row is None:
            raise ValueError('table row not found')
        score_cell = row.select('td.bdc')[-1]
        scores = [
            float(text) for text
            in score_cell.contents
            if isinstance(text, unicode)]
        team_names = [[text for text in link.contents
                       if isinstance(text, unicode)][0].strip(u'\xa0')
                      for link in row.select('a[onmouseover]')]
        for i in range(0, 2):
            teams[i].name = team_names[i]
            teams[i].score = scores[i]
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
        (scores_fetched, teams_fetched, self.info.teams) = self.__get_predefined_scores()
        if scores_fetched:
            if 'running' in self.config:
                self.info.running = int(self.config['running'])
            else:
                self.info.running = -1
        if not teams_fetched:
            try:
                try:
                    if self.database is None:
                        raise KeyError('database not configured')
                    if 'database' not in self.config:
                        raise KeyError('database not configured')
                    self.info.teams = self.__get_db_teams(
                        self.info.teams, not scores_fetched)
                except (mysql.connector.Error, TypeError, IndexError, KeyError):
                    self.info.teams = self.__get_html_teams(
                        self.info.teams, not scores_fetched)
            except (TypeError, IndexError, KeyError, IOError, ValueError):
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
        boards_to_play = int(row[0])
        boards_played = max(int(row[1]), 0)
        if boards_to_play > 0:
            boards_played += int(towels[0])
        return boards_played, boards_to_play

    def __has_segment_link(self, cell):
        links = [link for link in cell.select('a[href]')
                 if re.match(r'^.*\d+t\d+-\d+\.htm$', link['href'])]
        return len(links) > 0

    def __has_towel_image(self, cell):
        return len(cell.select('img[alt="towel"]')) > 0

    def __has_running_board_count(self, cell):
        return len(cell.select('img[alt="running..."]')) > 0

    def __get_html_running_boards(self, cell):
        return int(cell.contents[-1].strip())

    def __get_finished_info(self, cell):
        segment_link = cell.select('a[href]')
        if len(segment_link) > 0:
            segment_url = re.sub(
                r'\.htm$', '.html',
                urljoin(self.info.link, segment_link[0]['href']))
            try:
                segment_content = p_remote.fetch(segment_url)
                board_rows = [row for row in segment_content.find_all('tr') if len(row.select('a.zb')) > 0]
                board_count = len(board_rows)
                played_boards = len([
                    row for row in board_rows if len(
                        ''.join([cell.text.strip() for cell in row.select('td.bdn') + row.select('td.bde')])) > 0])
                return board_count, played_boards >= board_count
            except IOError:
                return 0, False
        return 0, False

    def __get_html_board_count(self):
        row = self.__find_table_row(self.info.link)
        if row is None:
            raise ValueError('table row not found')
        cells = row.select('td.bdc')
        segments = [cell for cell in cells if self.__has_segment_link(cell)]
        towels = [cell for cell in cells if self.__has_towel_image(cell)]
        if len(segments) == 0:
            if len(towels) > 0:
                return 1, 1 # entire match is toweled, so mark as finished
            else:
                raise ValueError('segments not found')
        running_segments = [cell for cell in row.select('td.bdca') if self.__has_running_board_count(cell)]
        running_boards = sum([self.__get_html_running_boards(segment) for segment in running_segments])
        finished_segments = []
        boards_in_segment = None
        for segment in segments:
            if segment not in running_segments:
                boards, is_finished = self.__get_finished_info(segment)
                if is_finished:
                    finished_segments.append(segment)
                if boards_in_segment is None and boards > 0:
                    boards_in_segment = boards
        total_boards = (len(segments) + len(towels) + len(running_segments)) * boards_in_segment
        played_boards = (len(towels) + len(finished_segments)) * boards_in_segment + running_boards
        return played_boards, total_boards

    def __fetch_board_count(self):
        boards_played = 0
        boards_to_play = 0
        try:
            if self.database is None:
                raise KeyError('database not configured')
            boards_played, boards_to_play = self.__get_db_board_count()
        except (mysql.connector.Error, TypeError, IndexError, KeyError):
            try:
                boards_played, boards_to_play = self.__get_html_board_count()
            except (TypeError, IndexError, KeyError, IOError, ValueError):
                pass
        if boards_played > 0:
            self.info.running = -1 \
                                if boards_played >= boards_to_play \
                                   else boards_played

    def __determine_outcome(self):
        if (self.info.running == -1):
            if self.info.teams[0].score > self.info.teams[1].score:
                self.info.winner = self.info.teams[0].name
                self.info.loser = self.info.teams[1].name
            else:
                self.info.loser = self.info.teams[0].name
                self.info.winner = self.info.teams[1].name

    def __get_db_running_link(self, prefix, round_no):
        current_segment = int(
            self.database.fetch(
                self.config['database'], p_sql.CURRENT_SEGMENT, ())[0])
        return '%s%st%d-%d.html' % (
            prefix, round_no, self.config['table'], current_segment)

    def __get_html_running_link(self):
        row = self.__find_table_row(self.info.link)
        running_link = row.select('td.bdcg a[href]')
        if len(running_link) == 0:
            raise ValueError('running link not found')
        return urljoin(self.info.link, running_link[0]['href'])

    def __determine_running_link(self):
        link_match = re.match(r'^(.*)runda(\d+)\.html$', self.info.link)
        if link_match:
            try:
                if self.database is None:
                    raise KeyError('database not configured')
                self.info.link = self.__get_db_running_link(
                    link_match.group(1), link_match.group(2))
            except (mysql.connector.Error, TypeError, IndexError, KeyError):
                try:
                    self.info.link = self.__get_html_running_link()
                except (TypeError, IndexError, KeyError, IOError, ValueError):
                    pass

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
        if self.info.running > 0:
            self.__determine_running_link()
        return self.info
