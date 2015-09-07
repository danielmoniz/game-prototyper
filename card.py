import logging

import resource

class Card(object):

    def __init__(self, data, game_name, index=0, front=True):
        self.card_id = index
        self.game_name = game_name

        self.card_type = self.get_card_type(data)

        self.only_print = False
        self.no_print = False
        if 'only_print' in data and data['only_print']:
            if not isinstance(data['only_print'], basestring):
                if data['only_print'][0]:
                    self.only_print = True
            else:
                self.only_print = True

        if 'no_print' in data and data['no_print']:
            self.no_print = True

        self.front = front
        self.front_or_back = 'front' if self.front else 'back'

        # store all data just in case
        self.data = data

        for key, value in data.iteritems():
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
            if hasattr(self, key):# and getattr(self, key):
                logging.debug("Card property '{0}' already set! Pick another name.".format(key))
                continue
            setattr(self, key, value)

    def __getitem__(self, attr):
        # A quick hack to allow for dynamic attribute retrieval in templates
        try:
            return getattr(self, attr)
        except AttributeError:
            return None


    def set_resources(self):
        with resource.open_file('goods.txt') as f:
            lines = f.readlines()
            resources = [x.strip() for x in lines if bool(x.strip())]
            self.resources = resources

    def set_icons(self):
        with resource.open_file('other_icons.txt') as f:
            lines = f.readlines()
            icons = [x.strip() for x in lines if bool(x.strip())]
            self.icons = icons

    def get_card_type(self, data):
        card_type = 'main'
        if 'card_type' in data and data['card_type'].strip():
            card_type = data['card_type'].strip()
        return card_type

