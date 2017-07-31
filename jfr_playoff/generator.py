from datetime import datetime
import template as p_temp
from data import PlayoffData

class PlayoffGenerator(object):
    def __init__(self, settings):
        self.settings = settings
        self.data = PlayoffData(self.settings)
        self.page = self.settings.get('page')
        self.canvas = {}
        if self.settings.has_section('canvas'):
            self.canvas = self.settings.get('canvas')

    def generate_content(self):
        return p_temp.PAGE % (
            p_temp.PAGE_HEAD % (
                p_temp.PAGE_HEAD_REFRESH % (self.page['refresh']) if self.page['refresh'] > 0 else '',
                self.page['title']
            ),
            p_temp.PAGE_BODY % (
                self.page['logoh'],
                self.get_match_grid(self.data.get_dimensions(), self.data.generate_phases(), self.data.fill_match_info()),
                self.get_leaderboard_table(self.data.fill_leaderboard()),
                p_temp.PAGE_BODY_FOOTER.decode('utf8') % (datetime.now().strftime('%Y-%m-%d o %H:%M'))
            )
        )

    def get_match_table(self, match):
        rows = ''
        for team in match.teams:
            rows += p_temp.MATCH_TEAM_ROW % (
                ' '.join(['winner' if team.name == match.winner else '',
                          'loser' if team.name == match.loser else '']).strip(),
                match.link,
                team.name,
                ' / '.join([self.data.get_shortname(name) for name in team.name.split('<br />')]),
                match.link,
                team.score
            )
        html = p_temp.MATCH_TABLE.decode('utf8') % (
            int(self.page['width'] * 0.75),
            int(self.page['width'] * 0.25),
            rows
        )
        if match.running > 0:
            html += p_temp.MATCH_RUNNING % (match.link, match.running)
        return html

    def get_match_grid(self, dimensions, grid, matches):
        grid_width = dimensions[0] * (
            self.page['width'] + self.page['margin']
        ) - self.page['margin']
        grid_height = dimensions[1] * (
            self.page['height'] + self.page['margin']
        ) - self.page['margin']
        grid_boxes = ''
        col_no = 0
        for column in grid:
            grid_x = col_no * (self.page['width'] + self.page['margin'])
            grid_header = p_temp.MATCH_GRID_PHASE_RUNNING if len([
                match for match in column if match is not None and matches[match].running > 0
            ]) > 0 else p_temp.MATCH_GRID_PHASE
            grid_boxes += grid_header % (
                self.settings.get('phases', col_no, 'link'),
                self.page['width'],
                grid_x,
                self.settings.get('phases', col_no, 'title')
            )
            row_no = 0
            column_height = grid_height / len(column)
            for match in column:
                grid_y = int(row_no * column_height + 0.5 * (column_height - self.page['height']))
                if match is not None:
                    grid_boxes += p_temp.MATCH_BOX % (
                        grid_x, grid_y,
                        match,
                        ' '.join([str(m) for m in matches[match].winner_matches]) if matches[match].winner_matches is not None else '',
                        ' '.join([str(m) for m in matches[match].loser_matches]) if matches[match].loser_matches is not None else '',
                        self.get_match_table(matches[match])
                    )
                row_no += 1
            col_no += 1
        canvas_attrs = []
        for setting, value in self.canvas.iteritems():
            canvas_attrs.append(
                'data-%s="%s"' % (setting.replace('_', '-'), str(value))
            )
        return p_temp.MATCH_GRID % (grid_width, grid_height, grid_width, grid_height, ' '.join(canvas_attrs), grid_boxes)

    def get_leaderboard_table(self, leaderboard):
        if len([t for t in leaderboard if t is not None]) == 0:
            return ''
        position = 1
        rows = ''
        for team in leaderboard:
            rows += p_temp.LEADERBOARD_ROW % (position, self.get_flag(team), team or '')
            position +=1
        html = p_temp.LEADERBOARD.decode('utf8') % (rows)
        return html

    def get_flag(self, team):
        flag = self.data.get_team_image(team)
        return '' if flag is None else p_temp.LEADERBOARD_ROW_FLAG % (flag)
