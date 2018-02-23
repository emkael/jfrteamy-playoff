from math import ceil
import re

import jfr_playoff.sql as p_sql
from jfr_playoff.remote import RemoteUrl as p_remote

SWISS_TIE_WARNING = 'WARNING: tie detected in swiss %s.' + \
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
            raise ValueError('unable to determine tournament results')
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
        for table in range(1, int(ceil(len(teams)/2.0))+1):
            table_url = self.get_results_link('1t%d-1.html' % (table))
            table_content = p_remote.fetch(table_url)
            for link in table_content.select('a.br'):
                if link['href'] in team_links:
                    for team in teams:
                        if team[0] == team_links[link['href']]:
                            team[1] = link.text.strip(u'\xa0')
                            break
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
        prev_result = None
        for team in swiss_results:
            if prev_result == team[1]:
                print SWISS_TIE_WARNING % (self.settings['database'])
            prev_result = team[1]
        db_teams = [[team[0], team[3], team[4]] for team in swiss_results]
        return db_teams

    def __get_html_finished(self):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('unable to determine tournament status')
        leaderboard = p_remote.fetch(self.settings['link'])
        leaderb_heading = leaderboard.select('td.bdnl12')[0].text
        non_zero_scores = [imps.text for imps in leaderboard.select('td.bdc small') if imps.text != '0-0']
        return (not any(char.isdigit() for char in leaderb_heading)) and (len(non_zero_scores) > 0)

    def __get_db_finished(self):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        finished = self.database.fetch(
            self.settings['database'], p_sql.SWISS_ENDED, {})
        return (len(finished) > 0) and (finished[0] > 0)

    def __get_html_link(self, suffix='leaderb.html'):
        if 'link' not in self.settings:
            raise KeyError('link not configured')
        if not self.settings['link'].endswith('leaderb.html'):
            raise ValueError('unable to determine html link')
        return re.sub(r'leaderb.html$', suffix, self.settings['link'])

    def __get_db_link(self, suffix='leaderb.html'):
        if self.database is None:
            raise KeyError('database not configured')
        if 'database' not in self.settings:
            raise KeyError('database not configured')
        row = self.database.fetch(
            self.settings['database'], p_sql.PREFIX, ())
        if row is not None:
            if len(row) > 0:
                return row[0] + suffix
        raise ValueError('unable to fetch db link')

    def get_tournament_results(self):
        teams = []
        try:
            teams = self.__get_db_results()
        except (IOError, TypeError, IndexError, KeyError):
            try:
                teams = self.__get_html_results()
            except (TypeError, IndexError, KeyError, IOError, ValueError):
                pass
        if self.is_finished() and 'final_positions' in self.settings:
            for position in self.settings['final_positions']:
                if len(teams) >= position:
                    teams[position-1].append(position)
        return teams

    def is_finished(self):
        try:
            return self.__get_db_finished()
        except (IOError, TypeError, IndexError, KeyError):
            try:
                return self.__get_html_finished()
            except (TypeError, IndexError, KeyError, IOError, ValueError):
                pass
        return True

    def get_results_link(self, suffix='leaderb.html'):
        try:
            return self.__get_db_link(suffix)
        except (IOError, TypeError, IndexError, KeyError):
            try:
                return self.__get_html_link(suffix)
            except (KeyError, ValueError):
                pass
        return None
