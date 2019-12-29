import re

import requests

from bs4 import BeautifulSoup as bs
from jfr_playoff.logger import PlayoffLogger

class RemoteUrl:

    url_cache = {}

    @classmethod
    def fetch_raw(cls, url):
        PlayoffLogger.get('remote').info(
            'fetching content for: %s', url)
        if url not in cls.url_cache:
            request = requests.get(url)
            encoding_match = re.search(
                'content=".*;( )?charset=(.*)"',
                request.content, re.IGNORECASE)
            if encoding_match:
                request.encoding = encoding_match.group(2)
            cls.url_cache[url] = request.text
            PlayoffLogger.get('remote').info(
                'fetched %d bytes from remote location',
                len(cls.url_cache[url]))
        return cls.url_cache[url]

    @classmethod
    def fetch(cls, url):
        return bs(RemoteUrl.fetch_raw(url), 'lxml')
