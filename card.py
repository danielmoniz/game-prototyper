import os
import logging

from PIL import Image
from reportlab.lib.units import cm, mm

import resource

class BaseCard:

    def __init__(self, size, border_width, x_padding, y_padding):
        pass

    def __getitem__(self, attr):
        # A quick hack to allow for dynamic attribute retrieval in templates
        try:
            return getattr(self, attr)
        except AttributeError:
            return None

    def get_available_width(self, x_padding=None, one_side=False):
        if x_padding is None:
            x_padding = self.x_padding
        available_width = self.width - self.border_width * 2 - x_padding * 2
        if one_side:
            available_width = self.width - self.border_width - x_padding
        return available_width


    def get_available_height(self, y_offset=0, one_side=False):
        available_height = self.height - self.border_width * 2 - self.y_padding * 2
        if one_side:
            available_height = self.height - self.border_width - self.y_padding
        return available_height

    def get_left_bordered_edge(self, x_padding=0):
        return self.border_width + x_padding

    def get_right_bordered_edge(self, x_padding=0):
        return self.get_available_width(x_padding=x_padding, one_side=True)

    def get_left_edge(self, x_offset=0):
        return x_offset

    def get_right_edge(self, x_offset=0):
        return self.width - x_offset

    def get_top_bordered_edge(self, y_padding=0):
        return self.border_width + y_padding

    def get_bottom_bordered_edge(self, y_padding=0):
        return self.get_available_height(y_offset=y_padding, one_side=True)

    def get_top_edge(self, y_offset=0):
        return y_offset

    def get_bottom_edge(self, y_offset=0):
        return self.height - y_offset


class Card(BaseCard):

    def __init__(self, index):
        self.image = None
        self.card_id = index
        self.components = []

    def render(self):
        for component in self.components:
            if not component.rendered: component.render(self)

    def add_component(self, component):
        self.components.append(component)
        return component


def make_new_card(settings, data, game_name, index=0, front=True):
    card = Card(index)
    card.game_name = game_name

    card.card_type = get_card_type(data)

    set_card_settings(card, settings)

    scale_factor = float(settings.get(card.card_type, 'scale_factor'))
    card.width = int(float(settings.get(card.card_type, 'width')) * scale_factor * mm)
    card.height = int(float(settings.get(card.card_type, 'height')) * scale_factor * mm)
    card.actual_width = int(float(settings.get(card.card_type, 'width')) * mm)
    card.actual_height = int(float(settings.get(card.card_type, 'height')) * mm)
    card.actual_size = (card.actual_width, card.actual_height)
    card.size = (card.width, card.height)

    card.image = get_new_card_image(card, front)

    card.only_print = False
    card.no_print = False
    if 'only_print' in data and data['only_print']:
        if not isinstance(data['only_print'], basestring):
            if data['only_print'][0]:
                card.only_print = True
        else:
            card.only_print = True

    if 'no_print' in data and data['no_print']:
        card.no_print = True

    card.front = front
    card.front_or_back = 'front' if card.front else 'back'

    # store all data just in case
    card.data = data

    for key, value in data.iteritems():
        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
        if hasattr(card, key):# and getattr(card, key):
            logging.debug("Card property '{0}' already set! Pick another name.".format(key))
            continue
        setattr(card, key, value)

    return card


def get_card_type(data):
    card_type = 'main'
    if 'card_type' in data and data['card_type'].strip():
        card_type = data['card_type'].strip()
    return card_type


def set_card_settings(card, settings):
    for setting in settings.options(card.card_type):
        value = settings.get(card.card_type, setting)
        try:
            value = int(value)
        except ValueError:
            pass
        if hasattr(card, setting) and getattr(card, setting):
            logging.debug("Card property {0} already set! Pick another name.".format(setting))
            continue
        setattr(card, setting, value)


def get_new_card_image(card, front=True):
    # @TODO Make card colours configurable
    colour = 'white'
    if not front:
        colour = '#D8D8D8'
    image = Image.new("RGB", card.size)
    image.paste('black') # black border
    image.paste(colour, (card.border_width, card.border_width, card.size[0] - card.border_width, card.size[1] - card.border_width))
    return image


def save_card(card, location, file_name):
    if not hasattr(card, "name"):
        print "card:", card
        #print "Skipping card. No 'name' attribute."
        print '## Empty card name! Not saving.'
        return False

    make_dir(location)
    file_name = file_name.replace('/', '-')
    card.image.save("{0}{1}".format(location, file_name))


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_card_to_file(card, location, file_name=None):
    file_name = file_name or card.name
    file_name = card.name.replace('/', '-')
    full_file_location = "{0}{1}".format(location, file_name)
    with open(full_file_location, 'w') as f:
        f.write(card.image)


def set_resources(card):

    with resource.open_file('goods.txt') as f:
        lines = f.readlines()
        resources = [x.strip() for x in lines if bool(x.strip())]
        card.resources = resources


def set_icons(card):

    with resource.open_file('other_icons.txt') as f:
        lines = f.readlines()
        icons = [x.strip() for x in lines if bool(x.strip())]
        card.icons = icons


