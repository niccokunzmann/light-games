import serial
import os
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import threading
import overview_site

SERIAL_IDENTIFIER = b"Light-Keyboard";

def list_serial_ports():
    ## got the code from
    ## http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    import os
    from serial.tools import list_ports
    # Windows
    if os.name == 'nt':
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append('COM'+str(i + 1))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        # Mac / Linux
        return [port[0] for port in list_ports.comports()]

def start_selenium_server():
    import subprocess
    subprocess.Popen(["javaw", "-jar", "selenium-server-standalone-2.44.0.jar"],
                     shell = True)

def click_in_the_middle():
    x = browser.get_window_position()["x"]
    y = browser.get_window_position()["y"]
    height = browser.get_window_size()["height"]
    width = browser.get_window_size()["width"]
    click(x + width // 2, y + height // 2)

def switch_to_game_url(url):
    browser.get(url)
    print("opened page", url)
    element = browser.find_element_by_xpath("//body")
    element.send_keys("")
    element.click()
    time.sleep(4)
    if "scratch.mit.edu" in url:
        click_in_the_middle()
    time.sleep(1)
    path = overview_site.get_screenshot_path(url)
    browser.get_screenshot_as_file(path)

current_game_index = 0

def switch_to_game(game_index):
    global current_game_index
    current_game_index = game_index
    url = overview_site.get_url_from_index(game_index)
    switch_to_game_url(url)

def switch_game():
    overview_url = overview_site.get_overview_game_url(current_game_index)
    switch_to_game_url(overview_url)

overview_site.switch_to_game = switch_to_game
    
def open_serial():
    ports = list_serial_ports()
    for port in reversed(ports):
        s = serial.Serial(port)
        s.timeout = 5;
        data = s.readline()
        if SERIAL_IDENTIFIER not in data:
            s.close()
            continue
        print("Serial Port:", port)
        return s
    return None

def get_key_event_form_serial():
    line = serial_to_light.readline()
    line = line.strip()
    if line and line[:-1].isdigit() and line[-1] in b"+-":
        return line[:-1], line[-1]
    elif line:
        print("Message from the Arduino:", line)

# continuous key presses

keys_pressed = set()
keys_pressing = set()
keys_removed = set()
def press_keys():
    while 1:
        time.sleep(0.05)
        for key in range(len(keys_removed)):
            key = keys_removed.pop()
            if key in keys_pressed:
                keys_pressed.remove(key)
            if key in keys_pressing:
                keys_pressing.remove(key)
        for key in keys_pressing:
            simulate_key_down(key)
        for key in range(len(keys_pressed)):
            keys_pressing.add(keys_pressed.pop())

key_pressed_thread = threading.Thread(target = press_keys)
key_pressed_thread.deamon = True
key_pressed_thread.start()

def add_key_pressed(key):
    keys_pressed.add(key)

def remove_key_pressed(key):
    keys_removed.add(key)

def remove_all_key_presses():
    keys_removed.update(keys_pressed)
    keys_removed.update(keys_pressing)

if os.name == 'nt':
    print("nt")
    # http://stackoverflow.com/questions/18096131/pywin32-sendkeys-windows-button-keypress
    # http://stackoverflow.com/questions/1823762/sendkeys-for-python-3-1-on-windows/2004267#2004267
    import win32api
    import win32con
    from win32con import KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP

    def simulate_key_down(key):
        key = keys[key]
        win32api.keybd_event(key, key, 0, 0)

    def simulate_key_up(key):
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

else:
    # other systems
    def simulate_key_down(key):
        key = keys[key]
        element = browser.find_element_by_xpath("//body")
        element.send_keys(key)
    
    def simulate_key_up(key):
        pass
    
    keys = {
        b"0" : Keys.LEFT,
        b"1" : Keys.RIGHT,
        b"2" : Keys.UP,
        b"3" : Keys.DOWN,
        b"4" : Keys.SPACE,
        }
    
    def click(x, y):
        pass

def press_key(key):
    simulate_key_down(key)
    add_key_pressed(key)

def release_key(key):
    remove_key_pressed(key)
    simulate_key_up(key) #multithreading issues may arise

RELEASE = b'-'[0]
PRESS = b'+'[0]

def handle_key_event(event):
    action = event[1]
    
    if event[0] not in keys:
        if action == RELEASE:
            switch_game()
    else:
        key = event[0]
        if action == RELEASE:
            print("release", key)
            release_key(key)
        elif action == PRESS:
            print("press", key)
            press_key(key)                                                                                                                                                                                                                                                                                                                                                                                                      
        else:
            print("unknown action", event)
        

def get_web_window():
    browser = webdriver.Firefox()
    browser.set_window_position(0,0)
    browser.maximize_window()
    return browser


def view_overview_site():
    

start_selenium_server()
serial_to_light = open_serial()
if not serial_to_light:
    print("""Could not open a connection to the Arduino.
Maybe the Arduino is not connected
or it does not run the right program. Exiting...""")
    exit(1)

browser = get_web_window()
switch_game()
try:
    while 1:
        key_event = get_key_event_form_serial()
        if key_event:
            handle_key_event(key_event)
finally:
    #browser.close()
    remove_all_key_presses()
