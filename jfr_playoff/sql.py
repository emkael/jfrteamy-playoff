MATCH_RESULTS = '''
SELECT t1.fullname, t2.fullname, matches.carry,
 matches.vph, matches.vpv, matches.corrh, matches.corrv
FROM #db#.matches matches
JOIN #db#.teams t1
 ON t1.id = #db#.matches.homet
JOIN #db#.teams t2
 ON t2.id = #db#.matches.visit
WHERE matches.tabl = %s AND matches.rnd = %s
'''

BOARD_COUNT = '''
SELECT segmentsperround*boardspersegment,
 SUM(sc1.contract IS NOT NULL AND sc2.contract IS NOT NULL)
FROM #db#.scores sc1
JOIN #db#.scores sc2
 ON sc1.rnd = sc2.rnd
 AND sc1.segment = sc2.segment
 AND sc1.tabl = sc2.tabl
 AND sc1.board = sc2.board
 AND sc1.room = 1
 AND sc2.room = 2
JOIN #db#.admin
WHERE sc1.tabl = %s AND sc1.rnd = %s
'''

TOWEL_COUNT = '''
SELECT #db#.admin.boardspersegment * SUM(#db#.segments.towel > 0)
FROM #db#.segments
JOIN #db#.admin
WHERE #db#.segments.tabl = %s AND #db#.segments.rnd = %s
'''

PREFIX = '''
SELECT shortname FROM #db#.admin
'''

SWISS_ENDED = '''
SELECT (rnd = roundcnt) AND (segm = segmentsperround) FROM #db#.admin
'''

SWISS_RESULTS = '''
SELECT #db#.teams.fullname,
 SUM(IF(#db#.matches.homet = #db#.teams.id, vph+corrh, vpv+corrv))
  + #db#.teams.score,
 #db#.teams.grupa
FROM #db#.teams
LEFT JOIN #db#.matches
 ON (#db#.teams.id = #db#.matches.homet OR #db#.teams.id = #db#.matches.visit)
WHERE #db#.teams.bye = 0
GROUP BY #db#.teams.id
'''
