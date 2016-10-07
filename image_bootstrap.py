#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script retrieves icons from thenounproject.com (using their API and
credentials) based on the goods and resources (e.g. costs) in your game.
It takes a few command line arguments but defaults to grabbing icons for each
item listed in your goods.txt/other_icons.txt files.
"""

import argparse
import json

import requests
from requests_oauthlib import OAuth1

parser = argparse.ArgumentParser(description="Generate resource images/icons for your project.")
parser.add_argument('game_name', help="The directory name for your game.")
parser.add_argument('-s', '--search', nargs='*', help="The term(s) to search.")
parser.add_argument('-n', '--names', required=False, nargs='*', help="The name(s) of the image(s) for the search term(s).")
parser.add_argument('-l', '--limit', type=int, default=3, required=False, help="The number of images to download.")
parser.add_argument('-k', '--skip', type=int, default=0, required=False, help="The number of results to skip.")
parser.add_argument('-p', '--public', action="store_true", help="Pull only images in the public domain for which no attribution is needed.")
parser.add_argument('-c', '--collection', help="Take images from this collection with this slug.")
args = parser.parse_args()

if args.names and not args.search:
    print 'Cannot set names without setting search terms.'
    exit()
if args.names and len(args.names) != len(args.search):
    print 'The number of names provided do not match the number of search terms.'
    exit()
if args.search and args.collection:
    print "Cannot search as well as ask for a specific collection."
    exit()

project = args.game_name
search_terms = args.search
icon_names = args.names
image_limit = args.limit
offset = args.skip
public_only = args.public
collection = args.collection

api_keys_file_name = 'thenounproject_api_keys.txt'
key, secret = None, None
try:
    with open(api_keys_file_name, 'r') as f:
        key = f.readline().strip()
        secret = f.readline().strip()
except IOError:
    print 'Must create file for api keys named {0}'.format(api_keys_file_name)
    exit()

if not key or not secret:
    print 'Missing api keys in file {0}'.format(api_keys_file_name)
    exit()


def save_image(image, file_path):
    with open(file_path, 'w+') as f:
        for chunk in image.iter_content(1024):
            f.write(chunk)

def add_license_info(image_info, file_path, practical_name, file_name):
    with open(file_path, 'a') as f:
        if image_info['license_description'] == 'public-domain':
            return
        f.write("{0}\n".format(practical_name))
        f.write(u"\tLicense: {0}\n".format(image_info['license_description']))
        f.write("\t")
        f.write(image_info['attribution'].encode('utf-8'))
        f.write("\n")


def save_icon_data(search_term, name, icon_location, attributions_location):
    print "Search term:", search_term
    if name != search_term:
        print "name:", name
    auth = OAuth1(key, secret)
    endpoint = "http://api.thenounproject.com/icons/{0}?limit={1}&limit_to_public_domain={2}&offset={3}".format(search_term, image_limit, int(public_only), offset)

    response = requests.get(endpoint, auth=auth)
    try:
        content = json.loads(response.content)
    except ValueError:
        return
    for i, icon in enumerate(content['icons']):
        icon_url = icon['preview_url']
        icon_image = requests.get(icon_url)

        practical_name = "{0}{1}".format(name, i + offset + 1)
        if i + offset == 0:
            practical_name = name
        file_name = "{0}.png".format(practical_name)

        save_image(icon_image, "{0}{1}".format(icon_location, file_name))
        add_license_info(icon, attributions_location, practical_name, file_name)


def get_collection(search_term, name):
    print "Collection:", search_term
    if name != search_term:
        print "name:", name
    auth = OAuth1(key, secret)
    endpoint = "http://api.thenounproject.com/collection/{0}/icons?limit={1}&limit_to_public_domain={2}&offset={3}".format(search_term, image_limit, int(public_only), offset)

    response = requests.get(endpoint, auth=auth)
    try:
        content = json.loads(response.content)
    except ValueError:
        print "Something went wrong with the response for the request:"
        print endpoint
        return
    return content['icons']


def save_icons(icon_data, name, icon_location, attributions_location):
    if not icon_data:
        return
    for i, icon in enumerate(icon_data):
        icon_url = icon['preview_url']
        icon_image = requests.get(icon_url)

        practical_name = "{0}{1}".format(name, i + offset + 1)
        if i + offset == 0:
            practical_name = name
        file_name = "{0}.png".format(practical_name)

        save_image(icon_image, "{0}{1}".format(icon_location, file_name))
        add_license_info(icon, attributions_location, practical_name, file_name)


icon_location = "{0}/resources/".format(project)
attributions_location = "{0}/attributions.txt".format(project)

with open(attributions_location, 'a') as f:
    f.write('\n' + '-'*20 + '\n\n')

if search_terms:
    for i, search_term in enumerate(search_terms):
        name = search_term
        if icon_names:
            name = icon_names[i]
        save_icon_data(search_term, name, icon_location, attributions_location)
elif collection:
    name = collection
    if icon_names:
        name = icon_names[0]
    icon_data = get_collection(collection, name)
    save_icons(icon_data, name, icon_location, attributions_location)
else:
    files_to_parse = ['goods.txt', 'other_icons.txt']
    for file_name in files_to_parse:
        location = project + '/resources/' + file_name
        with open(location) as f:
            lines = f.readlines()
            config = [x.strip() for x in lines if bool(x.strip())]

        for line in config:
            segments = line.split()
            search_term = line.split()[0]
            name = search_term
            for segment in segments:
                if segment[0] == '{' and segment[-1] == '}':
                    search_term = segment[1:-1]
                    break

            save_icon_data(search_term, name, icon_location, attributions_location)
