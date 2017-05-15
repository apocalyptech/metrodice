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

    def test_populate_initial_with_empty_passed_in_deck(self):
        """
        Testing initial population of the market when we pass in an
        empty deck of cards.
        """
        market = markets.MarketBase(self.game, name='Test Market', deck=[])
        self.assertEqual(len(market.cards_available()), 0)

    def test_populate_initial_with_passed_in_deck(self):
        """
        Testing initial population of the market when we pass in a
        deck of cards.
        """
        wheat = cards.CardWheat(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[wheat])
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, count) in available.items():
            self.assertEqual(type(card), type(wheat))
            self.assertEqual(count, 1)

    def test_populate_initial_with_passed_in_deck_two_different(self):
        """
        Testing initial population of the market when we pass in a
        deck of cards.
        """
        wheat = cards.CardWheat(self.game)
        bakery = cards.CardBakery(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[wheat, bakery])
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        available_cards = sorted(available.keys())
        self.assertEqual(type(available_cards[0]), cards.CardWheat)
        self.assertEqual(type(available_cards[1]), cards.CardBakery)
        self.assertEqual(available[available_cards[0]], 1)
        self.assertEqual(available[available_cards[1]], 1)

    def test_passed_in_deck_does_not_get_altered(self):
        """
        When passing in a list of cards as a deck, make sure that we only store a copy
        of the list, so changes in the class can't affect the passed-in var, and vice-versa
        """
        wheat = cards.CardWheat(self.game)
        bakery = cards.CardBakery(self.game)
        cafe = cards.CardCafe(self.game)
        deck = [wheat, bakery, cafe]
        market = markets.MarketBase(self.game, name='Test Market', deck=deck)
        self.assertEqual(deck, [wheat, bakery, cafe])
        deck.append(cards.CardForest(self.game))
        self.assertEqual(market.deck, [wheat, bakery, cafe])

    def test_populate_initial_with_passed_in_expansion(self):
        """
        Testing initial population of the market when we pass in an
        Expansion object
        """
        expansion = cards.Expansion(name='Test Expansion',
            deck_regular=[(1, cards.CardWheat)],
            deck_major=[],
            landmarks=[])
        market = markets.MarketBase(self.game, name='Test Market', expansion=expansion)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, count) in available.items():
            self.assertEqual(type(card), cards.CardWheat)
            self.assertEqual(count, 1)

    def test_take_card_not_in_deck(self):
        """
        Test taking a card that's not actually present.  An Exception should be raised
        """
        market = markets.MarketBase(self.game, name='Test Market', deck=[cards.CardWheat(self.game)])
        with self.assertRaises(Exception) as cm:
            market.take_card(cards.CardBakery(self.game))

    def test_take_last_card_in_market(self):
        """
        Test taking the last card from a Market.
        """
        wheat = cards.CardWheat(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[wheat])
        got_wheat = market.take_card(wheat)
        self.assertEqual(got_wheat, wheat)
        self.assertEqual(len(market.cards_available()), 0)

    def test_take_card_from_market(self):
        """
        Test taking a card from a Market.
        """
        wheat1 = cards.CardWheat(self.game)
        wheat2 = cards.CardWheat(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[wheat1, wheat2])
        got_wheat = market.take_card(wheat1)
        self.assertEqual(type(got_wheat), cards.CardWheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, count) in available.items():
            self.assertEqual(type(card), cards.CardWheat)
            self.assertEqual(count, 1)

    def test_take_card_from_market_2(self):
        """
        Second test taking a card from a Market.
        """
        wheat = cards.CardWheat(self.game)
        bakery = cards.CardBakery(self.game)
        market = markets.MarketBase(self.game, name='Test Market', deck=[wheat, bakery])
        got_wheat = market.take_card(wheat)
        self.assertEqual(type(got_wheat), cards.CardWheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, count) in available.items():
            self.assertEqual(type(card), cards.CardBakery)
            self.assertEqual(count, 1)

class MarketHarborTests(unittest.TestCase):
    """
    Tests for the "Harbor" style market.  Unlike the base market class, the
    functionality of this one involves randomizing the deck, which would
    make testing some aspects of functionality difficult.  To that end, some of
    these tests will rely on knowing that the internal randomized deck is stored
    in the 'deck' var, and that values are pop()'d off the top, and so we'll
    alter that variable to suit.
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
            market = markets.MarketHarbor(self.game)

    def test_market_initial_population_expansion(self):
        """
        Initial market population with an Expansion should create ten piles
        """
        market = markets.MarketHarbor(self.game, expansion=cards.expansion_base)
        self.assertEqual(len(market.cards_available()), 10)

    def test_market_initial_population_deck(self):
        """
        Initial market population should create ten piles
        """
        deck = [
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            cards.CardCafe(self.game),
            cards.CardConvenienceStore(self.game),
            cards.CardForest(self.game),
            cards.CardStadium(self.game),
            cards.CardTVStation(self.game),
            cards.CardBusinessCenter(self.game),
            cards.CardCheeseFactory(self.game),
            cards.CardMine(self.game),
            ]
        market = markets.MarketHarbor(self.game, deck=deck)
        self.assertEqual(len(market.cards_available()), 10)

    def test_market_initial_population_fewer_piles(self):
        """
        If we pass in pile_limit, don't use the default of ten.
        """
        deck = [
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            ]
        market = markets.MarketHarbor(self.game, deck=deck, pile_limit=2)
        self.assertEqual(len(market.cards_available()), 2)

    def test_market_initial_population_no_cards(self):
        """
        Test to make sure that passing in an empty deck just results in an empty
        market.
        """
        market = markets.MarketHarbor(self.game, deck=[], pile_limit=2)
        self.assertEqual(len(market.cards_available()), 0)

    def test_take_last_of_pile_when_deck_exhausted(self):
        """
        Test what happens when the last card is taken off a pile, and there are
        no other cards to replace it.
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketHarbor(self.game, deck=deck, pile_limit=2)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})
        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        self.assertEqual(available, {ranch: 1})

    def test_market_replace_with_new_pile(self):
        """
        After taking a card from the market, if it's the last card in the pile,
        a new one should be created.
        """
        deck = [
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            ]
        market = markets.MarketHarbor(self.game, deck=deck, pile_limit=2)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        initial_cardlist = list(sorted(available.keys()))
        for card in initial_cardlist:
            deck.remove(card)
        got_card = market.take_card(initial_cardlist[0])
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        initial_cardlist.remove(got_card)
        in_market = sorted([deck[0], initial_cardlist[0]])
        new_cardlist = list(sorted(available.keys()))
        self.assertEqual(new_cardlist, in_market)

    def test_passed_in_deck_does_not_get_altered(self):
        """
        When passing in a list of cards as a deck, make sure that we only store a copy
        of the list, so changes in the class can't affect the passed-in var, and vice-versa
        """
        wheat = cards.CardWheat(self.game)
        bakery = cards.CardBakery(self.game)
        cafe = cards.CardCafe(self.game)
        deck = [wheat, bakery, cafe]
        market = markets.MarketHarbor(self.game, deck=deck)
        self.assertEqual(deck, [wheat, bakery, cafe])
        deck.append(cards.CardForest(self.game))
        self.assertEqual(market.deck, [])

    def test_take_last_of_pile_can_add_more_to_other_pile(self):
        """
        Exhausting a pile may end up adding more to existing piles before 
        creating a new pile
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketHarbor(self.game, deck=deck, pile_limit=2)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})

        # here's where we're injecting into a theoretically-private var
        # of the market, to control output a bit.
        ranch2 = cards.CardRanch(self.game)
        bakery = cards.CardBakery(self.game)
        market.deck = [bakery, ranch2]

        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {bakery: 1, ranch: 2})

    def test_take_last_of_pile_can_add_more_to_other_pile_and_leave_pile_empty(self):
        """
        Exhausting a pile may end up adding more to existing piles before
        running out of cards.
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketHarbor(self.game, deck=deck, pile_limit=2)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})

        # here's where we're injecting into a theoretically-private var
        # of the market, to control output a bit.
        ranch2 = cards.CardRanch(self.game)
        market.deck = [ranch2]

        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        self.assertEqual(available, {ranch: 2})

    def test_take_last_of_pile_might_not_add_more_to_other_pile(self):
        """
        Exhausting a pile may not end up adding more to other existing piles,
        even if a card would be coming up later in the deck.
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketHarbor(self.game, deck=deck, pile_limit=2)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})

        # here's where we're injecting into a theoretically-private var
        # of the market, to control output a bit.
        ranch2 = cards.CardRanch(self.game)
        bakery = cards.CardBakery(self.game)
        market.deck = [ranch2, bakery]

        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {bakery: 1, ranch: 1})

    def test_take_card_not_in_market(self):
        """
        Test taking a card that's not actually present.  An Exception should be raised
        """
        market = markets.MarketHarbor(self.game, deck=[cards.CardWheat(self.game)])
        with self.assertRaises(Exception) as cm:
            market.take_card(cards.CardBakery(self.game))

class MarketBrightLightsTests(unittest.TestCase):
    """
    Tests for the "Bright Lights" style market.  As with the Harbor tests,
    some of these will rely on some implementation details of the market itself.
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
            market = markets.MarketBrightLights(self.game)

    def test_market_initial_population_expansion(self):
        """
        Initial market population with an Expansion should create twelve piles
        """
        market = markets.MarketBrightLights(self.game, expansion=cards.expansion_base)
        self.assertEqual(len(market.cards_available()), 12)

    def test_market_initial_population_deck(self):
        """
        Initial market population should create ten piles
        """
        deck = [
            # 1-6 Regular
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            cards.CardCafe(self.game),
            cards.CardConvenienceStore(self.game),
            cards.CardForest(self.game),
            
            # Major Establishments
            cards.CardStadium(self.game),
            cards.CardTVStation(self.game),
            cards.CardBusinessCenter(self.game),

            # 7+ Regular
            cards.CardCheeseFactory(self.game),
            cards.CardMine(self.game),
            cards.CardMackerelBoat(self.game),
            cards.CardTunaBoat(self.game),
            cards.CardAppleOrchard(self.game),
            cards.CardFruitAndVeg(self.game),
            ]
        market = markets.MarketBrightLights(self.game, deck=deck)
        self.assertEqual(len(market.cards_available()), 12)
        self.assertEqual(len(market.stock_low.cards_available()), 5)
        self.assertEqual(len(market.stock_major.cards_available()), 2)
        self.assertEqual(len(market.stock_high.cards_available()), 5)
        self.assertEqual(len(market.stock_low.deck), 1)
        self.assertEqual(len(market.stock_major.deck), 1)
        self.assertEqual(len(market.stock_high.deck), 1)

    def test_market_initial_population_no_cards(self):
        """
        Test to make sure that passing in an empty deck just results in an empty
        market.
        """
        market = markets.MarketBrightLights(self.game, deck=[])
        self.assertEqual(len(market.cards_available()), 0)

    def test_take_last_of_pile_when_deck_exhausted(self):
        """
        Test what happens when the last card is taken off a pile, and there are
        no other cards to replace it.
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketBrightLights(self.game, deck=deck)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})
        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        self.assertEqual(available, {ranch: 1})

    def test_market_replace_with_new_pile(self):
        """
        After taking a card from the market, if it's the last card in the pile,
        a new one should be created.
        """
        deck = [
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            cards.CardCafe(self.game),
            cards.CardConvenienceStore(self.game),
            cards.CardForest(self.game),
            ]
        market = markets.MarketBrightLights(self.game, deck=deck)
        available = market.cards_available()
        self.assertEqual(len(available), 5)
        got_card = market.take_card(list(available.keys())[0])
        available = market.cards_available()
        self.assertEqual(len(available), 5)

    def test_passed_in_deck_does_not_get_altered(self):
        """
        When passing in a list of cards as a deck, make sure that we only store a copy
        of the list, so changes in the class can't affect the passed-in var, and vice-versa.
        """
        wheat = cards.CardWheat(self.game)
        bakery = cards.CardBakery(self.game)
        cafe = cards.CardCafe(self.game)
        deck = [wheat, bakery, cafe]
        market = markets.MarketBrightLights(self.game, deck=deck)
        self.assertEqual(deck, [wheat, bakery, cafe])
        deck.append(cards.CardForest(self.game))
        self.assertEqual(market.deck, [wheat, bakery, cafe])

    def test_take_last_of_pile_can_add_more_to_other_pile(self):
        """
        Exhausting a pile may end up adding more to existing piles before 
        creating a new pile
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketBrightLights(self.game, deck=deck)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})

        # here's where we're injecting into a theoretically-private var
        # of the market, to control output a bit.
        ranch2 = cards.CardRanch(self.game)
        bakery = cards.CardBakery(self.game)
        market.stock_low.deck = [bakery, ranch2]

        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {bakery: 1, ranch: 2})

    def test_take_last_of_pile_can_add_more_to_other_pile_and_leave_pile_empty(self):
        """
        Exhausting a pile may end up adding more to existing piles before
        running out of cards.
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        deck = [wheat, ranch]
        market = markets.MarketBrightLights(self.game, deck=deck)
        available = market.cards_available()
        self.assertEqual(len(available), 2)
        self.assertEqual(available, {wheat: 1, ranch: 1})

        # here's where we're injecting into a theoretically-private var
        # of the market, to control output a bit.
        ranch2 = cards.CardRanch(self.game)
        market.stock_low.deck = [ranch2]

        got_card = market.take_card(wheat)
        available = market.cards_available()
        self.assertEqual(len(available), 1)
        self.assertEqual(available, {ranch: 2})

    def test_take_last_of_pile_might_not_add_more_to_other_pile(self):
        """
        Exhausting a pile may not end up adding more to other existing piles,
        even if a card would be coming up later in the deck.
        """
        wheat = cards.CardWheat(self.game)
        ranch = cards.CardRanch(self.game)
        cafe = cards.CardCafe(self.game)
        forest = cards.CardForest(self.game)
        store = cards.CardConvenienceStore(self.game)
        deck = [wheat, ranch, cafe, forest, store]
        market = markets.MarketBrightLights(self.game, deck=deck)
        old_available = market.cards_available()
        self.assertEqual(len(old_available), 5)
        self.assertEqual(old_available, {wheat: 1, ranch: 1, cafe: 1, forest: 1, store: 1})

        # here's where we're injecting into a theoretically-private var
        # of the market, to control output a bit.
        ranch2 = cards.CardRanch(self.game)
        bakery = cards.CardBakery(self.game)
        market.stock_low.deck = [ranch2, bakery]

        got_card = market.take_card(wheat)
        del old_available[got_card]
        old_available[bakery] = 1
        new_available = market.cards_available()
        self.assertEqual(len(new_available), 5)
        self.assertEqual(new_available, old_available)

    def test_take_card_not_in_market(self):
        """
        Test taking a card that's not actually present.  An Exception should be raised
        """
        market = markets.MarketBrightLights(self.game, deck=[cards.CardWheat(self.game)])
        with self.assertRaises(Exception) as cm:
            market.take_card(cards.CardBakery(self.game))

    def test_deplete_low_cards(self):
        """
        If the Low Card sub-market is depleted when a card is taken, make sure
        that cards from the other markets don't get pulled in.
        """
        card_to_take = cards.CardWheat(self.game)
        deck = [
            # 1-6 Regular
            card_to_take,
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            cards.CardCafe(self.game),
            cards.CardConvenienceStore(self.game),
            
            # Major Establishments
            cards.CardStadium(self.game),
            cards.CardTVStation(self.game),
            cards.CardBusinessCenter(self.game),

            # 7+ Regular
            cards.CardCheeseFactory(self.game),
            cards.CardMine(self.game),
            cards.CardMackerelBoat(self.game),
            cards.CardTunaBoat(self.game),
            cards.CardAppleOrchard(self.game),
            cards.CardFruitAndVeg(self.game),
            ]
        market = markets.MarketBrightLights(self.game, deck=deck)
        self.assertEqual(len(market.cards_available()), 12)
        self.assertEqual(len(market.stock_low.cards_available()), 5)
        self.assertEqual(len(market.stock_major.cards_available()), 2)
        self.assertEqual(len(market.stock_high.cards_available()), 5)
        self.assertEqual(len(market.stock_low.deck), 0)
        self.assertEqual(len(market.stock_major.deck), 1)
        self.assertEqual(len(market.stock_high.deck), 1)
        card = market.take_card(card_to_take)
        self.assertEqual(len(market.cards_available()), 11)
        self.assertEqual(len(market.stock_low.cards_available()), 4)
        self.assertEqual(len(market.stock_major.cards_available()), 2)
        self.assertEqual(len(market.stock_high.cards_available()), 5)
        self.assertEqual(len(market.stock_low.deck), 0)
        self.assertEqual(len(market.stock_major.deck), 1)
        self.assertEqual(len(market.stock_high.deck), 1)

    def test_deplete_major_cards(self):
        """
        If the Major Est. market is depleted when a card is taken, make sure
        that cards from the other markets don't get pulled in.
        """
        card_to_take = cards.CardStadium(self.game)
        deck = [
            # 1-6 Regular
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            cards.CardCafe(self.game),
            cards.CardConvenienceStore(self.game),
            cards.CardForest(self.game),
            
            # Major Establishments
            card_to_take,
            cards.CardTVStation(self.game),

            # 7+ Regular
            cards.CardCheeseFactory(self.game),
            cards.CardMine(self.game),
            cards.CardMackerelBoat(self.game),
            cards.CardTunaBoat(self.game),
            cards.CardAppleOrchard(self.game),
            cards.CardFruitAndVeg(self.game),
            ]
        market = markets.MarketBrightLights(self.game, deck=deck)
        self.assertEqual(len(market.cards_available()), 12)
        self.assertEqual(len(market.stock_low.cards_available()), 5)
        self.assertEqual(len(market.stock_major.cards_available()), 2)
        self.assertEqual(len(market.stock_high.cards_available()), 5)
        self.assertEqual(len(market.stock_low.deck), 1)
        self.assertEqual(len(market.stock_major.deck), 0)
        self.assertEqual(len(market.stock_high.deck), 1)
        card = market.take_card(card_to_take)
        self.assertEqual(len(market.cards_available()), 11)
        self.assertEqual(len(market.stock_low.cards_available()), 5)
        self.assertEqual(len(market.stock_major.cards_available()), 1)
        self.assertEqual(len(market.stock_high.cards_available()), 5)
        self.assertEqual(len(market.stock_low.deck), 1)
        self.assertEqual(len(market.stock_major.deck), 0)
        self.assertEqual(len(market.stock_high.deck), 1)

    def test_deplete_high_cards(self):
        """
        If the High Card sub-market is depleted when a card is taken, make sure
        that cards from the other markets don't get pulled in.
        """
        card_to_take = cards.CardMine(self.game)
        deck = [
            # 1-6 Regular
            cards.CardWheat(self.game),
            cards.CardRanch(self.game),
            cards.CardBakery(self.game),
            cards.CardCafe(self.game),
            cards.CardConvenienceStore(self.game),
            cards.CardForest(self.game),
            
            # Major Establishments
            cards.CardStadium(self.game),
            cards.CardTVStation(self.game),
            cards.CardBusinessCenter(self.game),

            # 7+ Regular
            cards.CardCheeseFactory(self.game),
            card_to_take,
            cards.CardMackerelBoat(self.game),
            cards.CardTunaBoat(self.game),
            cards.CardAppleOrchard(self.game),
            ]
        market = markets.MarketBrightLights(self.game, deck=deck)
        self.assertEqual(len(market.cards_available()), 12)
        self.assertEqual(len(market.stock_low.cards_available()), 5)
        self.assertEqual(len(market.stock_major.cards_available()), 2)
        self.assertEqual(len(market.stock_high.cards_available()), 5)
        self.assertEqual(len(market.stock_low.deck), 1)
        self.assertEqual(len(market.stock_major.deck), 1)
        self.assertEqual(len(market.stock_high.deck), 0)
        card = market.take_card(card_to_take)
        self.assertEqual(len(market.cards_available()), 11)
        self.assertEqual(len(market.stock_low.cards_available()), 5)
        self.assertEqual(len(market.stock_major.cards_available()), 2)
        self.assertEqual(len(market.stock_high.cards_available()), 4)
        self.assertEqual(len(market.stock_low.deck), 1)
        self.assertEqual(len(market.stock_major.deck), 1)
        self.assertEqual(len(market.stock_high.deck), 0)
