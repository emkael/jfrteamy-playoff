import json
import urlparse

from jfr_playoff.data.match import MatchInfoClient
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.logger import PlayoffLogger


class TCJsonMatchInfo(MatchInfoClient):
    @property
    def priority(self):
        return 20

    def is_capable(self):
        return ('link' in self.settings) and ('#' in self.settings['link'])

    def get_exceptions(self, method):
        return (TypeError, IndexError, KeyError, IOError, ValueError)

    def _get_results_link(self, suffix):
        return urlparse.urljoin(self.settings['link'], suffix)

    def _get_round_from_link(self, link):
        fragment = urlparse.urlparse(link).fragment
        return max(1, int(fragment[11:14])), max(1, int(fragment[14:17]))

    def get_match_link(self):
        PlayoffLogger.get('match.tcjson').info(
            'match #%d link pre-defined: %s',
            self.settings['id'], self.settings['link'])
        return self.settings['link']

    def _get_results(self, link, table_no):
        session_no, round_no = self._get_round_from_link(link)
        PlayoffLogger.get('match.tcjson').info(
            'link %s -> session %d, round %d', link, session_no, round_no)
        round_results = json.loads(
            p_remote.fetch_raw(
                self._get_results_link(
                    'o%d-%d.json' % (session_no, round_no))))
        table_id = str(table_no)
        for result in round_results['Results']:
            if result['Table'] == table_id:
                return result
        PlayoffLogger.get('match.tcjson').info(
            'results for table %d not found in %s', table_no, link)
        raise ValueError('results not found')

    def fetch_teams(self, teams):
        results = self._get_results(
            self.settings['link'], self.settings['table'])
        sides = [side for side in ['Ns', 'Sn', 'We', 'Ew'] if side in results]
        for idx, side in enumerate(sides):
            teams[idx].name = [results[side]['_name']]
            teams[idx].known_teams = 1
            teams[idx].score = results['Sum1'+side]
        PlayoffLogger.get('match.tcjson').info(
            'scores fetched: %s', teams)
        return teams

    def board_count(self):
        results = self._get_results(
            self.settings['link'], self.settings['table'])
        played = 0
        finished = True
        for segment in results['Segments']:
            PlayoffLogger.get('match.tcjson').info(
                'segment %d: played boards=%d, live=%s, towel=%s',
                segment['Segment']+1, segment['BoardsCounted'],
                segment['Live'], segment['Towel'])
            played += segment['BoardsCounted']
            if segment['Live'] or not (
                    (segment['BoardsCounted'] or segment['Towel'])):
                PlayoffLogger.get('match.tcjson').info(
                    'segment %d not finished', segment['Segment']+1)
                finished = False
        PlayoffLogger.get('match.tcjson').info(
            'board count: %d, finished: %s', played, finished)
        if finished and not played:
            # toweled match
            played = 1
        return played, played if finished else played+1

    def _get_segment_link(self, base_link, segment_id, table_id):
        table_id = '{t:{pad}>6}'.format(t=table_id, pad='0')
        session_id, round_id = self._get_round_from_link(base_link)
        fragment = '#000SS000000%03d%03d%03d%s' % (
            session_id, round_id, segment_id, table_id)
        return urlparse.urljoin(base_link, fragment)

    def running_link(self):
        settings = json.loads(p_remote.fetch_raw(
            self._get_results_link('settings.json')))
        if settings['ShowOnlyResults']:
            PlayoffLogger.get('match.tcjson').info(
                'ShowOnlyResults active, no running segment link available')
            return self.settings['link']
        results = self._get_results(
            self.settings['link'], self.settings['table'])
        for segment in results['Segments']:
            if segment['Live']:
                link = self._get_segment_link(
                    self.settings['link'],
                    segment['Segment'], results['TableFull'])
                PlayoffLogger.get('match.tcjson').info(
                    'running segment link for segment %d, table %s: %s',
                    segment['Segment']+1, results['TableFull'], link)
                return link
        PlayoffLogger.get('match.tcjson').info(
            'no running segment link available')
        return self.settings['link']
