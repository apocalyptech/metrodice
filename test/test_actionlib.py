#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from metrodice import actionlib, cards, markets, gamelib

class ActionTestBase(unittest.TestCase):
    """
    Common functions for most of our Action-based tests
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

class ActionBaseTests(ActionTestBase):
    """
    Tests for our base Action class
    """

    def test_unimplemented(self):
        """
        The base 'Action' class is unimplemented, probably shouldn't
        actually do anything.
        """
        action = actionlib.Action('Action', self.player)
        with self.assertRaises(Exception):
            action.do_action()

class ActionRollOneTests(ActionTestBase):
    """
    Tests for ActionRollOne
    """

    def test_desc_initial_roll(self):
        """
        Test the description of the action when we're doing an initial roll
        """
        action = actionlib.ActionRollOne(self.player)
        self.assertEqual(action.desc, 'Roll One Die')

    def test_desc_reroll(self):
        """
        Test the description of the action when we're doing a reroll
        """
        action = actionlib.ActionRollOne(self.player, num_to_reroll=None)
        self.assertEqual(action.desc, 'Reroll One Die')

    def test_action(self):
        """
        Test to ensure that the action does what it's supposed to.
        """
        self.assertEqual(self.game.rolled_dice, 0)
        self.assertEqual(self.game.roll_result, 0)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        action = actionlib.ActionRollOne(self.player)
        action.do_action()
        self.assertEqual(self.game.rolled_dice, 1)
        self.assertGreaterEqual(self.game.roll_result, 1)
        self.assertLessEqual(self.game.roll_result, 6)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)

    def test_hit_card(self):
        """
        Test to make sure that we hit cards properly when a number is rolled.
        (Hitting on the player's default Bakery here)
        """
        self.assertEqual(self.game.rolled_dice, 0)
        self.assertEqual(self.game.roll_result, 0)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertEqual(self.player.money, 3)
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        action = actionlib.ActionRollOne(self.player)
        action._rolled_dice(3)
        self.assertEqual(self.game.rolled_dice, 1)
        self.assertEqual(self.game.roll_result, 3)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertEqual(self.player.money, 4)
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)

class ActionRollTwoTests(ActionTestBase):
    """
    Tests for ActionRollTwo.
    """

    def test_desc_initial_roll(self):
        """
        Test the description of the action when we're doing an initial roll
        """
        action = actionlib.ActionRollTwo(self.player)
        self.assertEqual(action.desc, 'Roll Two Dice')

    def test_desc_reroll(self):
        """
        Test the description of the action when we're doing a reroll
        """
        action = actionlib.ActionRollTwo(self.player, num_to_reroll=None)
        self.assertEqual(action.desc, 'Reroll Two Dice')

    def test_action(self):
        """
        Test to ensure that the action does what it's supposed to.
        """
        self.assertEqual(self.game.rolled_dice, 0)
        self.assertEqual(self.game.roll_result, 0)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        action = actionlib.ActionRollTwo(self.player)
        action.do_action()
        self.assertEqual(self.game.rolled_dice, 2)
        self.assertGreaterEqual(self.game.roll_result, 2)
        self.assertLessEqual(self.game.roll_result, 12)
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)

    def test_rolled_no_doubles(self):
        """
        Test what happens when we don't roll doubles
        """
        self.assertEqual(self.game.rolled_dice, 0)
        self.assertEqual(self.game.roll_result, 0)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertEqual(self.player.money, 3)
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        action = actionlib.ActionRollTwo(self.player)
        action._rolled_dice(1, 2)
        self.assertEqual(self.game.rolled_dice, 2)
        self.assertEqual(self.game.roll_result, 3)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertEqual(self.player.money, 4)
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)

    def test_rolled_doubles(self):
        """
        Test what happens when we do roll doubles
        """
        self.player.add_card(cards.CardConvenienceStore(self.game))
        self.assertEqual(self.game.rolled_dice, 0)
        self.assertEqual(self.game.roll_result, 0)
        self.assertEqual(self.player.rolled_doubles, False)
        self.assertEqual(self.player.money, 3)
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        action = actionlib.ActionRollTwo(self.player)
        action._rolled_dice(2, 2)
        self.assertEqual(self.game.rolled_dice, 2)
        self.assertEqual(self.game.roll_result, 4)
        self.assertEqual(self.player.rolled_doubles, True)
        self.assertEqual(self.player.money, 6)
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)

class ActionKeepRollTests(ActionTestBase):
    """
    Tests for ActionKeepRoll
    """

    def test_do_action(self):
        """
        Test keeping a die roll
        """
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 3)
        action = actionlib.ActionKeepRoll(self.player, 3)
        action.do_action()
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 4)

class ActionAddToRollTests(ActionTestBase):
    """
    Tests for ActionAddToRoll
    """

    def test_do_action_miss_card(self):
        """
        Make sure that taking this action increases the dice roll.  In this case,
        no card is hit, though.
        """
        self.player.add_card(cards.CardAppleOrchard(self.game))
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 3)
        action = actionlib.ActionAddToRoll(self.player, roll=10)
        action.do_action()
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 3)

    def test_do_action_hit_card(self):
        """
        Make sure that taking this action increases the dice roll - this time,
        a card is hit.
        """
        # Remember we start with one wheat, so a Fruit+Veg will pay out
        self.player.add_card(cards.CardFruitAndVeg(self.game))
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 3)
        action = actionlib.ActionAddToRoll(self.player, roll=10)
        action.do_action()
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 5)

    def test_do_action_higher_num_to_add(self):
        """
        This is entirely hypothetical, but the action class supports adding more
        than two to the die result.
        """
        self.player.add_card(cards.CardFruitAndVeg(self.game))
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 3)
        action = actionlib.ActionAddToRoll(self.player, roll=6, num_to_add=6)
        action.do_action()
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 5)

class ActionSkipBuyTests(ActionTestBase):
    """
    Tests for ActionSkipBuy
    """

    def test_action_without_airport(self):
        """
        Test a simple skipping of the buy phase, when the player doesn't have an airport.
        """
        self.game.state = gamelib.Game.STATE_PURCHASE_DECISION
        self.assertEqual(self.player.money, 3)
        action = actionlib.ActionSkipBuy(self.player)
        action.do_action()
        self.assertEqual(self.game.state, gamelib.Game.STATE_TURN_BEGIN)
        self.assertEqual(self.player.money, 3)

    def test_action_with_airport(self):
        """
        Test a simple skipping of the buy phase, when the player does have an airport.
        The player should receive ten coins for not buying anything.
        """
        # A bit silly when we could just set the Player var directly.
        landmark = cards.LandmarkAirport(self.player)
        landmark.construct()

        self.game.state = gamelib.Game.STATE_PURCHASE_DECISION
        self.assertEqual(self.player.gets_ten_coins_for_not_building, landmark)
        self.assertEqual(self.player.money, 3)
        action = actionlib.ActionSkipBuy(self.player)
        action.do_action()
        self.assertEqual(self.game.state, gamelib.Game.STATE_TURN_BEGIN)
        self.assertEqual(self.player.money, 13)

class ActionBuyCardTests(unittest.TestCase):
    """
    Tests for ActionBuyCard
    """

    def setUp(self):
        """
        These tests require a bit more out of the Game's market instance
        """
        self.player = gamelib.Player(name='Player')
        self.game = gamelib.Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[(1, cards.CardWheat)],
                    deck_major=[],
                    landmarks=[]),
                markets.MarketBase)
        self.game.state = gamelib.Game.STATE_PURCHASE_DECISION

    def test_buy_card_from_market(self):
        """
        Buy an available card from the market, while having the funds to do so.
        """
        self.assertEqual(self.player.money, 3)
        self.assertEqual(len(self.player.deck), 2)
        available = self.game.market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, qty) in available.items():
            self.assertEqual(type(card), cards.CardWheat)
            self.assertEqual(qty, 1)

        action = actionlib.ActionBuyCard(self.player, card)
        action.do_action()

        self.assertEqual(self.player.money, 2)
        self.assertEqual(len(self.player.deck), 3)
        available = self.game.market.cards_available()
        self.assertEqual(len(available), 0)
        self.assertEqual(self.game.state, gamelib.Game.STATE_TURN_BEGIN)

    def test_buy_card_not_in_market(self):
        """
        Attempt to buy a card, but the card's not actually in the market.
        """
        action = actionlib.ActionBuyCard(self.player, cards.CardBakery(self.game))
        with self.assertRaises(Exception):
            action.do_action()

    def test_buy_card_from_market_without_funds(self):
        """
        Buy an available card from the market, but without having the funds to
        do so.
        """
        self.player.money = 0
        self.assertEqual(self.player.money, 0)
        self.assertEqual(len(self.player.deck), 2)
        available = self.game.market.cards_available()
        self.assertEqual(len(available), 1)
        for (card, qty) in available.items():
            self.assertEqual(type(card), cards.CardWheat)
            self.assertEqual(qty, 1)

        action = actionlib.ActionBuyCard(self.player, card)
        with self.assertRaises(Exception):
            action.do_action()

class ActionBuyLandmarkTests(unittest.TestCase):
    """
    Tests for ActionBuyLandmark
    """

    def setUp(self):
        """
        As for ActionBuyCard, we want a bit more out of our Game object for these.
        """
        self.player = gamelib.Player(name='Player')
        self.game = gamelib.Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[cards.LandmarkHarbor, cards.LandmarkTrainStation]),
                markets.MarketBase)
        self.game.state = gamelib.Game.STATE_PURCHASE_DECISION

    def test_construct_landmark(self):
        """
        Test a successful activation
        """
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(len(self.player.landmarks), 2)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, False)
        harbor = sorted(self.player.landmarks)[0]

        action = actionlib.ActionBuyLandmark(self.player, harbor)
        action.do_action()

        self.assertEqual(self.game.state, gamelib.Game.STATE_TURN_BEGIN)
        self.assertEqual(len(self.player.landmarks), 2)
        self.assertEqual(self.player.money, 1)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, self.player.landmarks[0])

    def test_construct_landmark_end_game(self):
        """
        Test a successful activation which ends the game
        """
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(len(self.player.landmarks), 2)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, False)
        harbor = sorted(self.player.landmarks)[0]
        station = sorted(self.player.landmarks)[1]
        station.constructed = True

        action = actionlib.ActionBuyLandmark(self.player, harbor)
        action.do_action()

        self.assertEqual(self.game.state, gamelib.Game.STATE_GAME_OVER)
        self.assertEqual(len(self.player.landmarks), 2)
        self.assertEqual(self.player.money, 1)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, harbor)

    def test_construct_landmark_without_funds(self):
        """
        Test a construction attempt but without funds
        """
        self.player.money = 0
        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(len(self.player.landmarks), 2)
        self.assertEqual(self.player.money, 0)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, False)
        harbor = sorted(self.player.landmarks)[0]

        action = actionlib.ActionBuyLandmark(self.player, harbor)
        with self.assertRaises(Exception):
            action.do_action()

class ActionChoosePlayer(unittest.TestCase):
    """
    Tests for ActionChoosePlayer.  This Action relies on some implementation
    from a calling card - at the moment the only one which does so is the
    TV Station.  The TV Station tests themselves are elsewhere, of course, in
    `test_cards.py`
    """

    def setUp(self):
        """
        Our tests will require a Game object
        """
        self.player = gamelib.Player(name='Player')
        self.player2 = gamelib.Player(name='Player 2')
        self.game = gamelib.Game([self.player, self.player2],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                markets.MarketBase)
        self.station = cards.CardTVStation(self.game)
        self.player.add_card(self.station)

    def test_do_action(self):
        """
        Test choosing a player.  Nothing much happens in this class itself;
        it's all in the Card's class.
        """
        self.assertNotEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player2.money, 3)

        action = actionlib.ActionChoosePlayer(self.player, self.station, self.player2)
        action.do_action()

        self.assertEqual(self.game.state, gamelib.Game.STATE_PURCHASE_DECISION)
        self.assertEqual(self.player.money, 6)
        self.assertEqual(self.player2.money, 0)

class ActionChooseOwnOtherCard(unittest.TestCase):
    """
    Tests for ActionChooseOwnCard and ActionChooseOtherCard.  These Actions rely on
    some implementation from a calling card - at the moment the only one which does
    so is the Business Center.  The Business Center tests themselves are elsewhere,
    of course, in `test_cards.py`
    """

    def setUp(self):
        """
        Our tests will require a Game object
        """
        self.player = gamelib.Player(name='Player')
        self.player2 = gamelib.Player(name='Player 2')
        self.game = gamelib.Game([self.player, self.player2],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                markets.MarketBase)
        self.station = cards.CardBusinessCenter(self.game)
        self.player.add_card(self.station)
        self.cafe = cards.CardCafe(self.game)
        self.player.add_card(self.cafe)
        self.forest = cards.CardForest(self.game)
        self.player2.add_card(self.forest)

    def test_choose_own_card(self):
        """
        Test choosing one of our own cards
        """
        self.assertEqual(self.station.trade_owner, None)
        action = actionlib.ActionChooseOwnCard(self.player, self.station, self.cafe)
        action.do_action()
        self.assertEqual(self.station.trade_owner, self.cafe)

    def test_choose_other_card(self):
        """
        Test choosing one of an opponent's cards
        """
        self.assertEqual(self.station.trade_other, None)
        action = actionlib.ActionChooseOtherCard(self.player, self.station, self.forest)
        action.do_action()
        self.assertEqual(self.station.trade_other, self.forest)
