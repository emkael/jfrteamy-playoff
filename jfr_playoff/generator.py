from datetime import datetime

from jfr_playoff.template import PlayoffTemplate
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
        self.leaderboard_classes = {}
        if settings.has_section('position_styles'):
            self.leaderboard_classes = settings.get('position_styles')
        PlayoffLogger.get('generator').info(
            'leaderboard classes settings: %s', self.leaderboard_classes)
        self.p_temp = PlayoffTemplate(
            settings.get('i18n') if settings.has_section('i18n') else {})

    def generate_content(self):
        match_grid = self.get_match_grid(
            self.data.get_dimensions(),
            self.data.generate_phases(),
            self.data.fill_match_info())
        leaderboard_table = self.get_leaderboard_table()
        return self.p_temp.get(
            'PAGE',
            self.p_temp.get(
                'PAGE_HEAD',
                self.p_temp.get(
                    'PAGE_HEAD_REFRESH',
                    self.page['refresh']) \
                if self.page['refresh'] > 0 else '',
                self.page['title']),
            self.p_temp.get(
                'PAGE_BODY',
                self.page['logoh'],
                match_grid,
                self.get_swiss_links(),
                leaderboard_table,
                self.get_leaderboard_caption_table() if leaderboard_table else '',
                self.p_temp.get(
                    'PAGE_BODY_FOOTER',
                    datetime.now().strftime('%Y-%m-%d o %H:%M:%S'))))

    def get_match_table(self, match):
        rows = ''
        for team in match.teams:
            score_html = self.p_temp.get('MATCH_SCORE', team.score)
            team_label = ' / '.join([
                self.data.get_shortname(name) for name in
                team.name.split('<br />')])
            label_max_length = self.page.get('label_length_limit', 0)
            if label_max_length:
                team_label = team_label[:label_max_length] + (team_label[label_max_length:] and '(...)')
            team_html = self.p_temp.get(
                'MATCH_TEAM_LINK',
                match.link, team.name, team_label) \
                if match.link is not None \
                   else self.p_temp.get(
                           'MATCH_TEAM_NON_LINK',
                           team.name, team_label)
            rows += self.p_temp.get(
                'MATCH_TEAM_ROW',
                ' '.join([
                    'winner' if team.name == match.winner else '',
                    'loser' if team.name == match.loser else ''
                ]).strip(),
                team_html,
                self.p_temp.get(
                    'MATCH_LINK',
                    match.link, score_html) \
                if match.link is not None else score_html)
        html = self.p_temp.get(
            'MATCH_TABLE',
            int(self.page['width'] * 0.7),
            int(self.page['width'] * 0.2),
            rows)
        if match.running > 0:
            running_html = self.p_temp.get('MATCH_RUNNING', match.running)
            html += self.p_temp.get('MATCH_LINK', match.link, running_html) if match.link is not None else running_html
        PlayoffLogger.get('generator').info(
            'match table for #%d generated: %d bytes', match.id, len(html))
        return html

    def get_phase_header(self, phase, position):
        grid_header = self.p_temp.get(
            'MATCH_GRID_PHASE_RUNNING' if phase.running \
            else 'MATCH_GRID_PHASE',
            phase.title)
        if phase.link is not None:
            return self.p_temp.get(
                'MATCH_GRID_PHASE_LINK',
                phase.link,
                self.page['width'], position,
                grid_header)
        else:
            return self.p_temp.get(
                'MATCH_GRID_PHASE_NON_LINK',
                self.page['width'], position,
                grid_header)

    def get_match_box(self, match, position):
        if match is not None:
            return self.p_temp.get(
                'MATCH_BOX',
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
                grid_y = self.page['margin'] / 2 if dimensions[1] == 1 else \
                         int(row_no * match_height +
                             0.5 * (match_height - self.page['height']))
                PlayoffLogger.get('generator').info(
                    'grid box (%d, %d) position: (%d, %d)',
                    col_no, row_no, grid_x, grid_y)
                grid_boxes += self.get_match_box(
                    matches[match] if match is not None else None,
                    (grid_x, grid_y))
                row_no += 1
            col_no += 1
        return self.p_temp.get(
            'MATCH_GRID',
            canvas_size[0], canvas_size[1],
            canvas_size[0], canvas_size[1],
            ' '.join(['data-%s="%s"' % (
                setting.replace('_', '-'), str(value)
            ) for setting, value in self.canvas.iteritems()]),
            grid_boxes
        )

    def get_leaderboard_row_class(self, position):
        classes = []
        for style in self.leaderboard_classes:
            if position in style['positions']:
                classes.append(style['class'])
        return ' '.join(classes)

    def get_leaderboard_caption_table(self):
        rows = ''
        for style in self.leaderboard_classes:
            if 'caption' in style:
                rows += self.p_temp.get(
                    'LEADERBOARD_CAPTION_TABLE_ROW',
                    style['class'], style['caption'])
        return self.p_temp.get('LEADERBOARD_CAPTION_TABLE', rows) if rows else ''

    def get_leaderboard_table(self):
        leaderboard = self.data.fill_leaderboard()
        if len([t for t in leaderboard if t is not None]) == 0:
            return ''
        position = 1
        rows = ''
        for team in leaderboard:
            rows += self.p_temp.get(
                'LEADERBOARD_ROW',
                self.get_leaderboard_row_class(position),
                position, self.get_flag(team), team or '')
            position += 1
        html = self.p_temp.get('LEADERBOARD', rows)
        PlayoffLogger.get('generator').info(
            'leaderboard HTML generated: %d bytes', len(html))
        return html

    def get_swiss_links(self):
        info = []
        for event in self.data.get_swiss_info():
            event_label = self.p_temp.get('SWISS_DEFAULT_LABEL', event['position'])
            if event.get('label', None):
                event_label = event['label']
            info.append((self.p_temp.get('SWISS_LINK',
                                         event['link'], event_label) \
                         if event['finished'] \
                         else self.p_temp.get(
                                 'SWISS_RUNNING_LINK',
                                 event['link'], event_label)))
        html = '\n'.join(info)
        PlayoffLogger.get('generator').info(
            'swiss HTML generated: %d bytes', len(html))
        return html

    def get_flag(self, team):
        flag = self.data.get_team_image(team)
        return '' if flag is None else self.p_temp.get('LEADERBOARD_ROW_FLAG', flag)
