import logging as log


class PlayoffLogger:

    @classmethod
    def setup(cls, level):
        log.basicConfig(
            level=getattr(log, level),
            streamhandler=log.StreamHandler(),
            format='%(levelname)-8s %(name)-8s %(message)s')

    @classmethod
    def get(cls, category=''):
        return log.getLogger(category)
