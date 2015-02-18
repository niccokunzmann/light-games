import bottle
import threading
from bottle import route, run, static_file, redirect
import hashlib
import os

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
    maximum_game_index = number_of_games()
    game_index = int(game_index) % maximum_game_index
    next_game_index = (game_index + 1) % maximum_game_index
    previous_game_index = (game_index - 1) % maximum_game_index
    url = get_url_from_index(game_index)
    screenshot_path = "/" + get_screenshot_path(url)
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
        <img src="{screenshot_path}" width="100%"/>
    </body>
</html>
""".format(**locals())

@route("/images/<image_name:path>")
def get_image(image_name):
    if not os.path.exists("images/" + image_name):
        redirect(unknown_game_url)
    return static_file(image_name, root='images')

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




                          
