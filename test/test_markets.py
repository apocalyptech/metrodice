#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from metrodice import cards, markets, gamelib

class MarketBaseTests(unittest.TestCase):
    """
    Tests for our "base" market type.
    """

    def setUp(self):
        """
        Our market tests will require a Game object
        """
        self.player = gamelib.Player(name='Player')
        self.game = gamelib.Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                markets.MarketBase)

    def test_market_require_one_of_expansion_or_deck(self):
        """
        A Market initialization requires one of either a deck of
        cards or an expansion object
        """

        with self.assertRaises(Exception):
            market = markets.MarketBase(self.game)

    def test_market_repr_is_name(self):
        """
        repr() of a market should be the name
        """
        market = markets.MarketBase(self.game, name='Test Market', deck=[])
        self.assertEqual(repr(market), 'Test Market')

    def test_add_to_available_no_previous(self):
        """
        Test to ensure that adding a new card to the market adds it in to
        the available list.
        """
        wheat = cards.CardWheat(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[])
        market._add_to_available(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        self.assertEqual(available, {wheat: 1})

    def test_add_to_available_one_previous(self):
        """
        Test to ensure that adding a new card to the market adds it in to
        the available list.
        """
        wheat1 = cards.CardWheat(self.game)
        wheat2 = cards.CardWheat(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[])
        market._add_to_available(wheat1)
        market._add_to_available(wheat2)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, count) in available.items():
            self.assertEqual(type(card), type(wheat1))
            self.assertEqual(count, 2)

    def test_add_two_different_cards(self):
        """
        Test to ensure that adding two cards to the market adds them in to
        the available list.
        """
        wheat = cards.CardWheat(self.game)
        bakery = cards.CardBakery(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[])
        market._add_to_available(wheat)
        market._add_to_available(bakery)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        available_cards = sorted(available.keys())
        self.assertEqual(available_cards[0], wheat)
        self.assertEqual(available_cards[1], bakery)
        self.assertEqual(available[wheat], 1)
        self.assertEqual(available[bakery], 1)
