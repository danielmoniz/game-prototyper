from flask import Flask, url_for, request, send_from_directory, send_file
from flask import render_template
import jinja2
from jinja2 import Environment, PackageLoader

from card_creator import data
from card_creator import card as card_helper

app = Flask(__name__)
#app.jinja_env.add_extension('utils.jinja2htmlcompress.HTMLCompress')


@app.route('/<game_name>/')
def display(game_name):
    data_file = request.args.get('data_file', None)
    data_files = [data_file]
    if data_file is None:
        data_files = None

    use_backs = request.args.get('backs', 'true')
    use_backs = use_backs.lower() == 'true'

    search = request.args.get('search', '')
    card_type = request.args.get('card_type', '')

    duplicates = request.args.get('duplicates', 'true')
    duplicates = duplicates.lower() == 'true'

    old_loader = app.jinja_env.loader
    app.jinja_env.loader = PackageLoader(game_name, 'cards')

    all_card_data = data.get_card_data(game_name, data_files=data_files, card_names=None)
    columns = all_card_data[0].keys()
    cards = { True: [], False: [] }

    card_types = []
    sides = (True, False)
    if not use_backs: sides = (True,)
    for front in sides:
        for card_data in all_card_data:
            card = card_helper.Card(card_data, game_name, index=0, front=front)
            card_types.append(card.card_type)

            quantity = range(card.quantity)
            if not duplicates: quantity = range(1)
            for i in quantity:
                if (not card.card_type.startswith(card_type)
                    or not card.name.lower().startswith(search.lower())
                    or card.no_print):
                    continue
                card = card_helper.Card(card_data, game_name, index=i, front=front)
                card.process(card, i + 1)
                cards[front].append(get_renderable_card(game_name, card))

    styles = []
    for card_type in list(set(card_types)):
        styles.append(url_for('get_style', game_name=game_name, file_name='{0}.css'.format(card_type)))

    print_stylesheet = url_for('static', filename='styles/print.css')
    print_adjust_stylesheet = url_for('get_style', game_name=game_name, file_name='print_adjust.css')
    global_stylesheet = url_for('static', filename='styles/global_cards.css')
    default_stylesheet = url_for('static', filename='styles/default_cards.css')

    app.jinja_env.loader = old_loader
    resources = card_helper.Card.get_text_config('goods.txt')
    other_icons = card_helper.Card.get_text_config('other_icons.txt')
    icon_styles = get_icon_styles(game_name, resources, other_icons)

    return render_template('cards.html', fronts=cards[True], backs=cards[False], styles=styles, icon_styles=icon_styles, style_global=global_stylesheet, style_default=default_stylesheet, style_print=print_stylesheet, style_print_adjust=print_adjust_stylesheet, columns=columns)


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


def debug(text, print_text=True):
    print text
    print ''
    if print_text:
        return text
    return ''


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
    print "text:", text
    chunks = text.split()
    for i, chunk in enumerate(chunks):
        for item_block in item_list:
            for item in item_block.split()[::-1]:
                if item in chunk:
                    # ignore items with a backslash prepended and replace others
                    # NOTE: this code cannot handle (say) 'graingrainsgrain'
                    # because the loop will break before dealing with both 'grain'
                    # and 'grains'
                    chunk = chunk.replace('\\' + item, '@#$%^')
                    chunk = chunk.replace(item, template.format(item))
                    chunk = chunk.replace('@#$%^', item)
                    chunks[i] = chunk
                    break

    return ' '.join(chunks)


app.jinja_env.filters['debug'] = debug
app.jinja_env.filters['format_body_text'] = format_body_text
app.jinja_env.filters['word_tokenize'] = word_tokenize
app.jinja_env.filters['replace_items_with_tokens'] = replace_items_with_tokens

if __name__ == '__main__':
    app.debug = True
    app.run()
