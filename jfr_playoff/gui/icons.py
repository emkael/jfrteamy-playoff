import os, sys

import Tkinter as tk

class GuiImage(object):
    icons = {}

    @staticmethod
    def __get_base_path():
        try:
            return os.path.join(sys._MEIPASS, 'res').decode(
                sys.getfilesystemencoding())
        except:
            return os.path.abspath(os.path.dirname(__file__)).decode(
                sys.getfilesystemencoding())

    @staticmethod
    def get_path(imageType, code, fileType='gif'):
        return os.path.join(
            GuiImage.__get_base_path(), imageType, '%s.%s' % (code, fileType))

    @staticmethod
    def __get_image(imageType, cache, code, fileType='gif'):
        if code not in cache:
            path = GuiImage.get_path(imageType, code, fileType)
            cache[code] = tk.PhotoImage(file=path)
        return cache[code]

    @staticmethod
    def get_icon(code):
        return GuiImage.__get_image('icons', GuiImage.icons, code)
