import copy
import re
from urlparse import urljoin

from jfr_playoff.data.match import MatchInfoClient
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.logger import PlayoffLogger


class JFRHtmlMatchInfo(MatchInfoClient):
    @property
    def priority(self):
        return 30

    def is_capable(self):
        return ('link' in self.settings) and ('#' not in self.settings['link'])

    def get_exceptions(self, method):
        return (TypeError, IndexError, KeyError, IOError, ValueError)

    def get_match_link(self):
        PlayoffLogger.get('match.jfrhtml').info(
            'match #%d link pre-defined: %s',
            self.settings['id'], self.settings['link'])
        return self.settings['link']

    def _find_table_row(self, url):
        html_content = p_remote.fetch(url)
        for row in html_content.select('tr tr'):
            for cell in row.select('td.t1'):
                if cell.text.strip() == str(self.settings['table']):
                    PlayoffLogger.get('match.jfrhtml').debug(
                        'HTML row for table %d found: %s',
                        self.settings['table'], row)
                    return row
        PlayoffLogger.get('match.jfrhtml').debug(
            'HTML row for table %d not found',
            self.settings['table'])
        return None

    def fetch_teams(self, teams):
        if self.settings['link'] is None:
            raise ValueError('link not set')
        row = self._find_table_row(self.settings['link'])
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
        PlayoffLogger.get('match.jfrhtml').info(
            'scores fetched: %s', teams)
        return teams


    def _has_segment_link(self, cell):
        links = [link for link in cell.select('a[href]')
                 if re.match(r'^.*\d+t\d+-\d+\.htm$', link['href'])]
        return len(links) > 0

    def _has_towel_image(self, cell):
        return len(cell.select('img[alt="towel"]')) > 0

    def _get_html_running_boards(self, cell):
        return int(cell.contents[-1].strip())

    def segment_board_count(self, segment_url):
        segment_content = p_remote.fetch(segment_url)
        board_rows = [
            row for row
            in segment_content.find_all('tr')
            if len(row.select('td.bdcc a.zb')) > 0]
        board_count = len(board_rows)
        played_boards = len([
            row for row
            in board_rows
            if len(''.join([
                    cell.text.strip()
                    for cell in row.select('td.bdc')])) > 0])
        return played_boards, board_count

    def _get_finished_info(self, cell):
        segment_link = cell.select('a[href]')
        if len(segment_link) > 0:
            segment_url = re.sub(
                r'\.htm$', '.html',
                urljoin(self.settings['link'], segment_link[0]['href']))
            try:
                played_boards, board_count = \
                    self.segment_board_count(segment_url)
                PlayoffLogger.get('match.jfrhtml').info(
                    'HTML played boards count for segment: %d/%d',
                    played_boards, board_count)
                return board_count, played_boards >= board_count
            except IOError as e:
                PlayoffLogger.get('match.jfrhtml').info(
                    'cannot fetch played boards count for segment: %s(%s)',
                    type(e).__name__, str(e))
                return 0, False
        return 0, False

    def board_count(self):
        row = self._find_table_row(self.settings['link'])
        if row is None:
            raise ValueError('table row not found')
        for selector in ['td.bdc', 'td.bdcg']:
            cells = row.select(selector)
            segments = [cell for cell in cells if self._has_segment_link(cell)]
            towels = [cell for cell in cells if self._has_towel_image(cell)]
            if len(segments) == 0:
                # in single-segment match,
                # there are no td.bdc cells with segment links,
                # but maybe it's a multi-segment match with towels
                if len(towels) > 0:
                    PlayoffLogger.get('match.jfrhtml').info(
                        'board count: all towels')
                    return 1, 1 # entire match is toweled, so mark as finished
            else:
                # not a single-segment match
                # no need to look for td.bdcg cells
                break
        if len(segments) == 0:
            raise ValueError('segments not found')
        running_segments = row.select('td.bdca')
        running_boards = sum([
            self._get_html_running_boards(segment)
            for segment
            in running_segments])
        finished_segments = []
        boards_in_segment = None
        for segment in segments:
            if segment not in running_segments:
                boards, is_finished = self._get_finished_info(segment)
                if is_finished:
                    finished_segments.append(segment)
                if boards_in_segment is None and boards > 0:
                    boards_in_segment = boards
        if 'bdcg' in segments[0]['class']:
            # only a single-segment match will yield
            # td.bdcg cells with segment scores
            total_boards = boards_in_segment
        else:
            PlayoffLogger.get('match.jfrhtml').info(
                'board count, found: %d finished segments, %d towels, ' \
                + '%d boards per segment and %d boards in running segment',
                len(finished_segments), len(towels),
                boards_in_segment, running_boards)
            total_boards = (
                len(segments) + len(towels) + len(running_segments)) \
                * boards_in_segment
        played_boards = (len(towels) + len(finished_segments)) \
            * boards_in_segment \
            + running_boards
        PlayoffLogger.get('match.jfrhtml').info(
            'board count: %d/%d', played_boards, total_boards)
        return played_boards, total_boards

    def running_link(self):
        row = self._find_table_row(self.settings['link'])
        running_link = row.select('td.bdcg a[href]')
        if len(running_link) == 0:
            raise ValueError('running link not found')
        PlayoffLogger.get('match.jfrhtml').info(
            'fetched running link from HTML: %s', running_link)
        match_link = urljoin(self.settings['link'], running_link[0]['href'])
        try:
            boards_played, board_count = self.segment_board_count(
                re.sub('\.htm$', '.html', match_link))
        except Exception as e:
            boards_played = 0
        if not boards_played:
            PlayoffLogger.get('match.jfrhtml').info(
                'running link is not live - reverting to match link (%s)',
                self.settings['link'])
            match_link = self.settings['link']
        return match_link
