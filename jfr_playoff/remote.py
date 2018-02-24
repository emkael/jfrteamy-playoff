import re

import requests

from bs4 import BeautifulSoup as bs

class RemoteUrl:

    url_cache = {}

    @classmethod
    def fetch(cls, url):
        if url not in cls.url_cache:
            request = requests.get(url)
            encoding_match = re.search(
                'content=".*;( )?charset=(.*)"',
                request.content, re.IGNORECASE)
            if encoding_match:
                request.encoding = encoding_match.group(2)
            cls.url_cache[url] = request.text
        return bs(cls.url_cache[url], 'lxml')
