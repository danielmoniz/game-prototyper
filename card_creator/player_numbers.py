# -*- coding: utf-8 -*-


def update(card, count, *args, **kwargs):
    # if asking to print more cards than allowed...
    if get_max_quantity(get_quantities(card)) < count:
        card.skip = True
        return False

    players_required, exact = get_num_players_required(card, count)
    if kwargs['players'] and players_required > kwargs['players']:
        card.skip = True
    if kwargs['skip_players'] and players_required <= kwargs['skip_players']:
        card.skip = True

    text = format_num_players_required(players_required, exact)
    card.players_required = text


def get_num_players_required(card, num_copies):
    """
    Determine the minimum number of required players for a card.
    In general, assumes more of a card is needed for more players. Cannot
    have a card that requires a higher quantity for fewer players.
    Assumes num_copies is not higher than the highest specified quantity.
        Will get extra cards if passed a bad value of num_copies!
    Also determine whether the card requires an exact player count or simply a
    minimum.
    Ie. requires an exact amount for the highest player number specified.
        Eg. 2 players: 4 copies
            3 players: 6 copies
            If num_copies <= 4, should say be for exactly 2 players.
            If num_copies is 5 or 6, should be for at least 3 players.
            If num_copies > 6, bad input!
    """
    quantities = get_quantities(card)

    min_players = 0
    exact = True

    for num_players, quantity in quantities[::-1]:
        quantity = quantity or 0
        if num_copies <= quantity:
            if min_players != 0:
                exact = False
            min_players = num_players

    return min_players, exact


def format_num_players_required(players_required, exact):
    '''Assumes integer input. Returns a string like '4' or '3+'.
    Returns '' if no minimum (ie. players_required == 0).
    '''
    if players_required <= 0:
        return ''
    num_players = "{0}".format(players_required)
    if not exact:
        num_players += "+"
    return num_players


def get_max_quantity(quantities):
    return max([y for x, y in quantities])


def get_quantities(card):
    return (
        (1, getattr(card, 'qty_1_players', None)),
        (2, getattr(card, 'qty_2_players', None)),
        (3, getattr(card, 'qty_3_players', None)),
        (4, getattr(card, 'qty_4_players', None)),
        (5, getattr(card, 'qty_5_players', None)),
        (6, getattr(card, 'qty_6_players', None)),
        (7, getattr(card, 'qty_7_players', None)),
        (8, getattr(card, 'qty_8_players', None)),
    )
