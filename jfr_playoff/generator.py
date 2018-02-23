from datetime import datetime

import jfr_playoff.template as p_temp
from jfr_playoff.data import PlayoffData
from jfr_playoff.logger import PlayoffLogger


class PlayoffGenerator(object):
    def __init__(self, settings):
        self.data = PlayoffData(settings)
        self.page = settings.get('page')
        PlayoffLogger.get('generator').info(
            'page settings: %s', self.page)
        self.canvas = {}
        if settings.has_section('canvas'):
            self.canvas = settings.get('canvas')
        PlayoffLogger.get('generator').info(
            'canvas settings: %s', self.canvas)

    def generate_content(self):
        return p_temp.PAGE % (
            p_temp.PAGE_HEAD % (
                p_temp.PAGE_HEAD_REFRESH % (
                    self.page['refresh'])
                if self.page['refresh'] > 0 else '',
                self.page['title']),
            p_temp.PAGE_BODY % (
                self.page['logoh'],
                self.get_match_grid(
                    self.data.get_dimensions(),
                    self.data.generate_phases(),
                    self.data.fill_match_info()),
                self.get_swiss_links(),
                self.get_leaderboard_table(),
                p_temp.PAGE_BODY_FOOTER.decode('utf8') % (
                    datetime.now().strftime('%Y-%m-%d o %H:%M'))))

    def get_match_table(self, match):
        rows = ''
        for team in match.teams:
            score_html = p_temp.MATCH_SCORE % (team.score)
            team_label = ' / '.join([
                self.data.get_shortname(name) for name in
                team.name.split('<br />')])
            team_html = p_temp.MATCH_TEAM_LINK % (
                match.link, team.name, team_label) if match.link is not None \
                else p_temp.MATCH_TEAM_NON_LINK % (
                        team.name, team_label)
            rows += p_temp.MATCH_TEAM_ROW % (
                ' '.join([
                    'winner' if team.name == match.winner else '',
                    'loser' if team.name == match.loser else ''
                ]).strip(),
                team_html,
                p_temp.MATCH_LINK % (match.link, score_html) if match.link is not None else score_html)
        html = p_temp.MATCH_TABLE.decode('utf8') % (
            int(self.page['width'] * 0.75),
            int(self.page['width'] * 0.25),
            rows)
        if match.running > 0:
            running_html = p_temp.MATCH_RUNNING % (match.running)
            html += p_temp.MATCH_LINK % (match.link, running_html) if match.link is not None else running_html
        PlayoffLogger.get('generator').info(
            'match table for #%d generated: %d bytes', match.id, len(html))
        return html

    def get_phase_header(self, phase, position):
        if phase.running:
            grid_header = p_temp.MATCH_GRID_PHASE_RUNNING
        else:
            grid_header = p_temp.MATCH_GRID_PHASE
        grid_header = grid_header % (phase.title)
        if phase.link is not None:
            return p_temp.MATCH_GRID_PHASE_LINK % (
                phase.link,
                self.page['width'], position,
                grid_header)
        else:
            return p_temp.MATCH_GRID_PHASE_NON_LINK % (
                self.page['width'], position,
                grid_header)

    def get_match_box(self, match, position):
        if match is not None:
            return p_temp.MATCH_BOX % (
                position[0], position[1],
                match.id,
                ' '.join([
                    str(m) for m in match.winner_matches
                ]) if match.winner_matches is not None else '',
                ' '.join([
                    str(m) for m in match.loser_matches
                ]) if match.loser_matches is not None else '',
                self.get_match_table(match))
        return ''

    def get_match_grid(self, dimensions, grid, matches):
        canvas_size = (
            dimensions[0] * (
                self.page['width'] + self.page['margin']
            ) - self.page['margin'],
            dimensions[1] * (
                self.page['height'] + self.page['margin']
            ) - self.page['margin'])
        PlayoffLogger.get('generator').info(
            'canvas size: %s', canvas_size)
        grid_boxes = ''
        col_no = 0
        for phase in grid:
            grid_x = col_no * (self.page['width'] + self.page['margin'])
            grid_boxes += self.get_phase_header(phase, grid_x)
            match_height = canvas_size[1] / len(phase.matches)
            row_no = 0
            for match in phase.matches:
                grid_y = int(row_no * match_height +
                             0.5 * (match_height - self.page['height']))
                PlayoffLogger.get('generator').info(
                    'grid box (%d, %d) position: (%d, %d)',
                    col_no, row_no, grid_x, grid_y)
                grid_boxes += self.get_match_box(
                    matches[match] if match is not None else None,
                    (grid_x, grid_y))
                row_no += 1
            col_no += 1
        return p_temp.MATCH_GRID % (
            canvas_size[0], canvas_size[1],
            canvas_size[0], canvas_size[1],
            ' '.join(['data-%s="%s"' % (
                setting.replace('_', '-'), str(value)
            ) for setting, value in self.canvas.iteritems()]),
            grid_boxes
        )

    def get_leaderboard_table(self):
        leaderboard = self.data.fill_leaderboard()
        if len([t for t in leaderboard if t is not None]) == 0:
            return ''
        position = 1
        rows = ''
        for team in leaderboard:
            rows += p_temp.LEADERBOARD_ROW % (
                position, self.get_flag(team), team or '')
            position += 1
        html = p_temp.LEADERBOARD.decode('utf8') % (rows)
        PlayoffLogger.get('generator').info(
            'leaderboard HTML generated: %d bytes', len(html))
        return html

    def get_swiss_links(self):
        info = []
        for event in self.data.get_swiss_info():
            event_label = p_temp.SWISS_DEFAULT_LABEL % (event['position'])
            if 'label' in event and event['label'] is not None:
                event_label = event['label']
            info.append((p_temp.SWISS_LINK if event['finished'] else p_temp.SWISS_RUNNING_LINK) % (
                event['link'], event_label
            ))
        html = '\n'.join(info)
        PlayoffLogger.get('generator').info(
            'swiss HTML generated: %d bytes', len(html))
        return html

    def get_flag(self, team):
        flag = self.data.get_team_image(team)
        return '' if flag is None else p_temp.LEADERBOARD_ROW_FLAG % (flag)
