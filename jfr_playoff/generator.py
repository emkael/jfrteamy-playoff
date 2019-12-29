from datetime import datetime
import urlparse

from jfr_playoff.dto import coalesce
from jfr_playoff.template import PlayoffTemplate
from jfr_playoff.data import PlayoffData
from jfr_playoff.logger import PlayoffLogger


class PlayoffGenerator(object):
    def __init__(self, settings):
        self.data = PlayoffData(settings)
        self.page = settings.get('page')
        print self.page.get('favicon')
        PlayoffLogger.get('generator').info(
            'page settings: %s', self.page)
        self.team_box_settings = self.page.get('team_boxes', {})
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
                self.p_temp.get(
                    'PAGE_HEAD_FAVICON',
                    self.page['favicon']) \
                if len(self.page.get('favicon', '')) else '',
                self.page['title']),
            self.p_temp.get(
                'PAGE_BODY',
                self.page['logoh'],
                match_grid,
                self.get_swiss_links(),
                leaderboard_table,
                self.get_leaderboard_caption_table() \
                if leaderboard_table or (
                        'finishing_position_indicators' in self.page
                        and self.page['finishing_position_indicators']) \
                else '',
                self.p_temp.get(
                    'PAGE_BODY_FOOTER',
                    datetime.now().strftime('%Y-%m-%d o %H:%M:%S'))))

    def __get_team_label(self, team_name, template='MATCH_TEAM_LABEL'):
        if not self.team_box_settings.get('predict_teams', None):
            # override template if team predictions are not enabled
            template = 'MATCH_TEAM_LABEL'
        return self.p_temp.get(template, team_name)

    def __shorten_labels(self, labels, limit, separator, ellipsis):
        if limit > 0:
            current_length = 0
            shortened = []
            for l in range(0, len(labels)):
                if current_length + len(labels[l]) > limit:
                    # current label won't fit within limit, shorten it and stop
                    shortened.append(labels[l][0:limit-current_length] + ellipsis)
                    break
                else:
                    # current label fits, add it to output
                    shortened.append(labels[l])
                    current_length += len(labels[l])
                    if l < len(labels) - 1:
                        # if it's not the last label, separator will be added
                        # if it was the last label, next condition won't run and ellipsis won't be added
                        current_length += len(separator)
                    if current_length > limit:
                        # if separator puts us over the limit, add ellipsis and stop
                        shortened.append(ellipsis)
                        break
            labels = shortened
        return labels

    def get_match_table(self, match):
        rows = ''
        for team in match.teams:
            PlayoffLogger.get('generator').info(
                'generating HTML for team object: %s', team)
            # the easy part: team score cell
            score_html = self.p_temp.get('MATCH_SCORE', team.score)
            PlayoffLogger.get('generator').info(
                'score HTML for team object: %s', score_html.strip())
            # the hard part begins here.
            team_label = [] # label is what's shown in the table cell
            label_separator = self.team_box_settings.get('label_separator', ' / ')
            label_placeholder = self.team_box_settings.get('label_placeholder', '??')
            label_length_limit = self.team_box_settings.get('label_length_limit', self.page.get('label_length_limit', 0))
            label_ellipsis = self.team_box_settings.get('label_ellipsis', '(...)')
            team_name = []  # name is what's shown in the tooltip
            name_separator = self.team_box_settings.get('name_separator', '<br />')
            name_prefix = self.team_box_settings.get('name_prefix', '&nbsp;&nbsp;') # prefix (indent) for team names in the tooltip
            if (team.known_teams == 0) and not self.team_box_settings.get('predict_teams', False):
                PlayoffLogger.get('generator').info('no eligible teams and predictions are disabled')
                # we've got no teams eligible for the match and the prediction option is disabled
                team_label = ''
                team_name = ''
            else:
                # predicted teams are not in team.name, they're in tem.possible_name so corresponding spots in team.name are empty
                is_label_predicted = [name is None for name in team.name]
                # fetch labels (shortnames) for teams in both lists
                labels = [self.data.get_shortname(name) if name else None for name in team.name]
                PlayoffLogger.get('generator').info('eligible team labels: %s', labels)
                predicted_labels = [self.data.get_shortname(name) if name else None for name in team.possible_name]
                PlayoffLogger.get('generator').info('predicted team labels: %s', predicted_labels)
                for l in range(0, len(labels)):
                    if labels[l] is None:
                        if self.team_box_settings.get('predict_teams', False) and (len(predicted_labels) > l):
                            # fill team labels with either predictions...
                            labels[l] = predicted_labels[l]
                        else:
                            # ...or empty placeholders
                            labels[l] = label_placeholder
                # count how many teams are eligible (how many non-predicted teams are there)
                known_teams = len(is_label_predicted) - sum(is_label_predicted)
                PlayoffLogger.get('generator').info('detected %d known team(s), predicted mask: %s', known_teams, is_label_predicted)
                # the team's already selected, cut the label list to single entry
                if team.selected_team > -1:
                    PlayoffLogger.get('generator').info('pre-selected team #%d, label: %s', team.selected_team, labels[team.selected_team])
                    labels = [labels[team.selected_team]]
                    is_label_predicted = [False]
                if self.team_box_settings.get('sort_eligible_first', True):
                    # sort labels to move eligible teams in front of predicted teams
                    labels = [label for i, label in enumerate(labels) if not is_label_predicted[i]] \
                             + [label for i, label in enumerate(labels) if is_label_predicted[i]]
                PlayoffLogger.get('generator').info('team labels: %s', labels)
                if len([label for label in labels if label is not None]):
                    # we have at least one known/predicted team
                    for l in range(0, len(labels)):
                        # fill any remaining empty labels (i.e. these which had empty predictions available) with placeholders
                        labels[l] = coalesce(labels[l], label_placeholder)
                    # shorten concatenated label to specified combined length
                    labels = self.__shorten_labels(labels, label_length_limit, label_separator, label_ellipsis)
                    PlayoffLogger.get('generator').info('shortened team labels: %s', labels)
                    for l in range(0, len(labels)):
                        # concatenate labels, assigning appropriate classes to predicted teams
                        if self.team_box_settings.get('sort_eligible_first', True):
                            team_label.append(self.__get_team_label(
                                labels[l],
                                'MATCH_PREDICTED_TEAM_LABEL' if l >= known_teams else 'MATCH_TEAM_LABEL'))
                        else:
                            team_label.append(self.__get_team_label(
                                labels[l],
                                'MATCH_PREDICTED_TEAM_LABEL' if is_label_predicted[l] else 'MATCH_TEAM_LABEL'))
                # the team's already selected, cut the tooltip list to single entry
                if team.selected_team > -1:
                    PlayoffLogger.get('generator').info('pre-selected team #%d, name: %s', team.selected_team, team.name[team.selected_team])
                    team_name = [team.name[team.selected_team]]
                else:
                    # team names for tooltip
                    for name in team.name:
                        if name:
                            # every non-empty name gets some indentation
                            team_name.append(name_prefix + name)
                    if self.team_box_settings.get('predict_teams', False):
                        # remember where the list of eligible teams ends
                        known_teams = len(team_name)
                        for name in team.possible_name:
                            # append predicted team names, with indentation as well
                            if name:
                                team_name.append(name_prefix + name)
                        if len(team_name) > known_teams:
                            # we've added some predicted team names, so we add a header
                            team_name.insert(known_teams, self.p_temp.get('MATCH_POSSIBLE_TEAM_LIST_HEADER'))
                    if (len(team_label) > 1) and (match.running == 0) and (known_teams > 0):
                        # and we add a header for matches that haven't started yet and have multiple options for teams
                        team_name.insert(0, self.p_temp.get('MATCH_TEAM_LIST_HEADER'))
                # glue it all together
                team_label = label_separator.join(team_label)
                PlayoffLogger.get('generator').info('output teams label HTML: %s', team_label)
                team_name = name_separator.join(team_name)
                PlayoffLogger.get('generator').info('output teams name HTML: %s', team_name)
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
            winner_link = [
                str(m) for m in match.winner_matches
            ] if match.winner_matches is not None else []
            loser_link = [
                str(m) for m in match.loser_matches
            ] if match.loser_matches is not None else []
            place_loser_link = []
            place_winner_link = []
            if self.page.get('starting_position_indicators', None):
                for team in match.teams:
                    if len(team.place) > 0:
                        place_link = ['place-' + str(pl) for pl in team.place]
                        if len(team.place) > 1:
                            place_loser_link += place_link
                        else:
                            place_winner_link += place_link
            return self.p_temp.get(
                'MATCH_BOX',
                position[0], position[1],
                match.id,
                ' '.join(winner_link),
                ' '.join(loser_link),
                ' '.join(place_winner_link),
                ' '.join(place_loser_link),
                self.get_match_table(match))
        return ''

    def get_starting_position_box(self, positions, dimensions):
        if 'starting_position_indicators' not in self.page \
           or not self.page['starting_position_indicators']:
            return ''
        boxes = ''
        order = 0
        for place in sorted(positions):
            boxes += self.p_temp.get(
                'STARTING_POSITION_BOX',
                0,
                self.page['margin'] / 2 + int(float(order) / float(len(positions)) * dimensions[1]),
                place,
                self.p_temp.get('POSITION_BOX', place))
            order += 1
        return boxes

    def get_finishing_position_box(self, positions, position_info, dimensions, margin):
        if 'finishing_position_indicators' not in self.page \
           or not self.page['finishing_position_indicators']:
            return ''
        boxes = ''
        order = 0
        for place in sorted(positions):
            caption = self.get_caption_for_finishing_position(place)
            boxes += self.p_temp.get(
                'FINISHING_POSITION_BOX',
                self.page['margin'] / 2 + int(float(order) / float(len(positions)) * dimensions[1]),
                self.get_leaderboard_row_class(place),
                place,
                ' '.join([str(p) for p in position_info[place]['winner']]),
                ' '.join([str(p) for p in position_info[place]['loser']]),
                self.p_temp.get('CAPTIONED_POSITION_BOX', caption, place) if caption else self.p_temp.get('POSITION_BOX', place))
            order += 1
        return boxes

    def get_match_grid(self, dimensions, grid, matches):
        canvas_size = [
            dimensions[0] * (
                self.page['width'] + self.page['margin']
            ) + self.page['margin'],
            dimensions[1] * (
                self.page['height'] + self.page['margin']
            ) - self.page['margin']]
        if 'starting_position_indicators' not in self.page \
           or not self.page['starting_position_indicators']:
            canvas_size[0] -= self.page['margin']
        if 'finishing_position_indicators' not in self.page \
           or not self.page['finishing_position_indicators']:
            canvas_size[0] -= self.page['margin']
        PlayoffLogger.get('generator').info(
            'canvas size: %s', canvas_size)
        grid_boxes = ''
        col_no = 0
        starting_positions = set()
        finishing_positions = {}
        finishing_places = set()
        for phase in grid:
            grid_x = col_no * self.page['width'] + (col_no + 1) * self.page['margin'] \
                if self.page.get('starting_position_indicators', None) \
                   else col_no * (self.page['width'] + self.page['margin'])
            grid_boxes += self.get_phase_header(phase, grid_x)
            match_height = canvas_size[1] / len(phase.matches) \
                if len(phase.matches) > 0 else 0
            row_no = 0
            for match in phase.matches:
                grid_y = self.page['margin'] / 2 if dimensions[1] == 1 else \
                         int(row_no * match_height +
                             0.5 * (match_height - self.page['height']))
                PlayoffLogger.get('generator').info(
                    'calculated grid box (%d, %d) position: (%d, %d)',
                    col_no, row_no, grid_x, grid_y)
                if str(match) in self.canvas.get('box_positioning', {}):
                    if isinstance(self.canvas['box_positioning'][str(match)], list):
                        grid_x, grid_y = self.canvas['box_positioning'][str(match)][0:2]
                    else:
                        grid_y = float(self.canvas['box_positioning'][str(match)])
                    PlayoffLogger.get('generator').info(
                        'overridden box #%d position: (%d, %d)',
                        match, grid_x, grid_y)
                grid_boxes += self.get_match_box(
                    matches[match] if match is not None else None,
                    (grid_x, grid_y))
                if match is not None:
                    for team in matches[match].teams:
                        starting_positions.update(team.place)
                    for place in matches[match].loser_place + matches[match].winner_place:
                        if place not in finishing_positions:
                            finishing_positions[place] = {
                                'winner': [],
                                'loser': []
                            }
                        finishing_places.add(place)
                    for place in matches[match].winner_place:
                        finishing_positions[place]['winner'].append(match)
                    for place in matches[match].loser_place:
                        finishing_positions[place]['loser'].append(match)
                row_no += 1
            col_no += 1
        return self.p_temp.get(
            'MATCH_GRID',
            canvas_size[0], canvas_size[1],
            canvas_size[0], canvas_size[1],
            ' '.join(['data-%s="%s"' % (
                setting.replace('_', '-'), str(value)
            ) for setting, value in self.canvas.iteritems() if not isinstance(value, dict)]),
            self.get_starting_position_box(starting_positions, canvas_size),
            grid_boxes,
            self.get_finishing_position_box(
                finishing_places, finishing_positions, canvas_size, self.page['margin']
            )
        )

    def get_caption_for_finishing_position(self, position):
        for style in self.leaderboard_classes:
            if position in style['positions']:
                return style['caption']
        return None

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
        return '' \
            if flag is None \
               else self.p_temp.get(
                       'LEADERBOARD_ROW_FLAG',
                       ''
                       if bool(urlparse.urlparse(flag).netloc)
                       else 'images/',
                       flag)
