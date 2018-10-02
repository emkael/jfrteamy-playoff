from datetime import datetime

from jfr_playoff.dto import coalesce
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

    def __get_team_label(self, team_name, template='MATCH_TEAM_LABEL'):
        if not self.page.get('predict_teams', None):
            # override template if team predictions are not enabled
            template = 'MATCH_TEAM_LABEL'
        return self.p_temp.get(template, team_name)

    def get_match_table(self, match):
        rows = ''
        for team in match.teams:
            # the easy part: team score cell
            score_html = self.p_temp.get('MATCH_SCORE', team.score)
            # the hard part begins here.
            team_label = [] # label is what's shown in the table cell
            label_separator = ' / '
            team_name = []  # name is what's shown in the tooltip
            name_separator = '<br />'
            name_prefix = '&nbsp;&nbsp;' # prefix (indent) for team names in the tooltip
            if (team.known_teams == 0) and not self.page.get('predict_teams', False):
                # we've got no teams eligible for the match and the prediction option is disabled
                team_label = ''
                team_name = ''
            else:
                # predicted teams are not in team.name, they're in tem.possible_name so corresponding spots in team.name are empty
                is_label_predicted = [name is None for name in team.name]
                # fetch labels (shortnames) for teams in both lists
                labels = [self.data.get_shortname(name) if name else None for name in team.name]
                predicted_labels = [self.data.get_shortname(name) if name else None for name in team.possible_name]
                for l in range(0, len(labels)):
                    if labels[l] is None:
                        if self.page.get('predict_teams', False) and (len(predicted_labels) > l):
                            # fill team labels with either predictions...
                            labels[l] = predicted_labels[l]
                        else:
                            # ...or empty placeholders
                            labels[l] = '??'
                # count how many teams are eligible (how many non-predicted teams are there)
                known_teams = len(is_label_predicted) - sum(is_label_predicted)
                # sort labels to move eligible teams in front of predicted teams
                # TODO: should this be optional?
                labels = [label for i, label in enumerate(labels) if not is_label_predicted[i]] \
                         + [label for i, label in enumerate(labels) if is_label_predicted[i]]
                if len([label for label in labels if label is not None]):
                    # we have at least one known/predicted team
                    for l in range(0, len(labels)):
                        # fill any remaining empty labels (i.e. these which had empty predictions available) with placeholders
                        labels[l] = coalesce(labels[l], '??')
                        # concatenate labels, assigning appropriate classes to predicted teams
                        team_label.append(self.__get_team_label(
                            labels[l],
                            'MATCH_PREDICTED_TEAM_LABEL' if l >= known_teams else 'MATCH_TEAM_LABEL'))
                # team names for tooltip
                for name in team.name:
                    if name:
                        # every non-empty name gets some indentation
                        team_name.append(name_prefix + name)
                if self.page.get('predict_teams', False):
                    # remember where the list of eligible teams ends
                    known_teams = len(team_name)
                    for name in team.possible_name:
                        # append predicted team names, with indentation as well
                        if name:
                            team_name.append(name_prefix + name)
                    if len(team_name) != known_teams:
                        # we've added some predicted team names, so we add a header
                        team_name.insert(known_teams, self.p_temp.get('MATCH_POSSIBLE_TEAM_LIST_HEADER'))
                if (len(team_label) > 1) and (match.running == 0):
                    # and we add a header for matches that haven't started yet and have multiple options for teams
                    team_name.insert(0, self.p_temp.get('MATCH_TEAM_LIST_HEADER'))
                # glue it all together
                team_label = label_separator.join(team_label)
                team_name = name_separator.join(team_name)
            team_html = self.p_temp.get(
                'MATCH_TEAM_LINK',
                match.link, team_name, team_label) \
                if match.link is not None \
                   else self.p_temp.get(
                           'MATCH_TEAM_NON_LINK',
                           team_name, team_label)
            rows += self.p_temp.get(
                'MATCH_TEAM_ROW',
                ' '.join([
                    'winner' if (match.winner is not None) and (match.winner in team.name) else '',
                    'loser' if (match.loser is not None) and (match.loser in team.name) else ''
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
