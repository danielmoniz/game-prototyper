"""
This parses data supplied in the form of resources/data.csv. It compiles lists
of the fronts and backs of cards (Card objects) and returns them.
"""
from __future__ import division
import csv
import sys
import imp
import logging

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
    card = card_helper.Card(data, game_name, index=index, front=front)
    card.set_resources()
    card.set_icons()

    return card


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

