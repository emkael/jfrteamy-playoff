import re, urlparse

import requests

from bs4 import BeautifulSoup as bs
from jfr_playoff.logger import PlayoffLogger

class RemoteUrl:

    url_cache = {}

    @classmethod
    def fetch_raw(cls, url, gzip_fallback=False):
        PlayoffLogger.get('remote').info(
            'fetching content for: %s', url)
        if url not in cls.url_cache:
            request = requests.get(url)
            if request.status_code == 404 and gzip_fallback:
                old_url = urlparse.urlparse(url)
                new_url = old_url._replace(path=old_url.path+'.gz')
                new_url = urlparse.urlunparse(new_url)
                PlayoffLogger.get('remote').info(
                    'URL %s not found, trying GZIP variant %s',
                    url, new_url)
                request = requests.get(url)
            encoding_match = re.search(
                'content=".*;( )?charset=(.*?)"',
                request.content, re.IGNORECASE)
            if encoding_match:
                PlayoffLogger.get('remote').debug(
                    'Content encoding: %s',
                    encoding_match.group(2))
                request.encoding = encoding_match.group(2)
            cls.url_cache[url] = request.text
            PlayoffLogger.get('remote').info(
                'fetched %d bytes from remote location',
                len(cls.url_cache[url]))
        return cls.url_cache[url]

    @classmethod
    def fetch(cls, url):
        return bs(RemoteUrl.fetch_raw(url), 'lxml')

    @classmethod
    def clear_cache(cls):
        cls.url_cache = {}
