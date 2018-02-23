import requests

from bs4 import BeautifulSoup as bs
from jfr_playoff.logger import PlayoffLogger

class RemoteUrl:

    url_cache = {}

    @classmethod
    def fetch(cls, url):
        PlayoffLogger.get('remote').info(
            'fetching content for: %s', url)
        if url not in cls.url_cache:
            cls.url_cache[url] = requests.get(url).text
            PlayoffLogger.get('remote').info(
                'content for %s not in cache: retrieved %d bytes',
                url, len(cls.url_cache[url]))
        return bs(cls.url_cache[url], 'lxml')
