import urllib

from bs4 import BeautifulSoup as bs

class RemoteUrl:

    url_cache = {}

    @classmethod
    def fetch(cls, url):
        if url not in cls.url_cache:
            cls.url_cache[url] = urllib.urlopen(url).read()
        return bs(cls.url_cache[url], 'lxml')
