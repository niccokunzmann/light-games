from selenium.webdriver.common.keys import Keys
import subprocess

# other systems
def simulate_key_down(key):
    key = keys[key]
    # http://www.semicomplete.com/projects/xdotool/xdotool.xhtml
    subprocess.call(["xdotool", 'keydown', key])

def simulate_key_up(key):
    subprocess.call(["xdotool", 'keyup', key])

keys = {
    b"0" : "Left",
    b"1" : "Right",
    b"2" : "Up",
    b"3" : "Down",
    b"4" : "0x020",
    }

def click(x, y):
    subprocess.call(["xdotool", 'mousemove', str(int(x)), str(int(y))])
    subprocess.call(["xdotool", 'click', "1"])

def screenshot(x, y, width, height, file_name):
    subprocess.call(["import", '-window', 'root', file_name])

browser = None

def set_browser(_browser):
    global browser
    browser = _browser


def game_handles_key(key):
    return key in keys
    
__all__ = "simulate_key_down simulate_key_up click screenshot "\
          "set_browser game_handles_key".split()
