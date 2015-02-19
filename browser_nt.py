# http://stackoverflow.com/questions/18096131/pywin32-sendkeys-windows-button-keypress
# http://stackoverflow.com/questions/1823762/sendkeys-for-python-3-1-on-windows/2004267#2004267
import win32api
import win32con
from win32con import KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP
import time

def simulate_key_down(key):
    key = keys[key]
    win32api.keybd_event(key, key, 0, 0)

def simulate_key_down(key):
    key = keys[key]
    win32api.keybd_event(key, key,  KEYEVENTF_KEYUP, 0)
    
    
keys = {
    b"0" : win32con.VK_LEFT,
    b"1" : win32con.VK_RIGHT,
    b"2" : win32con.VK_UP,
    b"3" : win32con.VK_DOWN,
    b"4" : win32con.VK_SPACE,
    }

def click(x, y):
    print("click", x, y)
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
    time.sleep(0.1)

def screenshot(x, y, width, height, file_name):
    import screenshot
    print('screenshot', x, y, width, height)
    screenshot.screenshot(file_name)

def set_browser(_browser):
    pass

def game_handles_key(key):
    return key in keys

__all__ = "simulate_key_down simulate_key_down click screenshot "\
          "set_browser game_handles_key".split()
