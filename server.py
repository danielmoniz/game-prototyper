from flask import Flask, url_for, request, send_from_directory, send_file
from flask import render_template
import jinja2
from jinja2 import Environment, PackageLoader

from card_creator import data
from card_creator import card as card_helper
from card_creator import player_numbers

app = Flask(__name__)
#app.jinja_env.add_extension('utils.jinja2htmlcompress.HTMLCompress')


@app.route('/favicon.ico/')
def favicon():
    return send_file('./favicon.png')


@app.route('/<game_name>/')
def display(game_name):
    data_file = request.args.get('data_file', None)
    data_files = [data_file]
    if data_file is None:
        data_files = None

    card_sides = request.args.get('card_sides', 'all')

    search = request.args.get('search', '').encode('UTF-8', errors='strict')
    search_card_type = request.args.get('card_type', '')
    page_size = request.args.get('page_size', 'letter')
    page_orientation = request.args.get('page_orientation', 'portrait')

    duplicates = request.args.get('duplicates', 'false')
    duplicates = duplicates.lower() == 'true'
    ignore_only_print = request.args.get('ignore_only_print', 'false')
    ignore_only_print = ignore_only_print.lower() == 'true'

    players = request.args.get('players', 0)
    if not players: players = 0
    players = int(players)

    skip_players = request.args.get('skip_players', 0)
    if not skip_players: skip_players = 0
    skip_players = int(skip_players)

    #macros = app.jinja_env.get_template('templates/macros.html')

    old_loader = app.jinja_env.loader
    app.jinja_env.loader = PackageLoader(game_name, 'cards')

    all_card_data = data.get_card_data(game_name, data_files=data_files, card_names=None)
    columns = all_card_data[0].keys()
    cards = { True: [], False: [] }
    only_print_cards = { True: [], False: [] }

    card_types = []
    sides = (True, False)
    for front in sides:
        for card_data in all_card_data:
            card = card_helper.Card(card_data, game_name, index=0, front=front)
            card_types.append(card.card_type)

            quantity = range(1, card.quantity + 1)
            if not duplicates: quantity = range(min(card.quantity, 1))

            for i in quantity:
                if (not card.card_type.startswith(search_card_type)
                    or not card.name.lower().startswith(search.lower())
                    or card.no_print):
                    continue

                card = card_helper.Card(card_data, game_name, index=i, front=front)
                player_numbers.update(card, i, players=players, skip_players=skip_players)
                if not card.skip:
                    cards[front].append(get_renderable_card(game_name, card))
                    if card.only_print and not ignore_only_print:
                        only_print_cards[front].append(get_renderable_card(game_name, card))

    if only_print_cards[True]:
        cards = only_print_cards

    styles = []
    styles.append(url_for('get_style', game_name=game_name, file_name='main.css'))
    for card_type in list(set(x for x in card_types if x != 'main')):
        styles.append(url_for('get_style', game_name=game_name, file_name='{0}.css'.format(card_type)))

    print_stylesheet = url_for('static', filename='styles/print.css')
    print_adjust_stylesheet = url_for('get_style', game_name=game_name, file_name='print_adjust.css')
    global_stylesheet = url_for('static', filename='styles/global_cards.css')
    default_stylesheet = url_for('static', filename='styles/default_cards.css')

    app.jinja_env.loader = old_loader
    resources = card_helper.Card.get_text_config('goods.txt')
    other_icons = card_helper.Card.get_text_config('other_icons.txt')
    icon_styles = get_icon_styles(game_name, resources, other_icons)

    return render_template(
        'cards.html',
        game_name=game_name,
        fronts=cards[True],
        backs=cards[False],
        styles=styles,
        icon_styles=icon_styles,
        style_global=global_stylesheet,
        style_default=default_stylesheet,
        style_print=print_stylesheet,
        style_print_adjust=print_adjust_stylesheet,
        columns=columns,
        page_size=page_size,
        page_orientation=page_orientation,
        duplicates=duplicates,
        players=players,
        skip_players=skip_players,
        search=search,
        card_type=search_card_type,
        card_sides=card_sides,
        ignore_only_print=ignore_only_print,
        )


@app.route('/<game_name>/<file_name>')
def get_file(game_name, file_name):
    path = "{0}/{1}".format(game_name, file_name)
    return get_file(path, game_name, file_name)


@app.route('/<game_name>/resource/<file_name>')
def get_resource(game_name, file_name):
    path = "{0}/resources/{1}".format(game_name, file_name)
    return get_file(path, game_name, file_name)


@app.route('/<game_name>/style/<file_name>')
def get_style(game_name, file_name):
    path = "{0}/cards/{1}".format(game_name, file_name)
    return get_file(path, game_name, file_name)


def get_file(path, game_name, file_name):
    if '..' in game_name or game_name.startswith('/'):
        abort(404)
    if '..' in file_name or file_name.startswith('/'):
        abort(404)
    try:
        return_file = send_file(path)
    except IOError:
        return 'Failed to load {0}'.format(file_name)
    return return_file


def get_renderable_card(game_name, card):
    env = app.jinja_env
    template_location = '{{0}}_{0}.html'.format(card.front_or_back)
    try:
        template = env.get_template(template_location.format(card.card_type))
    except jinja2.exceptions.TemplateNotFound:
        if card.card_type == 'main':
            card.html = 'Cannot find template'
            return card
        template = env.get_template(template_location.format('main'))

    card.html = template.render(card=card, testdict={'key': 'val'})
    return card


def get_icon_styles(game_name, resources, other_icons):
    styles = render_template('icons.css', game_name=game_name, resources=resources)
    styles += render_template('icons.css', game_name=game_name, resources=other_icons)
    return styles


def debug(text, print_text=True):
    print text
    print ''
    if print_text:
        return text
    return ''


def format_body_text(text):
    return text


def replace_items_with_tokens(text, item_list, template):
    return text


app.jinja_env.filters['debug'] = debug
app.jinja_env.filters['format_body_text'] = format_body_text
app.jinja_env.filters['replace_items_with_tokens'] = replace_items_with_tokens

if __name__ == '__main__':
    app.debug = True
    app.run()
