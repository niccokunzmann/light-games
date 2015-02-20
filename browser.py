#!/usr/bin/env python3
import serial
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import threading
import overview_site

if os.name == 'nt':
    import browser_nt
    from browser_nt import *
elif os.name == 'posix':
    import browser_posix
    from browser_posix import *
else:
    import browser_other
    from browser_other import *
browser_lock = threading.RLock()

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
    subprocess.Popen(["java", "-jar", "selenium-server-standalone-2.44.0.jar"])

def click_in_the_middle():
    with browser_lock:
        x = browser.get_window_position()["x"]
        y = browser.get_window_position()["y"]
        height = browser.get_window_size()["height"]
        width = browser.get_window_size()["width"]
        click(x + width // 2, y + height // 2)

def switch_to_game_url(url):
    with browser_lock:
        browser.get(url)
        print("opened page", url)
        element = browser.find_element_by_xpath("//body")
        element.send_keys("")
        element.click()
        time.sleep(4)
        if "scratch.mit.edu" in url:
            click_in_the_middle()

current_game_index = 0

is_in_overview = False

def switch_to_game(game_index):
    global current_game_index, is_in_overview
    current_game_index = game_index
    url = overview_site.get_url_from_index(game_index)
    switch_to_game_url(url)
    is_in_overview = False

def switch_game():
    if not is_in_overview:
        screenshot_game()
        open_overview()

def open_overview():
    global is_in_overview
    overview_url = overview_site.get_overview_game_url(current_game_index)
    switch_to_game_url(overview_url)
    is_in_overview = True

overview_site.switch_to_game = switch_to_game

def screenshot_game():
    url = overview_site.get_url_from_index(current_game_index)
    path = overview_site.get_screenshot_path(url)
    with browser_lock:
        x = browser.get_window_position()["x"]
        y = browser.get_window_position()["y"]
        height = browser.get_window_size()["height"]
        width = browser.get_window_size()["width"]
        screenshot(x, y, width, height, path)
    
def open_serial():
    ports = list_serial_ports()
    for port in reversed(ports):
        s = serial.Serial(port)
        s.timeout = 5;
        data = s.readline()
        if SERIAL_IDENTIFIER not in data:
            print('wrong serial:', data, port)
            s.close()
            continue
        print("Serial Port:", port)
        return s
    return None

def get_key_event_from_serial():
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
            with browser_lock:
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

def press_key(key):
    with browser_lock:
        simulate_key_down(key)
    add_key_pressed(key)

def release_key(key):
    remove_key_pressed(key)
    with browser_lock:
        simulate_key_up(key) #multithreading issues may arise

RELEASE = b'-'[0]
PRESS = b'+'[0]

def handle_key_event(event):
    action = event[1]
    
    if not game_handles_key(event[0]):
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
        
def maximize_browser():
    with browser_lock:
        #http://stackoverflow.com/questions/9601618/selenium-webdriver-c-fullscreen-mode-in-browser
        browser.find_element_by_tag_name("html").send_keys(Keys.F11)
        #browser.maximize_window()

def get_web_window():
    with browser_lock:
        browser = webdriver.Firefox()
        browser.set_window_position(0,0)
        return browser

if __name__ == '__main__':
    serial_to_light = open_serial()
    if not serial_to_light:
        print("""Could not open a connection to the Arduino.
Maybe the Arduino is not connected
or it does not run the right program or
somebody uses the Arduino already. Exiting...""")
        exit(1)

    start_selenium_server()
    browser = get_web_window()
    with browser_lock:
        set_browser(browser)
    maximize_browser()
    open_overview()
    try:
        while 1:
            key_event = get_key_event_from_serial()
            if key_event:
                handle_key_event(key_event)
    finally:
        remove_all_key_presses()
        serial_to_light.close()
        with browser_lock:
            browser.close()
