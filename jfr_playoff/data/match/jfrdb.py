import re

import jfr_playoff.sql as p_sql
from jfr_playoff.data import TournamentInfo
from jfr_playoff.data.match import MatchInfoClient
from jfr_playoff.logger import PlayoffLogger


class JFRDbMatchInfo(MatchInfoClient):
    @property
    def priority(self):
        return 50

    def is_capable(self):
        return (self.database is not None) and ('database' in self.settings)

    def get_exceptions(self, method):
        return (IOError, TypeError, IndexError, KeyError)

    def get_match_link(self):
        if 'link' in self.settings:
            raise NotImplementedError(
                'link specified in config, skipping lookup')
        if 'round' not in self.settings:
            raise IndexError('round number not specified in match config')
        event_info = TournamentInfo(self.settings, self.database)
        link = event_info.get_results_link(
            'runda%d.html' % (self.settings['round']))
        PlayoffLogger.get('match.jfrdb').info(
            'match #%d link fetched: %s', self.settings['id'], link)
        return link

    def fetch_teams(self, teams):
        row = self.database.fetch(
            self.settings['database'], p_sql.MATCH_RESULTS,
            (self.settings['table'], self.settings['round']))
        for i in range(0, 2):
            teams[i].name = [row[i]]
            teams[i].known_teams = 1
        teams[0].score = row[3] + row[5]
        teams[1].score = row[4] + row[6]
        if row[2] > 0:
            teams[0].score += row[2]
        else:
            teams[1].score -= row[2]
        PlayoffLogger.get('match.jfrdb').info(
            'scores fetched: %s', teams)
        return teams

    def board_count(self):
        towels = self.database.fetch(
            self.settings['database'], p_sql.TOWEL_COUNT,
            (self.settings['table'], self.settings['round']))
        row = [0 if r is None
               else r for r in
               self.database.fetch(
                   self.settings['database'], p_sql.BOARD_COUNT,
                   (self.settings['table'], self.settings['round']))]
        boards_to_play = int(row[0])
        boards_played = max(int(row[1]), 0)
        if boards_to_play > 0:
            boards_played += int(towels[0])
        PlayoffLogger.get('match.jfrdb').info(
            'board count: %d/%d', boards_played, boards_to_play)
        return boards_played, boards_to_play

    def running_link(self):
        match_link = self.settings['link']
        link_match = re.match(r'^(.*)runda(\d+)\.html$', match_link)
        if link_match:
            current_segment = int(
                self.database.fetch(
                    self.settings['database'], p_sql.CURRENT_SEGMENT,
                    (self.settings['round'],))[0])
            PlayoffLogger.get('match.jfrdb').info(
                'fetched running segment: %d', current_segment)
            match_link = '%s%st%d-%d.html' % (
                link_match.group(1), link_match.group(2),
                self.settings['table'], current_segment)
        if match_link != self.settings['link']:
            PlayoffLogger.get('match.jfrdb').info(
                'checking if running link %s is live', match_link)
            from jfr_playoff.data.match.jfrhtml import JFRHtmlMatchInfo
            client = JFRHtmlMatchInfo(self.settings)
            try:
                boards_played, board_count = client.segment_board_count(
                    re.sub('\.htm$', '.html', match_link))
            except Exception as e:
                PlayoffLogger.get('match.jfrdb').info(
                    'unable to determine confirm link: %s(%s)',
                    type(e).__name__, str(e))
                boards_played = 0
            if not boards_played:
                PlayoffLogger.get('match.jfrdb').info(
                    'running link is not live - reverting to match link (%s)',
                    self.settings['link'])
                match_link = self.settings['link']
            elif boards_played == board_count:
                PlayoffLogger.get('match.jfrdb').info(
                    'running link is finished - reverting to match link (%s)',
                    self.settings['link'])
                match_link = self.settings['link']
        return match_link
