import logging as log
import sys


def log_encoding():
    # if there's no sys.stdin (e.g. console-less GUI), revert to default
    return sys.stdin.encoding or 'utf8'


class PlayoffLogger:

    @classmethod
    def setup(cls, level):
        log.basicConfig(
            level=level,
            format='%(levelname)-8s %(name)-8s %(message)s')

    @classmethod
    def get(cls, category=''):
        return log.getLogger(category)
