"""
Prints images to file of the cards. Supports back sides for easy card cutting.
"""
import math
import os
import ConfigParser
import logging

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.pagesizes import letter

import card_creator

def print_cards(game_name, data_files, card_names):
    fronts, backs = card_creator.create_cards(game_name, data_files=data_files, card_names=card_names)

    only_print_fronts = [card for card in fronts if card and card.only_print]
    only_print_backs = [card for card in backs if card and card.only_print]

    if len(only_print_fronts) > 0:
        fronts = only_print_fronts
        backs = only_print_backs

    fronts = remove_no_print_cards(fronts)
    backs = remove_no_print_cards(backs)

    grouped_fronts = group_cards_by_size(fronts)
    grouped_backs = group_cards_by_size(backs)

    page_images_fronts = []
    for fronts in grouped_fronts:
        make_page(fronts, page_images_fronts)
    page_images_backs = []
    for backs in grouped_backs:
        make_page(backs, page_images_backs, backs=True)

    combined_pages = []
    for i in range(len(page_images_fronts)):
        combined_pages.append(page_images_fronts[i])
        combined_pages.append(page_images_backs[i])

    directory = card_creator.get_printouts_location(game_name, True)
    name = 'all_cards'
    if not os.path.exists(directory):
        os.makedirs(directory)
    c = canvas.Canvas('{0}/{1}.pdf'.format(directory, name), pagesize=letter)
    scale_factor = fronts[0].scale_factor
    make_document(game_name, c, combined_pages, fronts_and_backs=True, scale_factor=scale_factor)
    c.save()


def group_cards_by_size(cards):
    grouped_cards = []
    last_card = None
    current_set = []

    for card in cards:
        if last_card and card.size != last_card.size:
            grouped_cards.append(current_set)
            current_set = [card]
        else:
            current_set.append(card)
        last_card = card
    grouped_cards.append(current_set)

    return grouped_cards


def remove_no_print_cards(cards):
    return [card for card in cards if card and not card.no_print]


def make_document(game_name, canvas, pages, fronts_and_backs=False, scale_factor=1):

    front = True
    for i in range(len(pages)):
        page = pages[i]

        directory = card_creator.get_printouts_location(game_name, True)
        directory += 'pages'
        if not os.path.exists(directory):
            os.makedirs(directory)
        name = 'page{0}'.format(i)

        if not front:
            name = 'page{0}_backs'.format(i)
        image_location = '{0}/{1}.png'.format(directory, name)
        page.save(image_location)
        scaled_size = tuple(x / scale_factor for x in page.size)

        x_offset = (letter[0] - scaled_size[0]) / 2
        y_offset = (letter[1] - scaled_size[1]) / 2

        front_adjustment = get_page_adjustment(game_name, 'front')
        back_adjustment = get_page_adjustment(game_name, 'back')

        back_adjustment = back_adjustment or (0, 0)
        front_adjustment = front_adjustment or (0, 0)

        if front:
            x_offset += front_adjustment[0]
            y_offset += front_adjustment[1]
        else:
            x_offset += back_adjustment[0]
            y_offset += back_adjustment[1]

        actual_width, actual_height = canvas.drawImage(image_location, x_offset, y_offset, scaled_size[0], scaled_size[1])

        canvas.showPage()
        if fronts_and_backs:
            front = not front


def get_page_adjustment(game_name, side):
    print_settings = ConfigParser.ConfigParser()
    settings_location = "{0}/resources/print_settings.txt".format(game_name)
    try:
        print_settings.read(settings_location)
    except ConfigParser.MissingSectionHeaderError:
        print "page settings file formatted incorrectly. Use a section title in the form of [title]."
        return False

    try:
        if not print_settings.sections(): # file empty or does not exist
            return False
        x_adjustment = float(print_settings.get(side, 'x')) * mm
        y_adjustment = float(print_settings.get(side, 'y')) * mm
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
        logging.info("Failed to retrieve print settings from file.")
        return False

    return (x_adjustment, y_adjustment)


def make_page(cards, page_images, backs=False):
    if len(cards) == 0:
        return

    margin = 0.35 * inch # standard margin is 0.25", but pages can be shifted
    max_page_width = letter[0] - 2 * margin
    max_page_height = letter[1] - 2 * margin
    max_cards_wide = int(math.floor(max_page_width / cards[0].actual_width))
    max_cards_high = int(math.floor(max_page_height / cards[0].actual_height))

    cards_on_sheet = (max_cards_wide, max_cards_high)
    card_size_pixels = cards[0].size
    #card_size_pixels = cards[0].actual_size
    page_size_pixels = (card_size_pixels[0] * cards_on_sheet[0], card_size_pixels[1] * cards_on_sheet[1])

    page_image = Image.new("RGB", page_size_pixels, "white")
    direction = 1
    x_offset = 0
    y_offset = 0
    if backs:
        x_offset = page_image.size[0] - card_size_pixels[0]
        direction = -1

    initial_x_offset = x_offset

    card_number = 0
    for card in cards:
        print card.name
        page_image.paste(card.image, (x_offset, y_offset))
        card_number += 1
        x_offset += card_size_pixels[0] * direction

        if x_offset >= page_size_pixels[0]:
            x_offset = initial_x_offset
            y_offset += card_size_pixels[1]

        if x_offset < 0: # going backwards
            x_offset = initial_x_offset
            y_offset += card_size_pixels[1]

        if y_offset >= page_size_pixels[1]:
            x_offset = 0
            y_offset += card_size_pixels[1]
            break

    page_images.append(page_image)
    print '---'
    make_page(cards[card_number:], page_images, backs)


def run_print(args):
    print_cards(args.game_name, args.data_files, args.cards)
