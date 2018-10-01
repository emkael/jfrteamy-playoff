import sys

def coalesce(*arg):
    for el in arg:
        if el is not None:
            return el
    return None


class Team(object):
    name = None
    score = 0.0

    def __init__(self):
        self.name = []

    def __unicode__(self):
        return u'%s (%.1f)' % (coalesce(self.name, '<None>'), self.score)

    def __repr__(self):
        return unicode(self).encode(sys.stdin.encoding)


class Match(object):
    id = None
    teams = None
    running = 0
    link = None
    winner = None
    loser = None
    winner_matches = None
    loser_matches = None

    def __repr__(self):
        return (u'#%d (%s) %s [%s]' % (
            self.id, coalesce(self.link, '<None>'), [unicode(team) for team in self.teams],
            u'finished' if self.running < 0 else (
                u'%d boards' % self.running))
        ).encode(sys.stdin.encoding)


class Phase(object):
    title = None
    link = None
    matches = []
    running = False

    def __repr__(self):
        return u'%s (%s) <%d matches> [%srunning]' % (
            self.title, coalesce(self.link, '<None>'),
            len(self.matches), '' if self.running else 'not ')

__all__ = ('Team', 'Match', 'Phase')
