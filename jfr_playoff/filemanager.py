import os
import shutil
import socket

from jfr_playoff.logger import PlayoffLogger

import __main__


class PlayoffFileManager(object):

    def __init__(self, settings):
        self.goniec = settings.get('goniec') if settings.has_section('goniec') else None
        PlayoffLogger.get('filemanager').info('goniec settings: %s', self.goniec)
        self.output_file = settings.get('output')
        PlayoffLogger.get('filemanager').info('output file: %s', self.output_file)
        self.output_path = os.path.dirname(
            self.output_file
        ).strip(os.sep)
        if len(self.output_path) > 0:
            self.output_path += os.sep
        PlayoffLogger.get('filemanager').info('output path: %s', self.output_path)
        self.files = set()

    def reset(self):
        self.files.clear()

    def register_file(self, path):
        if path.startswith(self.output_path):
            PlayoffLogger.get('filemanager').info('registering file: %s', path)
            self.files.add(path.replace(self.output_path, ''))
        else:
            PlayoffLogger.get('filemanager').info(
                'file: %s outside of %s, not registering', path, self.output_path)

    def write_content(self, content):
        output_dir = os.path.dirname(self.output_file)
        if len(output_dir) > 0:
            if not os.path.exists(output_dir):
                PlayoffLogger.get('filemanager').info(
                    'output directory %s does not exist, creating',
                    output_dir)
                os.makedirs(output_dir)
        output = open(self.output_file, 'w')
        PlayoffLogger.get('filemanager').info(
            'writing %d bytes into file %s',
            len(content), self.output_file)
        output.write(content.encode('utf8'))
        output.close()
        self.register_file(self.output_file)
        return self.output_file

    def copy_file(self, filename, path):
        source_path = unicode(os.path.join(
            os.path.dirname(__main__.__file__), filename))
        if not os.path.exists(source_path):
            raise IOError('File: %s missing from runtime directory' % (
                filename))
        output_path = os.path.join(self.output_path, path)
        output_dir = os.path.dirname(output_path)
        if len(output_dir) > 0:
            if not os.path.exists(output_dir):
                PlayoffLogger.get('filemanager').info(
                    'output directory %s does not exist, creating',
                    output_dir)
                os.makedirs(output_dir)
        PlayoffLogger.get('filemanager').info(
            'copying file to %s', output_path)
        shutil.copy(source_path, unicode(output_path))
        self.register_file(output_path)
        return output_path

    def copy_scripts(self, script_path='sklady/playoff.js'):
        return self.copy_file('playoff.js', script_path)

    def copy_styles(self, sheet_path='css/playoff.css'):
        return self.copy_file('playoff.css', sheet_path)

    def send_files(self):
        if (self.goniec is not None) and self.goniec['enabled']:
            try:
                if 'host' not in self.goniec:
                    self.goniec['host'] = 'localhost'
                if 'port' not in self.goniec:
                    self.goniec['port'] = 8090
                content_lines = [self.output_path] + \
                                list(self.files) + \
                                ['bye', '']
                PlayoffLogger.get('goniec').info(
                    '\n'.join(content_lines))
                goniec = socket.socket()
                goniec.connect((self.goniec['host'], self.goniec['port']))
                goniec.sendall('\n'.join(content_lines))
                goniec.close()
            except socket.error:
                pass
