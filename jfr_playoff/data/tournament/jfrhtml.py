from math import ceil
import re

from jfr_playoff.logger import PlayoffLogger
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.data.tournament import TournamentInfoClient


class JFRHtmlTournamentInfo(TournamentInfoClient):
    @property
    def priority(self):
        return 30

    def is_capable(self):
        return ('link' in self.settings) \
            and (self.settings['link'].endswith('leaderb.html'))

    def get_exceptions(self, method):
        if method == 'get_results_link':
            return (KeyError, ValueError)
        return (TypeError, IndexError, KeyError, IOError, ValueError)

    def get_results_link(self, suffix='leaderb.html'):
        link = re.sub(r'leaderb.html$', suffix, self.settings['link'])
        PlayoffLogger.get('tournament.jfrhtml').info(
            'generating tournament-specific link from leaderboard link %s: %s -> %s',
            self.settings['link'], suffix, link)
        return link

    def is_finished(self):
        PlayoffLogger.get('tournament.jfrhtml').info(
            'fetching tournament finished status from HTML: %s',
            self.settings['link'])
        leaderboard = p_remote.fetch(self.settings['link'])
        leaderb_heading = leaderboard.select('td.bdnl12')[0].text
        contains_digits = any(char.isdigit() for char in leaderb_heading)
        PlayoffLogger.get('tournament.jfrhtml').info(
            'tournament header from HTML: %s, %s',
            leaderb_heading,
            'contains digits' if contains_digits else "doesn't contain digits")
        non_zero_scores = [
            imps.text
            for imps
            in leaderboard.select('td.bdc small')
            if imps.text != '0-0']
        PlayoffLogger.get('tournament.jfrhtml').info(
            'tournament leaderboard from HTML: has %d non-zero scores',
            len(non_zero_scores))
        finished = (not contains_digits) and (len(non_zero_scores) > 0)
        PlayoffLogger.get('tournament.jfrhtml').info(
            'tournament leaderboard from HTML indicates finished: %s',
            finished)
        return finished

    def get_tournament_results(self):
        PlayoffLogger.get('tournament.jfrhtml').info(
            'fetching tournament results from leaderboard URL: %s',
            self.settings['link'])
        leaderboard = p_remote.fetch(self.settings['link'])
        result_links = [
            row.select('a[onmouseover]')
            for row
            in leaderboard.find_all('tr')
            if len(row.select('a[onmouseover]')) > 0]
        results = [None] * (len(result_links) * max([
            len(links) for links in result_links]))
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
        PlayoffLogger.get('tournament.jfrhtml').info(
            'read tournament results from leaderboard: %s', teams)
        for table in range(1, int(ceil(len(teams)/2.0))+1):
            table_url = self.get_results_link('1t%d-1.html' % (table))
            table_content = p_remote.fetch(table_url)
            PlayoffLogger.get('tournament.jfrhtml').info(
                'reading team shortnames from traveller: %s', table_url)
            for link in table_content.select('a.br'):
                if link['href'] in team_links:
                    for team in teams:
                        if team[0] == team_links[link['href']]:
                            team[1] = link.text.strip(u'\xa0')
                            PlayoffLogger.get('tournament.jfrhtml').info(
                                'shortname for %s: %s', team[0], team[1])
                            break
        PlayoffLogger.get('tournament.jfrhtml').info(
            'tournament results from HTML: %s', teams)
        return teams
