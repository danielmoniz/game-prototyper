import logging
import sys
import imp

import resource

class Card(object):

    def __init__(self, data, game_name, index=0, front=True):
        self.skip = False

        self.icons = self.get_text_config('other_icons.txt')
        self.resources = self.get_text_config('goods.txt')

        self.card_id = index
        self.game_name = game_name

        self.card_type = self.get_card_type(data)

        self.set_print_data(data)

        self.front = front
        self.front_or_back = 'front' if self.front else 'back'

        # store all data just in case
        self.data = data
        self.set_generic_data(data)

        if not hasattr(self, 'quantity') or self.quantity == '':
            self.quantity = 1

        self.set_has_costs()

        '''
        # set project-specific custom process method
        file_name = "process.py"
        file_path = "./{0}/{1}".format(game_name, file_name)

        def process(self, *args, **kwargs): pass
        self.process = process
        try:
            process_module = imp.load_source(file_name, file_path)
            self.process = process_module.process
        except IOError as e:
            pass
        '''

    def set_generic_data(self, data):
        for key, value in data.iteritems():
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
            if hasattr(self, key):# and getattr(self, key):
                logging.debug("Card property '{0}' already set! Pick another name.".format(key))
                continue
            setattr(self, key, value)

    def set_print_data(self, data):
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

    def set_has_costs(self):
        self.has_costs = False
        for resource_data in self.resources:
            resource = resource_data.split()[0]
            if hasattr(self, resource) and self[resource]:
                self.has_costs = True


    def __getitem__(self, attr):
        # A quick hack to allow for dynamic attribute retrieval in templates
        try:
            return getattr(self, attr)
        except AttributeError:
            return None

    @classmethod
    def get_text_config(self, file_name):
        with resource.open_file(file_name) as f:
            lines = f.readlines()
            config = [x.strip() for x in lines if bool(x.strip())]
            return config
            self.icons = icons

    def get_card_type(self, data):
        card_type = 'main'
        if 'card_type' in data and data['card_type'].strip():
            card_type = data['card_type'].strip()
        return card_type

