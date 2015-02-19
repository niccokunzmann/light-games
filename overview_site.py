import bottle
import threading
from bottle import route, run, static_file, redirect, response
import hashlib
import os
try:
    import qrcode
    has_qrcode = True
except ImportError:
    has_qrcode = False
import io

i = 0

unknown_game_url = "https://upload.wikimedia.org/wikipedia/commons/6/6a/Dice.jpg"

def get_url_from_index(game_index):
    lines = get_games()
    game_index %= len(lines)
    url = lines[game_index]
    url = url.strip()
    return url

def get_screenshot_path(url):
    if isinstance(url, int):
        url = get_url_from_index(url)
    if isinstance(url, str):
        url = url.encode("utf-8")
    hash = hashlib.sha256(url).hexdigest()
    hash = hash[:30]
    return "images/" + hash + ".png"

def get_games():
    with open("games.txt") as f:
        return list(f)

def number_of_games():
    return len(get_games())

@route('/')
def overview_site():
    redirect("/games/0")

@route("/games/<game_index:int>")
def serve_site(game_index):
    global i
    maximum_game_index = number_of_games()
    game_index = int(game_index) % maximum_game_index
    next_game_index = (game_index + 1) % maximum_game_index
    previous_game_index = (game_index - 1) % maximum_game_index
    url = get_url_from_index(game_index)
    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
    # http://stackoverflow.com/questions/8749434/how-to-prevent-browser-image-caching
    screenshot_path = "/" + get_screenshot_path(url)
    screenshot_path_previous = "/" + get_screenshot_path(get_url_from_index(previous_game_index)) + "?t=" + str(i)
    screenshot_path_next = "/" + get_screenshot_path(get_url_from_index(next_game_index)) + "?t=" + str(i)
    i+= 1
    t = i
    return """
<html>
    <head>
        <title>
            {url}
        </title>
    </head>
    <body>
        <script type="text/javascript"><!--
	  function navigateThroughGames(event) {{
            if (event.keyCode == 39 || event.keyCode == 13) {{
              document.location = "/games/" + {next_game_index};
            }} else if (event.keyCode == 37) {{
              document.location = "/games/" + {previous_game_index};
            }} else if (event.charCode == 32) {{
              document.location = "/play/" + {game_index};
            }}
          }}
          document.onkeypress = navigateThroughGames;
        // --></script>
        <div width="100%">
            <img src="{screenshot_path_previous}?t={t}" width="10%" align="top"/>
            <img src="{screenshot_path}?t={t}" width="75%"/>
            <img src="{screenshot_path_next}?t={t}" width="10%"  align="top"/>
        </div>
        <div width="100%">
            <center><img src="/qrcode/{game_index}.png?t={t}" height="90%"/></center>
        </div>
    </body>
</html>
""".format(**locals())

@route("/images/<image_name:path>")
def get_image(image_name):
    if not os.path.exists("images/" + image_name):
        redirect(unknown_game_url)
    else:
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        # http://stackoverflow.com/questions/8749434/how-to-prevent-browser-image-caching
        return static_file(image_name, root='images')

@route("/qrcode/<game_index:int>.png")
def get_qr_code(game_index):
    if not has_qrcode:
        print('no qrcode')
        return None
    url = get_url_from_index(game_index)
    i = qrcode.make(url)
    b = io.BytesIO()
    i.save(b)
    b.seek(0)
    return b

@route("/play/<game_index:int>")
def play_game(game_index):
    maximum_game_index = number_of_games()
    game_index = int(game_index) % maximum_game_index
    switch_to_game(game_index)

def switch_to_game(game_index):
    print('play:', game_index)

HOST = 'localhost'
PORT = 8081

t = threading.Thread(target = run, kwargs = dict(host=HOST, port=PORT, debug=True))
t.deamon = True
t.start()

overview_url = 'http://{}:{}'.format(HOST, PORT)

def get_overview_game_url(game_index):
    return overview_url + '/games/' + str(game_index)




                          
