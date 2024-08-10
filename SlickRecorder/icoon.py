from PIL import Image
import pystray
from pystray import MenuItem as item
import sys
import os

icon = None

def current_path():
    x = os.path.abspath(__file__).split('/')
    x.pop()
    return "/".join(x)

def get_image():
    image = Image.open(f'{current_path()}/red_dot.png')
    return image

def setup(icon):
    icon.visible = True

def start():
    global icon
    image = get_image()
    icon = pystray.Icon("SlickRecorder", image, "Recording...")
    icon.run(setup)

