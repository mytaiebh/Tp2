"""
Future Todo (lower priority, need to figure out how to do it, or a lot of work):
    Collage editor - add more collage modes (grids)
    Rework cropping editor
    export to facebook - https://github.com/mobolic/facebook-sdk , https://blog.kivy.org/2013/08/using-facebook-sdk-with-python-for-android-kivy/
    RAW import if possible - https://github.com/photoshell/rawkit , need to get libraw working
"""
from main.PhotoManager import PhotoManager

"""
Todo:
    implement a .nomedia file that will make spm ignore a folder
    Need to think of a way to divide up years abstractly
"""

import time

start = time.perf_counter()

import sys
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
import os

os.environ['KIVY_VIDEO'] = 'ffpyplayer'
import threading

# all these are needed to get ffpyplayer working on linux

from kivy.config import Config

Config.window_icon = "data/icon.png"
from kivy.core.window import Window

try:
    import win32timezone
except:
    pass

from generalconstants import *

print('Startup Time: ' + str(time.perf_counter() - start))

version = sys.version_info
kivy.require('1.10.0')
lock = threading.Lock()

if desktop:
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    # Config.set('kivy', 'keyboard_mode', 'system')
    Window.minimum_height = 600
    Window.minimum_width = 800
    Window.maximize()
else:
    Window.softinput_mode = 'below_target'

if platform == 'android':
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

if __name__ == '__main__':
    PhotoManager().run()
