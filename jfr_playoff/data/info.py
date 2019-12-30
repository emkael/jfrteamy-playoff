from jfr_playoff.logger import PlayoffLogger


class ResultInfo(object):
    def __init__(self, *args):
        self.clients = self.fill_client_list(*args)

    def fill_client_list(self, settings, database):
        return []

    def call_client(self, method, default, *args):
        PlayoffLogger.get('resultinfo').info(
            'calling %s on result info clients', method)
        for client in self.clients:
            try:
                ret = getattr(client, method)(*args)
                PlayoffLogger.get('resultinfo').info(
                    '%s method returned %s', method, ret)
                return ret
            except Exception as e:
                if type(e) in client.get_exceptions(method):
                    PlayoffLogger.get('resultinfo').warning(
                        '%s method raised %s(%s)',
                        method, type(e).__name__, str(e))
                else:
                    raise
        PlayoffLogger.get('resultinfo').info(
            '%s method returning default: %s', method, default)
        return default
