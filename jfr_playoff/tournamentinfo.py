from math import ceil
import re

import jfr_playoff.sql as p_sql
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.logger import PlayoffLogger

SWISS_TIE_WARNING = 'tie detected in swiss %s.' + \
                    ' Make sure to resolve the tie by arranging teams' + \
                    ' in configuration file.'


class TournamentInfo:

    def __init__(self, settings, database):
        self.settings = settings
        self.database = database

    def __get_html_results(self):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('invalid link to tournament results')
        PlayoffLogger.get('tournamentinfo').info(
            'fetching tournament results from leaderboard URL: %s', self.settings['link'])
        leaderboard = p_remote.fetch(self.settings['link'])
        result_links = [row.select('a[onmouseover]') for row in leaderboard.find_all('tr') if len(row.select('a[onmouseover]')) > 0]
        results = [None] * (len(result_links) * max([len(links) for links in result_links]))
        for i in range(0, len(result_links)):
            for j in range(0, len(result_links[i])):
                results[len(result_links) * j + i] = result_links[i][j]
        teams = []
        team_links = {}
        for team in results:
            if team is not None:
                team_info = []
                fullname = team.text.strip(u'\xa0')
                team_links[team['href']] = fullname
                team_info.append(fullname)
                team_info.append('')
                team_image = team.find('img')
                if team_image is not None:
                    team_info.append(team_image['src'].replace('images/', ''))
                teams.append(team_info)
        PlayoffLogger.get('tournamentinfo').info(
            'read tournament results from leaderboard: %s', teams)
        for table in range(1, int(ceil(len(teams)/2.0))+1):
            table_url = self.get_results_link('1t%d-1.html' % (table))
            table_content = p_remote.fetch(table_url)
            PlayoffLogger.get('tournamentinfo').info(
                'reading team shortnames from traveller: %s', table_url)
            for link in table_content.select('a.br'):
                if link['href'] in team_links:
                    for team in teams:
                        if team[0] == team_links[link['href']]:
                            team[1] = link.text.strip(u'\xa0')
                            PlayoffLogger.get('tournamentinfo').info(
                                'shortname for %s: %s', team[0], team[1])
                            break
        PlayoffLogger.get('tournamentinfo').info(
            'tournament results from HTML: %s', teams)
        return teams

    def __get_db_results(self):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        if 'ties' not in self.settings:
            self.settings['ties'] = []
        swiss_teams = self.database.fetch_all(
            self.settings['database'], p_sql.SWISS_RESULTS, {})
        swiss_results = sorted(
            swiss_teams,
            key=lambda t: self.settings['ties'].index(t[0]) \
            if t[0] in self.settings['ties'] else -1)
        swiss_results = sorted(
            swiss_results, key=lambda t: t[1], reverse=True)
        swiss_results = sorted(swiss_results, key=lambda team: team[2])
        PlayoffLogger.get('tournamentinfo').info(
            'fetched tournament results from database %s: %s',
            self.settings['database'], swiss_results)
        prev_result = None
        for team in swiss_results:
            if prev_result == team[1]:
                PlayoffLogger.get('tournamentinfo').warning(
                    SWISS_TIE_WARNING, self.settings['database'])
            prev_result = team[1]
        db_teams = [[team[0], team[3], team[4]] for team in swiss_results]
        PlayoffLogger.get('tournamentinfo').info(
            'fetched team list from database %s: %s',
            self.settings['database'], db_teams)
        return db_teams

    def __get_html_finished(self):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('invalid tournament leaderboard link')
        PlayoffLogger.get('tournamentinfo').info(
            'fetching tournament finished status from HTML: %s',
            self.settings['link'])
        leaderboard = p_remote.fetch(self.settings['link'])
        leaderb_heading = leaderboard.select('td.bdnl12')[0].text
        contains_digits = any(char.isdigit() for char in leaderb_heading)
        PlayoffLogger.get('tournamentinfo').info(
            'tournament header from HTML: %s, %s',
            leaderb_heading, 'contains digits' if contains_digits else "doesn't contain digits")
        non_zero_scores = [imps.text for imps in leaderboard.select('td.bdc small') if imps.text != '0-0']
        PlayoffLogger.get('tournamentinfo').info(
            'tournament leaderboard from HTML: has %d non-zero scores',
            len(non_zero_scores))
        finished = (not contains_digits) and (len(non_zero_scores) > 0)
        PlayoffLogger.get('tournamentinfo').info(
            'tournament leaderboard from HTML indicates finished: %s',
            finished)
        return finished

    def __get_db_finished(self):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        finished = self.database.fetch(
            self.settings['database'], p_sql.SWISS_ENDED, {})
        PlayoffLogger.get('tournamentinfo').info(
            'fetching tournament finished status from DB %s: %s',
            self.settings['database'], finished)
        return (len(finished) > 0) and (finished[0] > 0)

    def __get_html_link(self, suffix='leaderb.html'):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('invalid tournament leaderboard link')
        link = re.sub(r'leaderb.html$', suffix, self.settings['link'])
        PlayoffLogger.get('tournamentinfo').info(
            'generating tournament-specific link from leaderboard link %s: %s -> %s',
            self.settings['link'], suffix, link)
        return link

    def __get_db_link(self, suffix='leaderb.html'):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        row = self.database.fetch(
            self.settings['database'], p_sql.PREFIX, ())
        if row is not None:
            if len(row) > 0:
                link = row[0] + suffix
                PlayoffLogger.get('tournamentinfo').info(
                    'generating tournament-specific link from DB %s prefix: %s -> %s',
                    self.settings['database'], suffix, link)
                return link
        raise ValueError('unable to fetch db link')

    def get_tournament_results(self):
        teams = []
        try:
            teams = self.__get_db_results()
        except (IOError, TypeError, IndexError, KeyError) as e:
            PlayoffLogger.get('tournamentinfo').warning(
                'cannot determine tournament results from DB: %s(%s)',
                type(e).__name__, str(e))
            try:
                teams = self.__get_html_results()
            except (TypeError, IndexError, KeyError, IOError, ValueError) as e:
                PlayoffLogger.get('tournamentinfo').warning(
                    'cannot determine tournament results from HTML: %s(%s)',
                    type(e).__name__, str(e))
        if self.is_finished() and 'final_positions' in self.settings:
            PlayoffLogger.get('tournamentinfo').info(
                'setting final positions from tournament results: %s',
                self.settings['final_positions'])
            for position in self.settings['final_positions']:
                if len(teams) >= position:
                    teams[position-1].append(position)
        return teams

    def is_finished(self):
        try:
            return self.__get_db_finished()
        except (IOError, TypeError, IndexError, KeyError) as e:
            PlayoffLogger.get('tournamentinfo').warning(
                'cannot determine tournament finished status from DB: %s(%s)',
                type(e).__name__, str(e))
            try:
                return self.__get_html_finished()
            except (TypeError, IndexError, KeyError, IOError, ValueError) as e:
                PlayoffLogger.get('tournamentinfo').warning(
                    'cannot determine tournament finished status from HTML: %s(%s)',
                    type(e).__name__, str(e))
        PlayoffLogger.get('tournamentinfo').info(
            'assuming tournament is finished')
        return True

    def get_results_link(self, suffix='leaderb.html'):
        try:
            return self.__get_db_link(suffix)
        except (IOError, TypeError, IndexError, KeyError) as e:
            PlayoffLogger.get('tournamentinfo').warning(
                'cannot determine tournament link from DB: %s(%s)',
                type(e).__name__, str(e))
            try:
                return self.__get_html_link(suffix)
            except (KeyError, ValueError):
                PlayoffLogger.get('tournamentinfo').warning(
                    'cannot determine tournament link from HTML: %s(%s)',
                    type(e).__name__, str(e))
        return None
