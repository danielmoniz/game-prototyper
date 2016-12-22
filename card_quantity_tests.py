import unittest

import mock

from card_creator.player_numbers import get_num_players_required, format_num_players_required, get_max_quantity
from card_creator.card import Card

class TestPlayerNumbers(unittest.TestCase):

    def setUp(self):
        # self.card = FakeCard()
        # self.card = unittest.mock.MagicMock()
        self.card = mock.MagicMock()
        self.card.qty_1_players = None
        self.card.qty_2_players = None
        self.card.qty_3_players = None
        self.card.qty_4_players = None
        self.card.qty_5_players = None
        self.card.qty_6_players = None
        self.card.qty_7_players = None
        self.card.qty_8_players = None

    def teardown(self):
        # delete self.card
        pass

    def test_quantities_all_equal(self):
        self.card.qty_2_players = 1
        self.card.qty_3_players = 1
        self.card.qty_4_players = 1

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 2, False)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 0, True)

    def test_quantities_ascending_monotonically(self):
        self.card.qty_2_players = 1
        self.card.qty_3_players = 2
        self.card.qty_4_players = 3

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 2, False)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 3, False)

        result = self.get_result(num_copies=3)
        self.assert_min_players_and_exact(result, 4, True)

    def test_quantities_two_high_amounts(self):
        self.card.qty_2_players = 1
        self.card.qty_3_players = 3
        self.card.qty_4_players = 3

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 2, False)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 3, False)

        result = self.get_result(num_copies=3)
        self.assert_min_players_and_exact(result, 3, False)

    def test_quantities_two_low_amounts(self):
        self.card.qty_2_players = 1
        self.card.qty_3_players = 1
        self.card.qty_4_players = 3

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 2, False)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 4, True)

        result = self.get_result(num_copies=3)
        self.assert_min_players_and_exact(result, 4, True)

    def test_quantities_single_player_only(self):
        self.card.qty_1_players = 2

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 1, True)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 1, True)

    def test_quantities_three_player_only(self):
        self.card.qty_3_players = 2

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 3, True)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 3, True)

    def test_quantities_all_players(self):
        self.card.qty_1_players = 1
        self.card.qty_2_players = 2
        self.card.qty_3_players = 3
        self.card.qty_4_players = 4
        self.card.qty_5_players = 5
        self.card.qty_6_players = 6
        self.card.qty_7_players = 7
        self.card.qty_8_players = 8

        result = self.get_result(num_copies=1)
        self.assert_min_players_and_exact(result, 1, False)

        result = self.get_result(num_copies=2)
        self.assert_min_players_and_exact(result, 2, False)

        result = self.get_result(num_copies=3)
        self.assert_min_players_and_exact(result, 3, False)

        result = self.get_result(num_copies=4)
        self.assert_min_players_and_exact(result, 4, False)

        result = self.get_result(num_copies=5)
        self.assert_min_players_and_exact(result, 5, False)

        result = self.get_result(num_copies=6)
        self.assert_min_players_and_exact(result, 6, False)

        result = self.get_result(num_copies=7)
        self.assert_min_players_and_exact(result, 7, False)

        result = self.get_result(num_copies=8)
        self.assert_min_players_and_exact(result, 8, True)

    def get_result(self, num_copies=None):
        return get_num_players_required(self.card, num_copies)

    def assert_min_players_and_exact(self, result, min_players, exact):
        self.assertEqual(result[0], min_players)
        self.assertEqual(result[1], exact)


class TestPlayerNumberOutput(unittest.TestCase):

    def test_bad_inputs(self):
        result = format_num_players_required(-5, False)
        self.assertEqual('', result)

        result = format_num_players_required(-5, True)
        self.assertEqual('', result)

    def test_exact_inputs(self):
        result = format_num_players_required(0, True)
        self.assertEqual('', result)

        result = format_num_players_required(1, True)
        self.assertEqual('1', result)

        result = format_num_players_required(63, True)
        self.assertEqual('63', result)

    def test_inexact_inputs(self):
        result = format_num_players_required(0, False)
        self.assertEqual('', result)

        result = format_num_players_required(1, False)
        self.assertEqual('1+', result)

        result = format_num_players_required(4, False)
        self.assertEqual('4+', result)


class TestMaxQuantities(unittest.TestCase):

    def setUp(self):
        self.quantities = (
            (1, 1),
            (2, 3),
            (3, 3),
            (4, 5),
        )

    def test_get_max_quantity(self):
        result = get_max_quantity(self.quantities)
        self.assertEqual(result, 5)


if __name__ == '__main__':
    unittest.main()
