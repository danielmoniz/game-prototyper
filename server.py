from flask import Flask, url_for, request, send_from_directory
from flask import render_template
import jinja2

import card_creator
import print_cards

app = Flask(__name__)

@app.route('/<game_name>/')
def display(game_name):
    all_card_data = card_creator.get_card_data(game_name, data_files=None, card_names=None)
    columns = all_card_data[0].keys()
    cards = { True: [], False: [] }

    card_types = []
    for front in (True, False):
        for card_data in all_card_data:
            card = card_creator.build_card_object(card_data, game_name, index=0, front=front)
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
        styles.append(url_for('static', filename='{0}/{1}.css'.format(game_name, card_type)))
    print "styles:", styles
    #stylesheet = url_for('static', filename='{0}/main.css'.format(game_name))
    print_stylesheet = url_for('static', filename='styles/print.css')
    global_stylesheet = url_for('static', filename='styles/global_cards.css')
    default_stylesheet = url_for('static', filename='styles/default_cards.css')
    return render_template('{0}/cards.html'.format(game_name), pages=combined_pages, styles=styles, style_global=global_stylesheet, style_default=default_stylesheet, style_print=print_stylesheet, columns=columns)


def get_renderable_card(game_name, card):
    try:
        print '{0}/{1}_{2}.html'.format(game_name, card.card_type, card.front_or_back)
        card.html = render_template('{0}/{1}_{2}.html'.format(game_name, card.card_type, card.front_or_back), card=card)
    except jinja2.exceptions.TemplateNotFound:
        pass

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

app.jinja_env.filters['debug'] = debug

if __name__ == '__main__':
    app.debug = True
    app.run()
