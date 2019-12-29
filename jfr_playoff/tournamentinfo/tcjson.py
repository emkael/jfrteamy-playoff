import json
import urlparse

from jfr_playoff.remote import RemoteUrl as p_remote
from jfr_playoff.tournamentinfo import TournamentInfoClient

FLAG_CDN_URL = 'https://cdn.tournamentcalculator.com/flags/'


class TCJsonTournamentInfo(TournamentInfoClient):
    def get_results_link(self, suffix):
        return urlparse.urljoin(self.settings['link'], suffix)

    def is_finished(self):
        settings_json = json.loads(
            p_remote.fetch_raw(self.get_results_link('settings.json')))
        return (not settings_json['LiveResults']) \
            and (settings_json['LastPlayedRound'] > 0) \
            and (settings_json['LastPlayedSession'] > 0)

    def get_tournament_results(self):
        results = []
        results_json = json.loads(
            p_remote.fetch_raw(self.get_results_link('results.json')))
        for result in results_json['Results']:
            participant = result['Participant']
            flag_url = None
            flag = participant['_flag']
            if flag is not None:
                flag_url = self.get_results_link(
                    flag['CustomFlagPath']
                    if flag['IsCustom']
                    else '%s/%s.png' % (FLAG_CDN_URL, flag['CountryNameCode']))
            results.append((
                result['ParticipantGroup'], result['Place'],
                participant['_name'], participant['_shortName'],
                flag_url))
        return [list(r[2:]) + [None] for r in sorted(results)]

    def get_exceptions(self, method):
        return (TypeError, IndexError, KeyError, IOError, ValueError)
