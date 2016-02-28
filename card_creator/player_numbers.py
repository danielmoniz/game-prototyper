# -*- coding: utf-8 -*-


def update(card, count, *args, **kwargs):
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
    Also determine whether the card requires an exact player count or simply a
    minimum.
    """
    quantities = (
        (2, getattr(card, 'qty_2_players', None)),
        (3, getattr(card, 'qty_3_players', None)),
        (4, getattr(card, 'qty_4_players', None)),
        (5, getattr(card, 'qty_5_players', None)),
        (6, getattr(card, 'qty_6_players', None)))
    min_players = 0
    exact = True

    for players, quantity in quantities[::-1]:
        quantity = quantity or 0
        if num_copies <= quantity:
            if min_players != 0:
                exact = False
            min_players = players

    return min_players, exact


def format_num_players_required(players_required, exact):
    if players_required > 2 or exact:
        if players_required == 0:
            return ''
        num_players = "{0}".format(players_required)
        if not exact:
            num_players += "+"

        return num_players
    return ''

