"""
This module commands the other modules. It parses data supplied in the form 
of resources/data.csv. It compiles lists of the fronts and backs of cards and 
returns them.
This file should be called from a script that can handle lists of card images.
"""
from __future__ import division
import math
import csv
import os
import sys
import imp
import ConfigParser
import logging
import functools

import resource

import card as card_helper


def get_card_data(game_name, data_files=None, card_names=None):
    """
    The parameter game needs to match the name of a folder containing the 
    relevant files to build the game's cards.
    """
    resource.set_location(game_name)

    data = parse_data(game_name, data_files=data_files)
    formatted_data = group_rows_by_card_name(data)
    return formatted_data


def build_card_object(data, game_name, index=0, front=True):
    card_type = card_helper.get_card_type(data)

    card = card_helper.make_new_card(data, game_name, index=index, front=front)
    card_helper.set_resources(card)
    card_helper.set_icons(card)

    return card


def create_cards(game_name, data_files=None, card_names=None):
    """
    The parameter game needs to match the name of a folder containing the 
    relevant files to build the game's cards.
    """
    resource.set_location(game_name)

    data = parse_data(game_name, data_files=data_files)

    card_settings = ConfigParser.ConfigParser()
    settings_location = resource.get_location("cards.txt")
    card_settings.read(settings_location)
    card_settings.sections()

    formatted_data = group_rows_by_card_name(data)
    fronts = []
    backs = []

    for i, row in enumerate(formatted_data):
        row = formatted_data[i]
        if card_names and not card_name_in_list(row['name'], card_names):
            continue

        try:
            quantity = int(row['quantity'])
        except KeyError:
            quantity = 1
            print "You are not specifying the quantity of each card. This is highly recommended."

        for j in range(quantity):
            front = build_card(card_settings, row, game_name, index=i, front=True)
            fronts.append(front)
            back = build_card(card_settings, row, game_name, index=i, front=False)
            backs.append(back)

            if card_names:
                front.only_print = True
                back.only_print = True

    return fronts, backs


def card_name_in_list(card_name, names):
    for name in names:
        if card_name.lower().startswith(name.lower()):
            return True
    return False


def group_rows_by_card_name(data):
    """
    Look for instances of a row without a name that still has data.
    Then combine this data into an array for compactness.
    These rows allow for having 5 cells arrayed vertically with data in them,
    instead of having them arrayed horizontally and having a hideous
    spreadsheet.

    Eg.
    name    quantity    text
    Farm    2           Some text
                        More text about the Farm
    Smithy  1           Smithy text here
    ... and so on.
    """
    formatted_data = []
    last_data = None
    rows_since_last_data = 0
    grouped_columns = []

    for row in data:
        if row['name']:
            if row['name'].startswith('#'): continue
            if last_data:
                formatted_data.append(last_data)
            last_data = row
            rows_since_last_data = 0
            continue

        rows_since_last_data += 1

        for column, value in row.iteritems():
            if value and value.strip():
                value = value.strip()
                if value.startswith('#'): continue # allow for comments
                if rows_since_last_data == 1:
                    last_data[column] = [last_data[column]]
                    if column not in grouped_columns:
                        grouped_columns.append(column)
                last_data[column].append(value)

    formatted_data.append(last_data)
    make_grouped_columns_lists(formatted_data, grouped_columns)
    return formatted_data


def make_grouped_columns_lists(data, grouped_columns):
    """convert all columns that are sometimes grouped to lists for consistency.
    """
    logging.debug("grouped_columns: {0}".format(grouped_columns))
    for row in data:
        for column in grouped_columns:
            if column not in row:
                continue
            if row[column] and isinstance(row[column], basestring):
                row[column] = [row[column]]


def get_settings_section(settings, section):
    options = settings.options(section)


def build_card(card_settings, data, game_name, index=0, front=True):
    card_type = card_helper.get_card_type(data)

    try:
        options = card_settings.options(card_type)
    except ConfigParser.NoSectionError as e:
        print 'Please create cards.txt to set up your card settings.'
        print "data['name']:", data['name']
        print "card_type:", card_type
        raise e
        #return False

    card = card_helper.make_new_card(card_settings, data, game_name, index=index, front=front)
    card_helper.set_resources(card)

    file_name = "{0}.py".format(card.card_type)
    file_path = "./{0}/{1}".format(game_name, file_name)
    #file_path = "./{0}".format(file_name)

    try:
        if card.card_type in sys.modules:
            card_module = sys.modules[card.card_type]
        else:
            card_module = imp.load_source(file_name, file_path)
    except IOError:
        print "Card type {0} has no builder file at {1}.".format(card.card_type, file_path)
        return card

    if front:
        try:
            card_module.create_card_front
        except AttributeError as e:
            print 'No card front specified for {0}'.format(card.name)
            return card
        card = card_module.create_card_front(card)

    else:
        try:
            card_module.create_card_back
        except AttributeError:
            logging.info('No card backing specified for {0}'.format(card.name))
            return card
        card = card_module.create_card_back(card)

    return card


def parse_data(game_name, data_files=None):

    if not data_files:
        data_files_location = "{0}/resources/data_files.txt".format(game_name)
        try:
            with resource.open_file('data_files.txt') as f:
                lines = f.readlines()
                data_files = [x.strip() + '.csv' for x in lines if bool(x.strip())]
        except IOError:
            data_files = ('data.csv',)

    searchable_rows = []
    logging.debug("data_files:{0}".format(data_files))
    for data_file in data_files:
        logging.debug("data_file:{0}".format(data_file))
        file_location = "{0}/resources/{1}".format(game_name, data_file)
        searchable_rows += parse_data_file(file_location)

    return searchable_rows


def parse_data_file(file_location):
    with open(file_location, 'r') as data:
        reader = csv.reader(data)
        keys = reader.next()
        keys = [x.lower().strip() for x in keys if x.strip()]
        searchable_rows = []
        logging.debug(keys)
        logging.debug('-'*5)

        for row in reader:
            searchable_row = {}

            for i in range(len(keys)):
                if not keys[i].strip():
                    continue
                searchable_row[keys[i]] = row[i]
            searchable_rows.append(searchable_row)
    return searchable_rows


def save_cards_to_disk(fronts, backs, extension):
    cards = fronts + backs
    for card in cards:
        path, name = get_card_save_location(card, extension)
        if not path:
            continue
        make_dir(path)
        card_helper.save_card(card, path, name)

    for card in backs:
        path, name = get_card_save_location(card, extension)
        if not path:
            continue
        make_dir(path)
        card_helper.save_card(card, path, name)


def get_card_save_location(card, extension):
    if not hasattr(card, 'game_name'):
        return (False, False)
    directory = get_printouts_location(card.game_name)
    side = 'fronts'
    if not card.front:
        side = 'backs'
    subdir = "card {0} (singles)".format(side)

    path = "{0}/{1}/_{2}/".format(directory, subdir, card.card_type)
    if card.card_type == 'main':
        path = "{0}/{1}/".format(directory, subdir)

    file_name = card.file_name if hasattr(card, 'file_name') else card.name
    full_file_name = "{0}.{1}".format(file_name, extension)
    return path, full_file_name


def get_printouts_location(game_name, trailing_slash=False):
    directory = game_name + "/printouts"
    if trailing_slash:
        directory += '/'
    return directory


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

