import serial
import os
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import threading

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

game_index = 0
def switch_game():
    global game_index
    game_index -= 1
    with open("games.txt") as f:
        for i, line in enumerate(f):
            if i == game_index:
                break
    if game_index < 0:
        game_index = i
    browser.get(line.strip())

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

keys_pressed = set()
def press_keys():
    while 1:
        time.sleep(0.05)
        for key in list(keys_pressed):
            # multithreading issues
            simulate_key_down(key)
key_pressed_thread = threading.Thread(target = press_keys)
key_pressed_thread.deamon = True
key_pressed_thread.start()

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

else:
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

def press_key(key):
    simulate_key_down(key)
    keys_pressed.add(key)

def release_key(key):
    if key in keys_pressed:
        keys_pressed.remove(key)
    simulate_key_up(key)

RELEASE = b'-'[0]
PRESS = b'+'[0]

def handle_key_event(event):
    action = event[1]
    
    if event[0] not in keys:
        if action == RELEASE:
            switch_game()
    else:
        key = event[0]
        element = browser.find_element_by_xpath("//body")
        element.click()
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
    #browser.maximize_window()
    return browser

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
    browser.close()
