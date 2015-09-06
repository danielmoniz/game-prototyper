from flask import Flask, url_for, request, send_from_directory, send_file
from flask import render_template
import jinja2
from jinja2 import Environment, PackageLoader

import card_creator
import print_cards

app = Flask(__name__)


@app.route('/<game_name>/resource/<file_name>')
def get_resource(game_name, file_name):
    if '..' in game_name or game_name.startswith('/'):
        abort(404)
    if '..' in file_name or file_name.startswith('/'):
        abort(404)
    path = "{0}/resources/{1}".format(game_name, file_name)
    return send_file(path)


@app.route('/<game_name>/style/<file_name>')
def get_style(game_name, file_name):
    if '..' in game_name or game_name.startswith('/'):
        abort(404)
    if '..' in file_name or file_name.startswith('/'):
        abort(404)
    path = "{0}/cards/{1}".format(game_name, file_name)
    return send_file(path)


@app.route('/<game_name>/')
def display(game_name):
    old_loader = app.jinja_env.loader
    app.jinja_env.loader = PackageLoader(game_name, 'cards')

    all_card_data = card_creator.get_card_data(game_name, data_files=None, card_names=None)
    columns = all_card_data[0].keys()
    cards = { True: [], False: [] }

    card_types = []
    for front in (True, False):
        for card_data in all_card_data:
            card = card_creator.build_card_object(card_data, game_name, index=0, front=front)
            if card.no_print:
                continue
            cards[front].append(get_renderable_card(game_name, card))
            card_types.append(card.card_type)

    front_pages = [] # groups of cards designed to fit on single pages
    back_pages = [] # groups of cards designed to fit on single pages
    # @TODO First group cards by their size
    #grouped_front_pages = group_cards_by_size(front_pages)
    print_cards.group_cards_by_page(cards[True], front_pages)
    print_cards.group_cards_by_page(cards[False], back_pages)

    combined_pages = []
    for i, page in enumerate(front_pages):
        combined_pages.append(front_pages[i])
        combined_pages.append(back_pages[i])

    styles = []
    for card_type in list(set(card_types)):
        styles.append(url_for('get_style', game_name=game_name, file_name='{0}.css'.format(card_type)))

    print_stylesheet = url_for('static', filename='styles/print.css')
    global_stylesheet = url_for('static', filename='styles/global_cards.css')
    default_stylesheet = url_for('static', filename='styles/default_cards.css')

    app.jinja_env.loader = old_loader
    return render_template('cards.html'.format(game_name), pages=combined_pages, styles=styles, style_global=global_stylesheet, style_default=default_stylesheet, style_print=print_stylesheet, columns=columns)


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


@app.route('/<game_name>/save', methods=['POST'])
def save(game_name):
    print "request:", request.method
    return 'test response'

@app.route('/single/')
@app.route('/single/<card_name>')
def single_card(card_name=None):
    # get parsed/processed info for all cards
    card = {
        'title': 'Magikarp',
    }
    return render_template('card.html', card=card)
    return "Card name: {0}".format(card_name)
    return 'Hello world!'


def debug(text):
    print text
    print ''
    return text


def format_body_text(text):
    text = text.strip()
    words = text.split(' ')
    new_text_list = [words[0].capitalize()] + words[1:]
    new_text = ' '.join(new_text_list)
    return new_text


def word_tokenize(text):
    import nltk
    nltk.download('punkt')
    sentences = nltk.sent_tokenize(text)
    words = nltk.word_tokenize(text)
    '''
    print "words:", words
    for sentence in sentences:
        nltk.word_tokenize(sentence)
    '''
    return words


def replace_items_with_tokens(text, item_list, template):
    chunks = text.split()
    for i, chunk in enumerate(chunks):
        for item in item_list:
            if item in chunk:
                chunks[i] = chunk.replace(item, template.format(item))
                break
    return ' '.join(chunks)


app.jinja_env.filters['debug'] = debug
app.jinja_env.filters['format_body_text'] = format_body_text
app.jinja_env.filters['word_tokenize'] = word_tokenize
app.jinja_env.filters['replace_items_with_tokens'] = replace_items_with_tokens

if __name__ == '__main__':
    app.debug = True
    app.run()
