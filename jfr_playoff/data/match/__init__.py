import re
from urlparse import urljoin

import jfr_playoff.sql as p_sql
from jfr_playoff.dto import Match, Team
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.data.info import ResultInfo, TournamentInfo
from jfr_playoff.logger import PlayoffLogger


class MatchInfo(ResultInfo):

    matches = {}

    def __init__(self, match_config, teams, database, aliases=None):
        self.config = match_config
        self.teams = teams
        self.database = database
        self.aliases = {}
        if aliases:
            for team, team_aliases in aliases.iteritems():
                for alias in team_aliases:
                    self.aliases[alias] = team
        ResultInfo.__init__(self, match_config, database)
        self.info = Match()
        self.__init_info()
        self.__fetch_match_link()

    def fill_client_list(self, settings, database):
        return []

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
        self.info.winner_place = self.config.get('winner', [])
        self.info.loser_place = self.config.get('loser', [])
        self.info.teams = []

    def __fetch_match_link(self):
        if 'link' in self.config:
            self.info.link = self.config['link']
            PlayoffLogger.get('matchinfo').info(
                'match #%d link pre-defined: %s', self.info.id, self.info.link)
        elif ('round' in self.config) and ('database' in self.config):
            event_info = TournamentInfo(self.config, self.database)
            self.info.link = event_info.get_results_link(
                'runda%d.html' % (self.config['round']))
            PlayoffLogger.get('matchinfo').info(
                'match #%d link fetched: %s', self.info.id, self.info.link)
        else:
            PlayoffLogger.get('matchinfo').info('match #%d link empty', self.info.id)

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

    def __get_db_teams(self, teams, fetch_scores):
        row = self.database.fetch(
            self.config['database'], p_sql.MATCH_RESULTS,
            (self.config['table'], self.config['round']))
        for i in range(0, 2):
            teams[i].name = [row[i]]
            teams[i].known_teams = 1
        if fetch_scores:
            teams[0].score = row[3] + row[5]
            teams[1].score = row[4] + row[6]
            if row[2] > 0:
                teams[0].score += row[2]
            else:
                teams[1].score -= row[2]
        PlayoffLogger.get('matchinfo').info(
            'db scores for match #%d: %s', self.info.id, teams)
        return teams

    def __find_table_row(self, url):
        html_content = p_remote.fetch(url)
        for row in html_content.select('tr tr'):
            for cell in row.select('td.t1'):
                if cell.text.strip() == str(self.config['table']):
                    PlayoffLogger.get('matchinfo.html').debug(
                        'HTML row for table %d found: %s',
                        self.config['table'], row)
                    return row
        PlayoffLogger.get('matchinfo.html').debug(
            'HTML row for table %d not found',
            self.config['table'])
        return None

    def __get_html_teams(self, teams, fetch_score):
        if self.info.link is None:
            raise ValueError('link not set')
        row = self.__find_table_row(self.info.link)
        if row is None:
            raise ValueError('table row not found')
        try:
            scores = [
                float(text) for text
                in row.select('td.bdc')[-1].contents
                if isinstance(text, unicode)]
        except ValueError:
            # single-segment match
            try:
                # running single-segment
                scores = [
                    float(text.strip()) for text
                    in row.select('td.bdcg a')[-1].contents
                    if isinstance(text, unicode)]
            except IndexError:
                try:
                    # static single-segment
                    scores = [
                        float(text.strip()) for text
                        in row.select('td.bdc a')[-1].contents
                        if isinstance(text, unicode)]
                except IndexError:
                    # toweled single-segment
                    scores = [0.0, 0.0]
            # carry-over
            carry_over = [
                float(text.strip()) if len(text.strip()) > 0 else 0.0 for text
                in row.select('td.bdc')[0].contents
                if isinstance(text, unicode)]
            if len(carry_over) < 2:
                # no carry-over, possibly no carry-over cells or empty
                carry_over = [0.0, 0.0]
            for i in range(0, 2):
                scores[i] += carry_over[i]
        team_names = [[text for text in link.contents
                       if isinstance(text, unicode)][0].strip(u'\xa0')
                      for link in row.select('a[onmouseover]')]
        for i in range(0, 2):
            teams[i].name = [team_names[i]]
            teams[i].known_teams = 1
            teams[i].score = scores[i]
        PlayoffLogger.get('matchinfo').info(
            'HTML scores for match #%d: %s',
            self.info.id, teams)
        return teams

    def __get_config_teams(self, teams):
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
                    match_teams += [
                        self.teams[place-1][0]
                        for place in self.config['teams'][i]['place']]
            teams[i].name = match_teams
            teams[i].possible_name = possible_teams
            teams[i].known_teams = len([team for team in match_teams if team is not None])
            teams[i].selected_team = self.config['selected_teams'][i] if 'selected_teams' in self.config else -1
        PlayoffLogger.get('matchinfo').info(
            'config scores for match #%d: %s',
            self.info.id, teams)
        return teams

    def __resolve_team_aliases(self, teams):
        return [self.aliases[team] if team in self.aliases else team for team in teams]

    def __fetch_teams_with_scores(self):
        (scores_fetched, teams_fetched, self.info.teams) = self.__get_predefined_scores()
        if scores_fetched:
            PlayoffLogger.get('matchinfo').info(
                'pre-defined scores for match #%d fetched', self.info.id)
            self.info.running = int(self.config.get('running', -1))
        if not teams_fetched:
            try:
                try:
                    if self.database is None:
                        raise KeyError('database not configured')
                    if 'database' not in self.config:
                        raise KeyError('database not configured')
                    self.info.teams = self.__get_db_teams(
                        self.info.teams, not scores_fetched)
                except (IOError, TypeError, IndexError, KeyError) as e:
                    PlayoffLogger.get('matchinfo').warning(
                        'fetching DB scores for match #%d failed: %s(%s)',
                        self.info.id, type(e).__name__, str(e))
                    self.info.teams = self.__get_html_teams(
                        self.info.teams, not scores_fetched)
            except (TypeError, IndexError, KeyError, IOError, ValueError) as e:
                PlayoffLogger.get('matchinfo').warning(
                    'fetching HTML scores for match #%d failed: %s(%s)',
                    self.info.id, type(e).__name__, str(e))
                self.info.teams = self.__get_config_teams(self.info.teams)
        for team in range(0, len(self.info.teams)):
            if isinstance(self.config['teams'][team], dict):
                self.info.teams[team].place = self.config['teams'][team].get(
                    'place', self.info.teams[team].place)
            self.info.teams[team].name = self.__resolve_team_aliases(self.info.teams[team].name)
            PlayoffLogger.get('matchinfo').info('team list after resolving aliases: %s', self.info.teams[team].name)
            self.info.teams[team].possible_name = self.__resolve_team_aliases(self.info.teams[team].possible_name)
            PlayoffLogger.get('matchinfo').info('predicted team list after resolving aliases: %s', self.info.teams[team].possible_name)


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
        PlayoffLogger.get('matchinfo').info(
            'DB board count for match #%d: %d/%d',
            self.info.id, boards_played, boards_to_play)
        return boards_played, boards_to_play

    def __has_segment_link(self, cell):
        links = [link for link in cell.select('a[href]')
                 if re.match(r'^.*\d+t\d+-\d+\.htm$', link['href'])]
        return len(links) > 0

    def __has_towel_image(self, cell):
        return len(cell.select('img[alt="towel"]')) > 0

    def __get_html_running_boards(self, cell):
        return int(cell.contents[-1].strip())

    def __get_html_segment_board_count(self, segment_url):
        segment_content = p_remote.fetch(segment_url)
        board_rows = [row for row in segment_content.find_all('tr') if len(row.select('td.bdcc a.zb')) > 0]
        board_count = len(board_rows)
        played_boards = len([
            row for row in board_rows if len(
                ''.join([cell.text.strip() for cell in row.select('td.bdc')])) > 0])
        return played_boards, board_count

    def __get_finished_info(self, cell):
        segment_link = cell.select('a[href]')
        if len(segment_link) > 0:
            segment_url = re.sub(
                r'\.htm$', '.html',
                urljoin(self.info.link, segment_link[0]['href']))
            try:
                played_boards, board_count = self.__get_html_segment_board_count(segment_url)
                PlayoffLogger.get('matchinfo').info(
                    'HTML played boards count for segment: %d/%d',
                    played_boards, board_count)
                return board_count, played_boards >= board_count
            except IOError as e:
                PlayoffLogger.get('matchinfo').info(
                    'cannot fetch HTML played boards count for segment: %s(%s)',
                    self.info.id, type(e).__name__, str(e))
                return 0, False
        return 0, False

    def __get_html_board_count(self):
        if self.info.link is None:
            raise ValueError('link not set')
        row = self.__find_table_row(self.info.link)
        if row is None:
            raise ValueError('table row not found')
        for selector in ['td.bdc', 'td.bdcg']:
            cells = row.select(selector)
            segments = [cell for cell in cells if self.__has_segment_link(cell)]
            towels = [cell for cell in cells if self.__has_towel_image(cell)]
            if len(segments) == 0:
                # in single-segment match, there are no td.bdc cells with segment links
                # but maybe it's a multi-segment match with towels
                if len(towels) > 0:
                    PlayoffLogger.get('matchinfo').info(
                        'HTML board count for match #%d: all towels', self.info.id)
                    return 1, 1 # entire match is toweled, so mark as finished
            else:
                # not a single-segment match, no need to look for td.bdcg cells
                break
        if len(segments) == 0:
            raise ValueError('segments not found')
        running_segments = row.select('td.bdca')
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
        if 'bdcg' in segments[0]['class']:
            # only a single-segment match will yield td.bdcg cells with segment scores
            total_boards = boards_in_segment
        else:
            PlayoffLogger.get('matchinfo').info(
                'HTML board count for match #%d, found: %d finished segments, %d towels, %d boards per segment and %d boards in running segment',
                self.info.id, len(finished_segments), len(towels), boards_in_segment, running_boards)
            total_boards = (len(segments) + len(towels) + len(running_segments)) * boards_in_segment
        played_boards = (len(towels) + len(finished_segments)) * boards_in_segment + running_boards
        PlayoffLogger.get('matchinfo').info(
            'HTML board count for match #%d: %d/%d',
            self.info.id, played_boards, total_boards)
        return played_boards, total_boards

    def __fetch_board_count(self):
        boards_played = 0
        boards_to_play = 0
        try:
            if self.database is None:
                raise KeyError('database not configured')
            boards_played, boards_to_play = self.__get_db_board_count()
        except (IOError, TypeError, IndexError, KeyError) as e:
            PlayoffLogger.get('matchinfo').warning(
                'fetching board count from DB for match #%d failed: %s(%s)',
                self.info.id, type(e).__name__, str(e))
            try:
                boards_played, boards_to_play = self.__get_html_board_count()
            except (TypeError, IndexError, KeyError, IOError, ValueError) as e:
                PlayoffLogger.get('matchinfo').warning(
                    'fetching board count from HTML for match #%d failed: %s(%s)',
                    self.info.id, type(e).__name__, str(e))
                pass
        if boards_played > 0:
            self.info.running = -1 \
                if boards_played >= boards_to_play \
                   else boards_played

    def __determine_outcome(self):
        if (self.info.teams[0].known_teams == 1) \
           and (self.info.teams[1].known_teams == 1):
            if self.info.running == -1:
                if self.info.teams[0].score > self.info.teams[1].score:
                    self.info.winner = self.info.teams[0].name[0]
                    self.info.loser = self.info.teams[1].name[0]
                else:
                    self.info.loser = self.info.teams[0].name[0]
                    self.info.winner = self.info.teams[1].name[0]
            elif self.info.running > 0:
                if self.info.teams[0].score > self.info.teams[1].score:
                    self.info.possible_winner = self.info.teams[0].name[0]
                    self.info.possible_loser = self.info.teams[1].name[0]
                elif self.info.teams[0].score < self.info.teams[1].score:
                    self.info.possible_loser = self.info.teams[0].name[0]
                    self.info.possible_winner = self.info.teams[1].name[0]

    def __get_db_running_link(self, prefix, round_no):
        current_segment = int(
            self.database.fetch(
                self.config['database'], p_sql.CURRENT_SEGMENT, ())[0])
        PlayoffLogger.get('matchinfo').info(
            'fetched running segment from DB for match #%d: %d',
            self.info.id, current_segment)
        return '%s%st%d-%d.html' % (
            prefix, round_no, self.config['table'], current_segment)

    def __get_html_running_link(self):
        if self.info.link is None:
            raise ValueError('link not set')
        row = self.__find_table_row(self.info.link)
        running_link = row.select('td.bdcg a[href]')
        if len(running_link) == 0:
            raise ValueError('running link not found')
        PlayoffLogger.get('matchinfo').info(
            'fetched running link from HTML for match #%d: %s',
            self.info.id, running_link)
        return urljoin(self.info.link, running_link[0]['href'])

    def __determine_running_link(self):
        if self.info.link is None:
            return
        match_link = self.info.link
        link_match = re.match(r'^(.*)runda(\d+)\.html$', self.info.link)
        if link_match:
            try:
                if self.database is None:
                    raise KeyError('database not configured')
                self.info.link = self.__get_db_running_link(
                    link_match.group(1), link_match.group(2))
            except (IOError, TypeError, IndexError, KeyError) as e:
                PlayoffLogger.get('matchinfo').warning(
                    'cannot determine running link from DB for match #%d: %s(%s)',
                    self.info.id, type(e).__name__, str(e))
                try:
                    self.info.link = self.__get_html_running_link()
                except (TypeError, IndexError, KeyError, IOError, ValueError) as e:
                    PlayoffLogger.get('matchinfo').warning(
                        'cannot determine running link from HTML for match #%d: %s(%s)',
                        self.info.id, type(e).__name__, str(e))
            if self.info.link != match_link:
                # we've detected a running segment link
                # we should check if the segment's uploaded live
                try:
                    boards_played, board_count = self.__get_html_segment_board_count(re.sub('\.htm$', '.html', self.info.link))
                except IOError as e:
                    PlayoffLogger.get('matchinfo').warning(
                        'cannot determine running link (%s) board count for match #%d: %s(%s)',
                        self.info.link, self.info.id, type(e).__name__, str(e))
                    boards_played = 0
                if not boards_played:
                    PlayoffLogger.get('matchinfo').warning(
                        'running link (%s) for match #%d is not live, reverting to match link (%s)',
                        self.info.link, self.info.id, match_link)
                    self.info.link = match_link

    def set_phase_link(self, phase_link):
        if self.info.link is None:
            self.info.link = phase_link
        else:
            if self.info.link != '#':
                self.info.link = urljoin(phase_link, self.info.link)
        PlayoffLogger.get('matchinfo').info(
            'applying phase link %s to match #%d: %s',
            phase_link, self.info.id, self.info.link)

    def get_info(self):
        self.__fetch_teams_with_scores()
        self.__fetch_board_count()
        self.__determine_outcome()
        if self.info.running > 0:
            self.__determine_running_link()
        return self.info
