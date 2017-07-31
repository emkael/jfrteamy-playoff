import glob, json, os, readline, shutil, socket, sys
from datetime import datetime
from urlparse import urljoin
from playoff import sql as p_sql
from playoff import template as p_temp

def complete_filename(text, state):
    return (glob.glob(text+'*')+[None])[state]

if len(sys.argv) > 1:
    settings_file = sys.argv[1]
else:
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete_filename)
    settings_file = raw_input('JSON settings file: ')

if not os.path.exists(settings_file):
    print 'Settings file "%s" not found' % settings_file
    sys.exit(1)

settings = json.load(open(settings_file))
teams = settings['teams']
leaderboard = [None] * len(teams)

from playoff.db import PlayoffDB
db = PlayoffDB(settings['database'])

def get_shortname(fullname):
    for team in settings['teams']:
        if team[0] == fullname:
            return team[1]
    return fullname

def get_team_image(fullname):
    for team in settings['teams']:
        if team[0] == fullname and len(team) > 2:
            if team[2] is not None:
                return p_temp.LEADERBOARD_ROW_FLAG % (team[2])
    return ''

def get_match_table(match):
    rows = ''
    for team in match.teams:
        rows += p_temp.MATCH_TEAM_ROW % (
            ' '.join(['winner' if team.name == match.winner else '',
                      'loser' if team.name == match.loser else '']).strip(),
            match.link,
            team.name,
            ' / '.join([get_shortname(name) for name in team.name.split('<br />')]),
            match.link,
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
        grid_header = p_temp.MATCH_GRID_PHASE_RUNNING if len([match for match in column if match is not None and matches[match].running > 0]) > 0 else p_temp.MATCH_GRID_PHASE
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
            if match is not None:
                grid_boxes += p_temp.MATCH_BOX % (
                    grid_x, grid_y,
                    match,
                    ' '.join([str(m) for m in matches[match].winner_matches]) if matches[match].winner_matches is not None else '',
                    ' '.join([str(m) for m in matches[match].loser_matches]) if matches[match].loser_matches is not None else '',
                    get_match_table(matches[match])
                )
            row_no += 1
        col_no += 1
    canvas_settings = []
    if 'canvas' in settings:
        for setting, value in settings['canvas'].iteritems():
            canvas_settings.append(
                'data-%s="%s"' % (setting.replace('_', '-'), str(value))
            )
    return p_temp.MATCH_GRID % (width, height, width, height, ' '.join(canvas_settings), grid_boxes)

def get_leaderboard_table(leaderboard):
    if len([t for t in leaderboard if t is not None]) == 0:
        return ''
    position = 1
    rows = ''
    for team in leaderboard:
        rows += p_temp.LEADERBOARD_ROW % (position, get_team_image(team), team or '')
        position +=1
    html = p_temp.LEADERBOARD.decode('utf8') % (rows)
    return html

class Team:
    name = ''
    score = 0.0

class Match:
    teams = None
    running = 0
    link = None
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
        row = db.fetch(match['database'], p_sql.PREFIX, ())
        info.link = '%srunda%d.html' % (row[0], match['round'])
    except Exception as e:
        pass
    try:
        row = db.fetch(match['database'], p_sql.MATCH_RESULTS, (match['table'], match['round']))
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
            elif isinstance(match['teams'][i], list):
                info.teams[i].name = '<br />'.join(match['teams'][i])
            else:
                match_teams = []
                if 'winner' in match['teams'][i]:
                    match_teams += [
                        match_info[winner_match].winner
                        for winner_match in match['teams'][i]['winner']
                    ]
                if 'loser' in match['teams'][i]:
                    match_teams += [
                        match_info[loser_match].loser
                        for loser_match in match['teams'][i]['loser']
                    ]
                if 'place' in match['teams'][i]:
                    match_teams += [
                        teams[place-1][0]
                        for place in match['teams'][i]['place']
                    ]
                info.teams[i].name = '<br />'.join([
                    team if team is not None else '??'
                    for team in match_teams]
                ) if len([team for team in match_teams if team is not None]) > 0 else ''

    try:
        towels = db.fetch(match['database'], p_sql.TOWEL_COUNT, (match['table'], match['round']))
        row = [0 if r is None else r for r in db.fetch(match['database'], p_sql.BOARD_COUNT, (match['table'], match['round']))]
        if row[1] > 0:
            info.running = int(row[1])
        if row[1] >= row[0] - towels[0]:
            info.running = 0
            info.winner = info.teams[0].name if info.teams[0].score > info.teams[1].score else info.teams[1].name
            info.loser = info.teams[1].name if info.teams[0].score > info.teams[1].score else info.teams[0].name
    except Exception as e:
        pass
    return info

grid = []
for phase in settings['phases']:
    phase_grid = [None] * (len(phase['dummies']) + len(phase['matches']) if 'dummies' in phase else len(phase['matches']))
    phase_pos = 0
    for match in phase['matches']:
        if 'dummies' in phase:
            while phase_pos in phase['dummies']:
                phase_pos += 1
        match_info[match['id']] = get_match_info(match)
        match_info[match['id']].link = phase['link'] if match_info[match['id']].link is None else urljoin(phase['link'], match_info[match['id']].link)
        phase_grid[phase_pos] = match['id']
        phase_pos += 1
    grid.append(phase_grid)

for team in settings['teams']:
    if len(team) > 3:
        leaderboard[team[3]-1] = team[0]

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
grid_rows = max([len(phase['matches']) + len(phase['dummies']) if 'dummies' in phase else len(phase['matches']) for phase in settings['phases']])
grid_height = grid_rows * (settings['page']['height'] + settings['page']['margin']) - settings['page']['margin']
grid_width = grid_columns * (settings['page']['width'] + settings['page']['margin']) - settings['page']['margin']

content = (
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

output = open(settings['output'], 'w')
output.write(content)
output.close()

output_path = os.path.dirname(settings['output'])
script_output_path = os.path.join(output_path, 'sklady/playoff.js')

shutil.copy(unicode(os.path.join(os.path.dirname(__file__), 'playoff.js')),
            unicode(script_output_path))

if settings['goniec']['enabled']:
    try:
        content_lines = [(output_path.strip('/') + '/').replace('/', '\\')] + [os.path.basename(settings['output']), 'sklady/playoff.js'] + ['bye', '']
        print '\n'.join(content_lines)
        goniec = socket.socket()
        goniec.connect((settings['goniec']['host'], settings['goniec']['port']))
        goniec.sendall('\n'.join(content_lines))
        goniec.close()
    except socket.error:
        pass
