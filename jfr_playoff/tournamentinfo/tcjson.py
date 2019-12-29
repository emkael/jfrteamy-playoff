import json
import urlparse

from jfr_playoff.logger import PlayoffLogger
from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.tournamentinfo import TournamentInfoClient

FLAG_CDN_URL = 'https://cdn.tournamentcalculator.com/flags/'


class TCJsonTournamentInfo(TournamentInfoClient):
    def get_exceptions(self, method):
        return (TypeError, IndexError, KeyError, IOError, ValueError)

    def get_results_link(self, suffix):
        link = urlparse.urljoin(self.settings['link'], suffix)
        PlayoffLogger.get('tcjson').info(
            'generating tournament-specific link from leaderboard link %s: %s -> %s',
            self.settings['link'], suffix, link)
        return link

    def is_finished(self):
        settings_json = json.loads(
            p_remote.fetch_raw(self.get_results_link('settings.json')))
        live_results = settings_json['LiveResults']
        last_round = settings_json['LastPlayedRound']
        last_session = settings_json['LastPlayedSession']
        finished = (not live_results) \
            and (last_round > 0) and (last_session > 0)
        PlayoffLogger.get('jfrhtml').info(
            'tournament settings (live = %s, last_round = %d, last_session = %d) indicate finished: %s',
            live_results, last_round, last_session, finished)
        return finished

    def get_tournament_results(self):
        results = []
        results_json = json.loads(
            p_remote.fetch_raw(self.get_results_link('results.json')))
        participant_groups = []
        for result in results_json['Results']:
            group = result['ParticipantGroup']
            if group is not None:
                if group not in participant_groups:
                    participant_groups.append(group)
                group_id = participant_groups.index(group) + 1
            else:
                group_id = 999999
            participant = result['Participant']
            flag_url = None
            flag = participant['_flag']
            if flag is not None:
                flag_url = self.get_results_link(
                    flag['CustomFlagPath']
                    if flag['IsCustom']
                    else '%s/%s.png' % (FLAG_CDN_URL, flag['CountryNameCode']))
            results.append((
                group_id, result['Place'],
                participant['_name'], participant['_shortName'],
                flag_url))
        PlayoffLogger.get('tcjson').info(
            'tournament results fetched: %s' % results)
        return [list(r[2:]) + [None] for r in sorted(results)]
