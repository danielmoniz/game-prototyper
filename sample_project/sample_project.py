# -*- coding: utf-8 -*-
import imp
import logging

import resource


def process(card, count, *args, **kwargs):
    players_required, exact = get_num_players_required(card, count)

    text = format_num_players_required(players_required, exact)
    card.players_required = text


def get_num_players_required(card, num_copies):
    """
    Determine the minimum number of required players for a card.
    Also determine whether the card requires an exact player count or simply a
    minimum.
    """
    quantities = ((2, card.qty_2_players), (3, card.qty_3_players), (4, card.qty_4_players))
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

        players_required_text = "{0} players".format(num_players)
        return players_required_text
    return ''

