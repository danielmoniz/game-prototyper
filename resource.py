
from PIL import Image, ImageDraw, ImageFont

game_name = None

def get_location(resource_name):
    if not game_name:
        raise ValueError("game_name not yet set! Use set_location() .")
    return "{0}/resources/{1}".format(game_name, resource_name)

def open_file(resource_name, options='r'):
    return open(get_location(resource_name), options)

def set_location(new_game_name):
    global game_name
    game_name = new_game_name

