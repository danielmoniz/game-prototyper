from flask import Flask, url_for, request, send_from_directory
from flask import render_template

import card_creator
import print_cards

app = Flask(__name__)

@app.route('/<game_name>/')
def display(game_name):
    all_card_data = card_creator.get_card_data(game_name, data_files=None, card_names=None)
    columns = all_card_data[0].keys()
    cards = []
    for card_data in all_card_data:
        card = card_creator.build_card_object(card_data, game_name, index=0, front=True)
        cards.append(card)

    pages = [] # groups of cards designed to fit on single pages
    # @TODO First group cards by their size
    #grouped_fronts = group_cards_by_size(fronts)
    print_cards.group_cards_by_page(cards, pages)
    from reportlab.lib.units import inch, cm, mm
    print "inch:", inch

    stylesheet = url_for('static', filename='{0}/main.css'.format(game_name))
    print_stylesheet = url_for('static', filename='styles/print.css')
    return render_template('{0}/cards.html'.format(game_name), pages=pages, cards=cards, style=stylesheet, style_print=print_stylesheet, columns=columns)


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
