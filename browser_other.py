from selenium.webdriver.common.keys import Keys

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

def screenshot(x, y, width, height, file_name):
    browser.get_screenshot_as_file(file_name)

browser = None

def set_browser(_browser):
    global browser
    browser = _browser


def game_handles_key(key):
    return key in keys
    
__all__ = "simulate_key_down simulate_key_down click screenshot "\
          "set_browser game_handles_key".split()
