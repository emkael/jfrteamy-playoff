import json, os, shutil, sys
import mysql.connector
from datetime import datetime
from playoff import sql as p_sql
from playoff import template as p_temp

settings = json.load(open(sys.argv[1]))
teams = settings['teams']
leaderboard = [None] * len(teams)

database = mysql.connector.connect(
    user=settings['database']['user'],
    password=settings['database']['pass'],
    host=settings['database']['host'],
    port=settings['database']['port']
)
db_cursor = database.cursor(buffered=True)

def db_fetch(db, sql, params):
    db_cursor.execute(sql.replace('#db#', db), params)
    row = db_cursor.fetchone()
    return row

def get_shortname(fullname):
    for team in settings['teams']:
        if team[0] == fullname:
            return team[1]
    return fullname

def get_match_table(match):
    rows = ''
    for team in match.teams:
        rows += p_temp.MATCH_TEAM_ROW % (
            team.name,
            ' / '.join([get_shortname(name) for name in team.name.split('<br />')]),
            team.score
        )
    html = p_temp.MATCH_TABLE.decode('utf8') % (
        int(settings['page']['width'] * 0.75),
        int(settings['page']['width'] * 0.25),
        rows
    )
    if match.running > 0:
        html += p_temp.MATCH_RUNNING % (match.link, match.running)
    return html

def get_match_grid(grid, matches, width, height):
    grid_boxes = ''
    col_no = 0
    for column in grid:
        grid_x = col_no * (settings['page']['width'] + settings['page']['margin'])
        grid_header = p_temp.MATCH_GRID_PHASE_RUNNING if len([match for match in column if matches[match].running > 0]) > 0 else p_temp.MATCH_GRID_PHASE
        grid_boxes += grid_header % (
            settings['phases'][col_no]['link'],
            settings['page']['width'],
            grid_x,
            settings['phases'][col_no]['title']
        )
        row_no = 0
        column_height = height / len(column)
        for match in column:
            grid_y = int(row_no * column_height + 0.5 * (column_height - settings['page']['height']))
            grid_boxes += p_temp.MATCH_BOX % (
                grid_x, grid_y,
                match,
                ' '.join([str(m) for m in matches[match].winner_matches]) if matches[match].winner_matches is not None else '',
                ' '.join([str(m) for m in matches[match].loser_matches]) if matches[match].loser_matches is not None else '',
                get_match_table(matches[match])
            )
            row_no += 1
        col_no += 1
    return p_temp.MATCH_GRID % (width, height, width, height, grid_boxes)

def get_leaderboard_table(leaderboard):
    position = 1
    rows = ''
    for team in [team if team is not None else '' for team in leaderboard]:
        rows += p_temp.LEADERBOARD_ROW % (position, team)
        position +=1
    html = p_temp.LEADERBOARD.decode('utf8') % (rows)
    return html

class Team:
    name = ''
    score = 0.0

class Match:
    teams = None
    running = 0
    link = '#'
    winner = None
    loser = None
    winner_matches = None
    loser_matches = None

match_info = {}

def get_match_info(match):
    info = Match()
    info.teams = [Team(), Team()]
    info.winner_matches = []
    info.loser_matches = []
    for i in range(0, 2):
        if 'winner' in match['teams'][i]:
            info.winner_matches += match['teams'][i]['winner']
        if 'loser' in match['teams'][i]:
            info.loser_matches += match['teams'][i]['loser']
    info.winner_matches = list(set(info.winner_matches))
    info.loser_matches = list(set(info.loser_matches))
    try:
        row = db_fetch(match['database'], p_sql.MATCH_RESULTS, (match['table'], match['round']))
        info.teams[0].name = row[0]
        info.teams[1].name = row[1]
        info.teams[0].score = row[3] + row[5]
        info.teams[1].score = row[4] + row[6]
        if row[2] > 0:
            info.teams[0].score += row[2]
        else:
            info.teams[1].score -= row[2]
    except Exception as e:
        for i in range(0, 2):
            if isinstance(match['teams'][i], basestring):
                info.teams[i].name = match['teams'][i]
            else:
                teams = []
                if 'winner' in match['teams'][i]:
                    teams += [
                        match_info[winner_match].winner
                        for winner_match in match['teams'][i]['winner']
                    ]
                if 'loser' in match['teams'][i]:
                    teams += [
                        match_info[loser_match].loser
                        for loser_match in match['teams'][i]['loser']
                    ]
                info.teams[i].name = '<br />'.join([
                    team if team is not None else '??'
                    for team in teams]
                ) if len([team for team in teams if team is not None]) > 0 else ''

    try:
        row = db_fetch(match['database'], p_sql.BOARD_COUNT, (match['table'], match['round']))
        if row[1] > 0:
            info.running = int(row[1])
            if row[1] == row[0]:
                info.running = 0
                info.winner = info.teams[0].name if info.teams[0].score > info.teams[1].score else info.teams[1].name
                info.loser = info.teams[1].name if info.teams[0].score > info.teams[1].score else info.teams[0].name
    except Exception as e:
        pass
    return info

grid = []
for phase in settings['phases']:
    grid.append([])
    for match in phase['matches']:
        match_info[match['id']] = get_match_info(match)
        match_info[match['id']].link = phase['link']
        grid[-1].append(match['id'])

leaderboard_teams = {}
for phase in settings['phases']:
    for match in phase['matches']:
        if 'winner' in match:
            winner_key = tuple(match['winner'])
            if winner_key not in leaderboard_teams:
                leaderboard_teams[winner_key] = []
            leaderboard_teams[winner_key].append(match_info[match['id']].winner)
        if 'loser' in match:
            loser_key = tuple(match['loser'])
            if loser_key not in leaderboard_teams:
                leaderboard_teams[loser_key] = []
            leaderboard_teams[loser_key].append(match_info[match['id']].loser)

for positions, teams in leaderboard_teams.iteritems():
    positions = list(positions)
    if len(positions) == len([team for team in teams if team is not None]):
        for table_team in settings['teams']:
            if table_team[0] in teams:
                position = positions.pop(0)
                leaderboard[position-1] = table_team[0]

grid_columns = len(settings['phases'])
grid_rows = max([len(phase['matches']) for phase in settings['phases']])
grid_height = grid_rows * (settings['page']['height'] + settings['page']['margin']) - settings['page']['margin']
grid_width = grid_columns * (settings['page']['width'] + settings['page']['margin']) - settings['page']['margin']

output = open(settings['output'], 'w')
output.write((
    p_temp.PAGE % (
        p_temp.PAGE_HEAD % (
            p_temp.PAGE_HEAD_REFRESH % (settings['page']['refresh']) if settings['page']['refresh'] > 0 else '',
            settings['page']['title']
        ),
        p_temp.PAGE_BODY % (
            settings['page']['logoh'],
            get_match_grid(grid, match_info, grid_width, grid_height),
            get_leaderboard_table(leaderboard),
            p_temp.PAGE_BODY_FOOTER.decode('utf8') % (datetime.now().strftime('%Y-%m-%d o %H:%M'))
        )
    )).encode('utf8')
)

shutil.copy(unicode(os.path.join(os.path.dirname(__file__), 'playoff.js')),
            unicode(os.path.join(os.path.dirname(settings['output']), 'sklady/playoff.js')))
