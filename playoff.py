from datetime import datetime
from urlparse import urljoin
import jfr_playoff.template as p_temp
from jfr_playoff.settings import PlayoffSettings

def get_shortname(fullname, teams):
    for team in teams:
        if team[0] == fullname:
            return team[1]
    return fullname

def get_team_image(fullname, teams):
    for team in teams:
        if team[0] == fullname and len(team) > 2:
            if team[2] is not None:
                return p_temp.LEADERBOARD_ROW_FLAG % (team[2])
    return ''

def get_match_table(match, teams, page_settings):
    rows = ''
    for team in match.teams:
        rows += p_temp.MATCH_TEAM_ROW % (
            ' '.join(['winner' if team.name == match.winner else '',
                      'loser' if team.name == match.loser else '']).strip(),
            match.link,
            team.name,
            ' / '.join([get_shortname(name, teams) for name in team.name.split('<br />')]),
            match.link,
            team.score
        )
    html = p_temp.MATCH_TABLE.decode('utf8') % (
        int(page_settings['width'] * 0.75),
        int(page_settings['width'] * 0.25),
        rows
    )
    if match.running > 0:
        html += p_temp.MATCH_RUNNING % (match.link, match.running)
    return html

def get_match_grid(grid, phases, matches, page_settings, width, height, teams, canvas_settings):
    grid_boxes = ''
    col_no = 0
    for column in grid:
        grid_x = col_no * (page_settings['width'] + page_settings['margin'])
        grid_header = p_temp.MATCH_GRID_PHASE_RUNNING if len([match for match in column if match is not None and matches[match].running > 0]) > 0 else p_temp.MATCH_GRID_PHASE
        grid_boxes += grid_header % (
            phases[col_no]['link'],
            page_settings['width'],
            grid_x,
            phases[col_no]['title']
        )
        row_no = 0
        column_height = height / len(column)
        for match in column:
            grid_y = int(row_no * column_height + 0.5 * (column_height - page_settings['height']))
            if match is not None:
                grid_boxes += p_temp.MATCH_BOX % (
                    grid_x, grid_y,
                    match,
                    ' '.join([str(m) for m in matches[match].winner_matches]) if matches[match].winner_matches is not None else '',
                    ' '.join([str(m) for m in matches[match].loser_matches]) if matches[match].loser_matches is not None else '',
                    get_match_table(matches[match], teams, page_settings)
                )
            row_no += 1
        col_no += 1
    canvas_attrs = []
    for setting, value in canvas_settings.iteritems():
        canvas_attrs.append(
            'data-%s="%s"' % (setting.replace('_', '-'), str(value))
        )
    return p_temp.MATCH_GRID % (width, height, width, height, ' '.join(canvas_attrs), grid_boxes)

def get_leaderboard_table(leaderboard, teams):
    if len([t for t in leaderboard if t is not None]) == 0:
        return ''
    position = 1
    rows = ''
    for team in leaderboard:
        rows += p_temp.LEADERBOARD_ROW % (position, get_team_image(team, teams), team or '')
        position +=1
    html = p_temp.LEADERBOARD.decode('utf8') % (rows)
    return html


def generate_content(grid, phases, match_info, teams, grid_width, grid_height, page_settings, canvas_settings, leaderboard):
    return p_temp.PAGE % (
        p_temp.PAGE_HEAD % (
            p_temp.PAGE_HEAD_REFRESH % (page_settings['refresh']) if page_settings['refresh'] > 0 else '',
            page_settings['title']
        ),
        p_temp.PAGE_BODY % (
            page_settings['logoh'],
            get_match_grid(grid, phases, match_info, page_settings, grid_width, grid_height, teams, canvas_settings),
            get_leaderboard_table(leaderboard, teams),
            p_temp.PAGE_BODY_FOOTER.decode('utf8') % (datetime.now().strftime('%Y-%m-%d o %H:%M'))
        )
    )

from jfr_playoff.filemanager import PlayoffFileManager

def main():
    s = PlayoffSettings()

    phase_settings = s.get('phases')
    from jfr_playoff.data import PlayoffData
    data = PlayoffData(s)
    grid = data.generate_phases()
    match_info = data.fill_match_info()
    leaderboard = data.fill_leaderboard()

    page_settings = s.get('page')
    grid_columns = len(phase_settings)
    grid_rows = max([len(phase['matches']) + len(phase['dummies']) if 'dummies' in phase else len(phase['matches']) for phase in phase_settings])
    grid_height = grid_rows * (page_settings['height'] + page_settings['margin']) - page_settings['margin']
    grid_width = grid_columns * (page_settings['width'] + page_settings['margin']) - page_settings['margin']

    content = generate_content(grid, phase_settings, match_info, s.get('teams'), grid_width, grid_height, page_settings, s.get('canvas') if s.has_section('canvas') else {}, leaderboard)

    file_manager = PlayoffFileManager(s)
    file_manager.write_content(content)
    file_manager.copy_scripts()
    file_manager.send_files()

main()
