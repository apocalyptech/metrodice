#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from metrodice import cards, actionlib
from metrodice.gamelib import Player, Game, \
        MarketBase, MarketHarbor, MarketBrightLights

class BaseCardTests(unittest.TestCase):
    """
    Base class which provides various new_card methods for ease of test writing.
    """

    def new_card(self, name, game=None, desc=None, short_desc=None,
            color=None, family=None, cost=0, activations=[1],
            required_landmark=None):
        """
        The actual Card class has all of its vars as required, which
        we don't actually need for many of our tests.  This wrapper just
        lets us pretend that they're optional.  We'll require name, though,
        since otherwise repr() will break.
        """
        return cards.Card(
            game=game,
            name=name,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
            required_landmark=required_landmark,
        )

    def new_payout_card(self, name, payout, game=None, desc=None, short_desc=None,
            color=None, family=None, cost=0, activations=[1],
            required_landmark=None):
        """
        The actual Card class has all of its vars as required, which
        we don't actually need for many of our tests.  This wrapper just
        lets us pretend that they're optional.  We'll require name, though,
        since otherwise repr() will break.
        """
        return cards.CardBasicPayout(
            game=game,
            name=name,
            payout=payout,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
            required_landmark=required_landmark,
        )

    def new_factory_family_card(self, name, payout, target_family, game=None, desc=None,
            short_desc=None, color=None, family=cards.Card.FAMILY_FACTORY, cost=0, activations=[1],
            required_landmark=None):
        """
        The actual Card class has all of its vars as required, which
        we don't actually need for many of our tests.  This wrapper just
        lets us pretend that they're optional.  We'll require name, though,
        since otherwise repr() will break.
        """
        return cards.CardFactoryFamily(
            game=game,
            name=name,
            payout=payout,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            target_family=target_family,
            activations=activations,
            required_landmark=required_landmark,
        )

    def new_factory_card_card(self, name, payout, target_card_type, game=None, desc=None,
            short_desc=None, color=None, family=cards.Card.FAMILY_FACTORY, cost=0, activations=[1],
            required_landmark=None):
        """
        The actual Card class has all of its vars as required, which
        we don't actually need for many of our tests.  This wrapper just
        lets us pretend that they're optional.  We'll require name, though,
        since otherwise repr() will break.
        """
        return cards.CardFactoryCard(
            game=game,
            name=name,
            payout=payout,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            target_card_type=target_card_type,
            activations=activations,
            required_landmark=required_landmark,
        )

    def new_red_card(self, name, fee, game=None, desc=None, short_desc=None,
            color=cards.Card.COLOR_RED, family=cards.Card.FAMILY_CUP, cost=0,
            activations=[1], required_landmark=None):
        """
        The actual Card class has all of its vars as required, which
        we don't actually need for many of our tests.  This wrapper just
        lets us pretend that they're optional.  We'll require name, though,
        since otherwise repr() will break.
        """
        return cards.CardBasicRed(
            game=game,
            name=name,
            fee=fee,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
            required_landmark=required_landmark,
        )

class CardTests(BaseCardTests):
    """
    Tests against our generic Card class
    """

    def test_card_repr(self):
        """
        Test to make sure that a card's repr() is its name
        """
        card = self.new_card(name='Card Name')
        self.assertEqual(repr(card), 'Card Name')

    def test_card_color_str(self):
        """
        Test to make sure a card's color string works
        """
        for (enum, english) in [
                (cards.Card.COLOR_BLUE, 'Blue'),
                (cards.Card.COLOR_GREEN, 'Green'),
                (cards.Card.COLOR_RED, 'Red'),
                (cards.Card.COLOR_PURPLE, 'Purple'),
                ]:
            with self.subTest(color=english):
                card = self.new_card(name='Color Test', color=enum)
                self.assertEqual(card.color_str(), english)

    def test_card_family_str(self):
        """
        Test to make sure a card's family string works
        """
        for (enum, english) in [
                (cards.Card.FAMILY_WHEAT, 'Wheat'),
                (cards.Card.FAMILY_COW, 'Cow'),
                (cards.Card.FAMILY_GEAR, 'Gear'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                (cards.Card.FAMILY_FACTORY, 'Factory'),
                (cards.Card.FAMILY_FRUIT, 'Fruit'),
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_MAJOR, 'Major Establishment'),
                (cards.Card.FAMILY_BOAT, 'Boat'),
                ]:
            with self.subTest(family=english):
                card = self.new_card(name='Family Test', family=enum)
                self.assertEqual(card.family_str(), english)

    def test_card_sorting_different_activation_num(self):
        """
        Cards with a different activation number should be sorted in order
        of their activations.
        """
        card_5 = self.new_card(name='Five', activations=[5])
        card_6 = self.new_card(name='Six', activations=[6])
        self.assertEqual(sorted([card_6, card_5]), [card_5, card_6])

    def test_card_sorting_different_number_of_activations(self):
        """
        If two cards have the same first activation number but have different
        numbers of activations, the one with the longest activation length
        goes afterwards.
        """
        card_single = self.new_card(name='Single', activations=[2])
        card_many = self.new_card(name='Many', activations=[2, 3])
        self.assertEqual(sorted([card_many, card_single]), [card_single, card_many])

    def test_card_sorting_different_colors(self):
        """
        Cards should be sorted blue -> green -> red -> purple
        """
        card_blue = self.new_card(name='Blue', color=cards.Card.COLOR_BLUE, activations=[1])
        card_green = self.new_card(name='Green', color=cards.Card.COLOR_GREEN, activations=[1])
        card_red = self.new_card(name='Red', color=cards.Card.COLOR_RED, activations=[1])
        card_purple = self.new_card(name='Purple', color=cards.Card.COLOR_PURPLE, activations=[1])
        self.assertEqual(
                sorted([card_purple, card_red, card_green, card_blue]),
                [card_blue, card_green, card_red, card_purple]
            )

    def test_card_sorting_name(self):
        """
        Lastly, in the event that all other criteria match, sorting should be by
        name.
        """
        card_aaa = self.new_card(name='AAA', color=cards.Card.COLOR_BLUE, activations=[1])
        card_zzz = self.new_card(name='ZZZ', color=cards.Card.COLOR_BLUE, activations=[1])
        self.assertEqual(sorted([card_zzz, card_aaa]), [card_aaa, card_zzz])

    def test_card_sorting_color_before_name(self):
        """
        Color should be sorted before names
        """
        card_blue = self.new_card(name='ZZZ', color=cards.Card.COLOR_BLUE, activations=[1])
        card_purple = self.new_card(name='AAA', color=cards.Card.COLOR_PURPLE, activations=[1])
        self.assertEqual(sorted([card_purple, card_blue]), [card_blue, card_purple])

    def test_card_sorting_num_activations_before_color(self):
        """
        Number of activations should be sorted before color
        """
        card_single = self.new_card(name='Single', color=cards.Card.COLOR_PURPLE, activations=[2])
        card_many = self.new_card(name='Many', color=cards.Card.COLOR_BLUE, activations=[2, 3])
        self.assertEqual(sorted([card_many, card_single]), [card_single, card_many])

    def test_card_sorting_different_num_before_num_activations(self):
        """
        First activation num should be sorted before number-of-activations
        """
        card_single = self.new_card(name='Single', activations=[2])
        card_many = self.new_card(name='Many', activations=[1, 2])
        self.assertEqual(sorted([card_single, card_many]), [card_many, card_single])

    def test_card_hit_not_implemented(self):
        """
        A base Card shouldn't actually be allowed to hit.
        """
        card = self.new_card(name='Card')
        with self.assertRaises(Exception):
            card.hit(None)

    def test_card_not_hit_without_landmark(self):
        """
        If a card has a required landmark, it shouldn't hit if its owner
        doesn't actually have the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_card(name='Card', required_landmark=cards.LandmarkHarbor)
        player = Player(name='Player')
        player.landmarks.append(cards.LandmarkHarbor())
        player.add_card(card)
        try:
            card.hit(None)
        except Exception as e:
            self.fail('card.hit raised an Exception unexpectedly')

    def test_card_hit_with_landmark(self):
        """
        If a card has a required landmark, it should hit if its owner
        has the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_card(name='Card', required_landmark=cards.LandmarkHarbor)
        player = Player(name='Player')
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        player.landmarks.append(landmark)
        player.add_card(card)
        with self.assertRaises(Exception):
            card.hit(None)

    def test_card_bread_cup_bonus_active(self):
        """
        If a player has the required ability and the card is bread or cup,
        we should receive the shopping mall bonus.
        """
        player = Player(name='Player')
        player.has_bread_cup_bonus = True
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                card = self.new_card(name=english, family=enum)
                player.add_card(card)
                self.assertEqual(card.does_bread_cup_bonus_apply(), True)

    def test_card_bread_cup_bonus_not_active_incorrect_family(self):
        """
        If a player has the required ability but the card family is not
        bread or cup, the bonus should not apply.
        """
        player = Player(name='Player')
        player.has_bread_cup_bonus = True
        card = self.new_card(name='Gear', family=cards.Card.FAMILY_GEAR)
        player.add_card(card)
        self.assertEqual(card.does_bread_cup_bonus_apply(), False)

    def test_card_bread_cup_bonus_not_active_no_bonus_flag(self):
        """
        If a player does not have the required ability, even if the card
        is a bread or cup, the bonus should not apply.
        """
        player = Player(name='Player')
        player.has_bread_cup_bonus = False
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                card = self.new_card(name=english, family=enum)
                player.add_card(card)
                self.assertEqual(card.does_bread_cup_bonus_apply(), False)

class CardBasicPayoutTests(BaseCardTests):
    """
    Tests against our generic CardBasicPayout class
    """

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_basic_payout_one_coin(self):
        """
        If our basic card hits, the player should receive the specified payout.
        """
        card = self.new_payout_card(name='One Coin', payout=1, game=self.game)
        self.player.money = 0
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

    def test_basic_payout_three_coins(self):
        """
        If our basic card hits, the player should receive the specified payout.
        """
        card = self.new_payout_card(name='Three Coins', payout=3, game=self.game)
        self.player.money = 0
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 3)

    def test_card_not_hit_without_landmark(self):
        """
        If a card has a required landmark, it shouldn't hit if its owner
        doesn't actually have the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_payout_card(name='Card', payout=1,
            game=self.game, required_landmark=cards.LandmarkHarbor)
        self.player.landmarks.append(cards.LandmarkHarbor())
        self.player.add_card(card)
        self.player.money = 0
        card.hit(None)
        self.assertEqual(self.player.money, 0)

    def test_card_hit_with_landmark(self):
        """
        If a card has a required landmark, it should hit if its owner
        has the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_payout_card(name='Card', payout=1,
            game=self.game, required_landmark=cards.LandmarkHarbor)
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player.money = 0
        self.player.landmarks.append(landmark)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

    def test_card_hit_cup_bread_without_cup_bread_bonus(self):
        """
        If a cup or bread card hits, without the player having a cup/bread bonus,
        don't apply any bonus.
        """
        self.player.has_bread_cup_bonus = False
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                self.player.money = 0
                card = self.new_payout_card(name='Card', payout=1,
                    game=self.game, family=enum)
                self.player.add_card(card)
                card.hit(None)
                self.assertEqual(self.player.money, 1)

    def test_card_hit_cup_bread_with_cup_bread_bonus(self):
        """
        If a cup or bread card hits, with the player having a cup/bread bonus,
        apply any bonus.
        """
        self.player.has_bread_cup_bonus = True
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                self.player.money = 0
                card = self.new_payout_card(name='Card', payout=1,
                    game=self.game, family=enum)
                self.player.add_card(card)
                card.hit(None)
                self.assertEqual(self.player.money, 2)

    def test_card_hit_non_cup_bread_with_cup_bread_bonus(self):
        """
        If a non-cup-or-bread card hits, with the player having a cup/bread bonus,
        don't apply any bonus.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        card = self.new_payout_card(name='Card', payout=1,
            game=self.game, family=cards.Card.FAMILY_GEAR)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

class CardFactoryFamilyTests(BaseCardTests):
    """
    Tests against our generic CardFactoryFamily class
    """

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.  Players start with a WHEAT and BREAD
        card - we'll add an additional two CUP cards so we have something to
        match on.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)
        self.player.add_card(self.new_card(name='Cup 1', family=cards.Card.FAMILY_CUP))
        self.player.add_card(self.new_card(name='Cup 2', family=cards.Card.FAMILY_CUP))

    def test_no_matches(self):
        """
        If the factory card doesn't actually match anything, the player gets nothing.
        """
        self.player.money = 0
        card = self.new_factory_family_card(name='Card',
            payout=1, target_family=cards.Card.FAMILY_GEAR,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 0)

    def test_single_match(self):
        """
        If the factory card matches a single card, get the payout.
        """
        self.player.money = 0
        card = self.new_factory_family_card(name='Card',
            payout=1, target_family=cards.Card.FAMILY_BREAD,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

    def test_two_matches(self):
        """
        If the factory card matches two cards, get the appropriate payout.
        """
        self.player.money = 0
        card = self.new_factory_family_card(name='Card',
            payout=1, target_family=cards.Card.FAMILY_CUP,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 2)

    def test_two_matches_larger_payout(self):
        """
        If the factory card matches two cards, get the appropriate payout.
        """
        self.player.money = 0
        card = self.new_factory_family_card(name='Card',
            payout=3, target_family=cards.Card.FAMILY_CUP,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 6)

    def test_card_not_hit_without_landmark(self):
        """
        If a card has a required landmark, it shouldn't hit if its owner
        doesn't actually have the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_factory_family_card(name='Card',
            payout=1, target_family=cards.Card.FAMILY_BREAD,
            game=self.game, required_landmark=cards.LandmarkHarbor)
        self.player.landmarks.append(cards.LandmarkHarbor())
        self.player.add_card(card)
        self.player.money = 0
        card.hit(None)
        self.assertEqual(self.player.money, 0)

    def test_card_hit_with_landmark(self):
        """
        If a card has a required landmark, it should hit if its owner
        has the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_factory_family_card(name='Card',
            payout=1, target_family=cards.Card.FAMILY_BREAD,
            game=self.game, required_landmark=cards.LandmarkHarbor)
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player.money = 0
        self.player.landmarks.append(landmark)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

    def test_card_hit_cup_bread_without_cup_bread_bonus(self):
        """
        If a cup or bread card hits, without the player having a cup/bread bonus,
        don't apply any bonus.  This is purely hypothetical since no factory-style
        cards are of type cup/bread.
        """
        self.player.has_bread_cup_bonus = False
        for (enum, english, total_payout) in [
                (cards.Card.FAMILY_CUP, 'Cup', 1),
                (cards.Card.FAMILY_BREAD, 'Bread', 2),
                ]:
            with self.subTest(family=english):
                self.player.money = 0
                card = self.new_factory_family_card(name='Card',
                    payout=1, target_family=cards.Card.FAMILY_BREAD,
                    game=self.game, family=enum)
                self.player.add_card(card)
                card.hit(None)
                self.assertEqual(self.player.money, total_payout)

    def test_card_hit_cup_bread_with_cup_bread_bonus(self):
        """
        If a cup or bread card hits, with the player having a cup/bread bonus,
        apply any bonus.  This is purely hypothetical since no factory-style
        cards are of type cup/bread.
        """
        self.player.has_bread_cup_bonus = True
        for (enum, english, total_payout) in [
                (cards.Card.FAMILY_CUP, 'Cup', 2),
                (cards.Card.FAMILY_BREAD, 'Bread', 3),
                ]:
            with self.subTest(family=english):
                self.player.money = 0
                card = self.new_factory_family_card(name='Card',
                    payout=1, target_family=cards.Card.FAMILY_BREAD,
                    game=self.game, family=enum)
                self.player.add_card(card)
                card.hit(None)
                self.assertEqual(self.player.money, total_payout)

    def test_card_hit_non_cup_bread_with_cup_bread_bonus(self):
        """
        If a non-cup-or-bread card hits, with the player having a cup/bread bonus,
        don't apply any bonus.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        card = self.new_factory_family_card(name='Card',
            payout=1, target_family=cards.Card.FAMILY_BREAD,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

class CardFactoryCardTests(BaseCardTests):
    """
    Tests against our generic CardFactoryCard class
    """

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.  Players start with a Wheat and Bakery
        card - we'll add an additional Bakery card so we have something to
        match on.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)
        self.player.add_card(cards.CardBakery(self.game))

    def test_no_matches(self):
        """
        If the factory card doesn't actually match anything, the player gets nothing.
        """
        self.player.money = 0
        card = self.new_factory_card_card(name='Card',
            payout=1, target_card_type=cards.CardCafe,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 0)

    def test_single_match(self):
        """
        If the factory card matches a single card, get the payout.
        """
        self.player.money = 0
        card = self.new_factory_card_card(name='Card',
            payout=1, target_card_type=cards.CardWheat,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

    def test_two_matches(self):
        """
        If the factory card matches two cards, get the appropriate payout.
        """
        self.player.money = 0
        card = self.new_factory_card_card(name='Card',
            payout=1, target_card_type=cards.CardBakery,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 2)

    def test_two_matches_larger_payout(self):
        """
        If the factory card matches two cards, get the appropriate payout.
        """
        self.player.money = 0
        card = self.new_factory_card_card(name='Card',
            payout=3, target_card_type=cards.CardBakery,
            game=self.game)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 6)

    def test_card_not_hit_without_landmark(self):
        """
        If a card has a required landmark, it shouldn't hit if its owner
        doesn't actually have the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_factory_card_card(name='Card',
            payout=1, target_card_type=cards.CardWheat,
            game=self.game, required_landmark=cards.LandmarkHarbor)
        self.player.landmarks.append(cards.LandmarkHarbor())
        self.player.add_card(card)
        self.player.money = 0
        card.hit(None)
        self.assertEqual(self.player.money, 0)

    def test_card_hit_with_landmark(self):
        """
        If a card has a required landmark, it should hit if its owner
        has the landmark constructed.  We're looking for Exceptions
        since we're dealing with unimplemented Card objects here.
        """
        card = self.new_factory_card_card(name='Card',
            payout=1, target_card_type=cards.CardWheat,
            game=self.game, required_landmark=cards.LandmarkHarbor)
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player.money = 0
        self.player.landmarks.append(landmark)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

    def test_card_hit_cup_bread_without_cup_bread_bonus(self):
        """
        If a cup or bread card hits, without the player having a cup/bread bonus,
        don't apply any bonus.  This is purely hypothetical since no factory-style
        cards are of type cup/bread.
        """
        self.player.has_bread_cup_bonus = False
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                self.player.money = 0
                card = self.new_factory_card_card(name='Card',
                    payout=1, target_card_type=cards.CardWheat,
                    game=self.game, family=enum)
                self.player.add_card(card)
                card.hit(None)
                self.assertEqual(self.player.money, 1)

    def test_card_hit_cup_bread_with_cup_bread_bonus(self):
        """
        If a cup or bread card hits, with the player having a cup/bread bonus,
        apply any bonus.  This is purely hypothetical since no factory-style
        cards are of type cup/bread.
        """
        self.player.has_bread_cup_bonus = True
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                self.player.money = 0
                card = self.new_factory_card_card(name='Card',
                    payout=1, target_card_type=cards.CardWheat,
                    game=self.game, family=enum)
                self.player.add_card(card)
                card.hit(None)
                self.assertEqual(self.player.money, 2)

    def test_card_hit_non_cup_bread_with_cup_bread_bonus(self):
        """
        If a non-cup-or-bread card hits, with the player having a cup/bread bonus,
        don't apply any bonus.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        card = self.new_factory_card_card(name='Card',
            payout=1, target_card_type=cards.CardWheat,
            game=self.game, family=cards.Card.FAMILY_GEAR)
        self.player.add_card(card)
        card.hit(None)
        self.assertEqual(self.player.money, 1)

class CardBasicRedTests(BaseCardTests):
    """
    Tests against our generic CardBasicRed class.  Note that the red-card counterclockwise
    payout will have to be tested out in the game classes, not here, since
    cards.py doesn't deal with that at all.
    """

    def setUp(self):
        """
        Setup methods.  For many of these we'll need 2 Players and a Game,
        so let's go ahead and make them.
        """
        self.player_rolled = Player(name='Player who rolled the die')
        self.player_card = Player(name='Player 2')
        self.game = Game([self.player_rolled, self.player_card],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_other_player_has_sufficient_funds(self):
        """
        Test what happens when the other player has sufficient funds to be stolen.
        """
        card = self.new_red_card(name='Red', fee=2, game=self.game)
        self.player_card.add_card(card)
        self.player_card.money = 0
        self.player_rolled.money = 3
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 2)
        self.assertEqual(self.player_rolled.money, 1)

    def test_other_player_has_partial_funds(self):
        """
        Test what happens when the other player has partial funds to be stolen.
        """
        card = self.new_red_card(name='Red', fee=2, game=self.game)
        self.player_card.add_card(card)
        self.player_card.money = 0
        self.player_rolled.money = 1
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 1)
        self.assertEqual(self.player_rolled.money, 0)

    def test_other_player_has_no_funds(self):
        """
        Test what happens when the other player has no funds to be stolen.
        """
        card = self.new_red_card(name='Red', fee=2, game=self.game)
        self.player_card.add_card(card)
        self.player_card.money = 3
        self.player_rolled.money = 0
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 3)
        self.assertEqual(self.player_rolled.money, 0)

    def test_card_bread_cup_player_card_bonus_active(self):
        """
        Test for when our red card gets a bread/cup bonus.  (In reality it'd
        only ever be CUP, since that's what all red cards are, but whatever.)
        """
        self.player_card.has_bread_cup_bonus = True
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                card = self.new_red_card(name='Red', fee=2, game=self.game, family=enum)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = 4
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, 3)
                self.assertEqual(self.player_rolled.money, 1)

    def test_card_bread_cup_player_card_bonus_not_active(self):
        """
        Test for when our red card doe NOT get a bread/cup bonus, because the player
        doesn't have the required ability.
        """
        self.player_card.has_bread_cup_bonus = False
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                card = self.new_red_card(name='Red', fee=2, game=self.game, family=enum)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = 4
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, 2)
                self.assertEqual(self.player_rolled.money, 2)

    def test_card_bread_cup_player_rolled_bonus_active(self):
        """
        Test for when our red card does not get a bread/cup bonus, but the rolled
        player has the bonus active.  No bonus should be applied!
        """
        self.player_card.has_bread_cup_bonus = False
        self.player_rolled.has_bread_cup_bonus = True
        for (enum, english) in [
                (cards.Card.FAMILY_CUP, 'Cup'),
                (cards.Card.FAMILY_BREAD, 'Bread'),
                ]:
            with self.subTest(family=english):
                card = self.new_red_card(name='Red', fee=2, game=self.game, family=enum)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = 4
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, 2)
                self.assertEqual(self.player_rolled.money, 2)

    def test_card_bread_cup_bonus_not_active_incorrect_family(self):
        """
        Test when a red card isn't the correct family to receive a cup/bread bonus.
        This is entirely hypothetical since all red cards are currently CUP.
        """
        self.player_card.has_bread_cup_bonus = True
        card = self.new_red_card(name='Red', fee=2, game=self.game, family=cards.Card.FAMILY_GEAR)
        self.player_card.add_card(card)
        self.player_card.money = 0
        self.player_rolled.money = 3
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 2)
        self.assertEqual(self.player_rolled.money, 1)

    def test_card_hit_with_landmark(self):
        """
        If we have the required landmark, the card should hit properly.
        """
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player_card.landmarks.append(landmark)

        card = self.new_red_card(name='Red', fee=2, game=self.game,
            required_landmark=cards.LandmarkHarbor)
        self.player_card.add_card(card)
        self.player_card.money = 0
        self.player_rolled.money = 3
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 2)
        self.assertEqual(self.player_rolled.money, 1)

    def test_card_hit_without_landmark(self):
        """
        If we don't have the required landmark, the card should not hit.
        """
        landmark = cards.LandmarkHarbor()
        landmark.constructed = False
        self.player_card.landmarks.append(landmark)

        card = self.new_red_card(name='Red', fee=2, game=self.game,
            required_landmark=cards.LandmarkHarbor)
        self.player_card.add_card(card)
        self.player_card.money = 0
        self.player_rolled.money = 3
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 0)
        self.assertEqual(self.player_rolled.money, 3)

    def test_card_hit_without_landmark_but_rolled_player_does(self):
        """
        If we don't have the required landmark, the card should not hit,
        even if the player who rolled the dice has the landmark enabled.
        """
        landmark = cards.LandmarkHarbor()
        landmark.constructed = False
        self.player_card.landmarks.append(landmark)

        landmark2 = cards.LandmarkHarbor()
        landmark2.constructed = True
        self.player_rolled.landmarks.append(landmark2)

        card = self.new_red_card(name='Red', fee=2, game=self.game,
            required_landmark=cards.LandmarkHarbor)
        self.player_card.add_card(card)
        self.player_card.money = 0
        self.player_rolled.money = 3
        card.hit(self.player_rolled)
        self.assertEqual(self.player_card.money, 0)
        self.assertEqual(self.player_rolled.money, 3)

class CardNamedRegularBlueTests(BaseCardTests):
    """
    Tests against our regular blue named cards which provide a simple payout.  These
    are all unaffected by cup/bread, and do not have a required landmark
    """

    card_classes = [
            (cards.CardWheat, 'Wheat', 1),
            (cards.CardRanch, 'Ranch', 1),
            (cards.CardForest, 'Forest', 1),
            (cards.CardMine, 'Mine', 5),
            (cards.CardAppleOrchard, 'Apple Orchard', 3),
            (cards.CardFlowerOrchard, 'Flower Orchard', 1),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_basic_payout(self):
        """
        If our basic card hits, the player should receive the specified payout.
        """
        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

    def test_with_cup_bread_bonus(self):
        """
        Test with the user's cup/bread bonus active.  Nothing should change, since
        these cards aren't in the required family.
        """
        self.player.has_bread_cup_bonus = True
        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

class CardNamedHarborBlueTests(BaseCardTests):
    """
    Tests against our Harbor-requiring blue named cards which provide a simple
    payout.  These are all unaffected by cup/bread, but require the Harbor landmark.
    """

    card_classes = [
            (cards.CardMackerelBoat, 'Mackerel Boat', 3),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_basic_payout_without_landmark(self):
        """
        If our basic card hits without a landmark, nothing should happen.
        """

        landmark = cards.LandmarkHarbor()
        landmark.constructed = False
        self.player.landmarks.append(landmark)

        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, 0)

    def test_basic_payout_with_landmark(self):
        """
        If our basic card hits with a landmark, the player should receive the payout.
        """
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player.landmarks.append(landmark)

        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

    def test_basic_payout_with_landmark_and_cup_bread_bonus(self):
        """
        If our basic card hits with a landmark, the player should receive the payout.
        Even if the player has a cup/bread bonus, it should not be applied since these
        cards aren't in the proper family.
        """
        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player.landmarks.append(landmark)

        self.player.has_bread_cup_bonus = True

        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

class CardNamedRegularGreenTests(BaseCardTests):
    """
    Tests against our regular green named cards which provide a simple payout.  These
    are all affected by cup/bread, but do not have a required landmark
    """

    card_classes = [
            (cards.CardBakery, 'Bakery', 1),
            (cards.CardConvenienceStore, 'Convenience Store', 3),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_basic_payout(self):
        """
        If our basic card hits, the player should receive the specified payout.
        """
        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

    def test_with_cup_bread_bonus(self):
        """
        Test with the user's cup/bread bonus active.  Nothing should change, since
        these cards aren't in the required family.
        """
        self.player.has_bread_cup_bonus = True
        for (card_class, name, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout+1)

class CardNamedRegularRedTests(BaseCardTests):
    """
    Tests against our regular red named cards which provide a simple payout.  These
    are all affected by cup/bread bonuses, but do not have a required landmark.
    """

    card_classes = [
            (cards.CardCafe, 'Cafe', 1),
            (cards.CardFamilyRestaurant, 'Family Restaurant', 2),
            (cards.CardPizzaJoint, 'Pizza Joint', 1),
            (cards.CardHamburgerStand, 'Hamburger Stand', 1),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need 2 Players and a Game,
        so let's go ahead and make them.
        """
        self.player_rolled = Player(name='Player who rolled the die')
        self.player_card = Player(name='Player 2')
        self.game = Game([self.player_rolled, self.player_card],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_other_player_has_sufficient_funds(self):
        """
        Test what happens when the other player has sufficient funds to be stolen.
        """
        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee + 1
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, fee)
                self.assertEqual(self.player_rolled.money, 1)

    def test_other_player_has_partial_funds(self):
        """
        Test what happens when the other player has partial funds to be stolen.
        (this'll actually be zero funds for most of them)
        """
        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee - 1
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, fee - 1)
                self.assertEqual(self.player_rolled.money, 0)

    def test_other_player_has_no_funds(self):
        """
        Test what happens when the other player has no funds to be stolen.
        """
        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 3
                self.player_rolled.money = 0
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, 3)
                self.assertEqual(self.player_rolled.money, 0)

    def test_other_player_has_sufficient_funds_with_cup_bread_bonus(self):
        """
        Test what happens when the other player has sufficient funds to be stolen,
        when the player's cup/bread bonus is active
        """
        self.player_card.has_bread_cup_bonus = True
        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee + 2
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, fee + 1)
                self.assertEqual(self.player_rolled.money, 1)

class CardNamedHarborRedTests(BaseCardTests):
    """
    Tests against our Harbor red named cards which provide a simple payout.  These
    are all affected by cup/bread bonuses, and require a Harbor.
    """

    card_classes = [
            (cards.CardSushiBar, 'Sushi Bar', 3),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need 2 Players and a Game,
        so let's go ahead and make them.
        """
        self.player_rolled = Player(name='Player who rolled the die')
        self.player_card = Player(name='Player 2')
        self.game = Game([self.player_rolled, self.player_card],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_other_player_has_sufficient_funds_no_harbor(self):
        """
        Test what happens when the other player has sufficient funds to be stolen,
        but no harbor.
        """

        landmark = cards.LandmarkHarbor()
        landmark.constructed = False
        self.player_card.landmarks.append(landmark)

        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee + 1
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, 0)
                self.assertEqual(self.player_rolled.money, fee + 1)

    def test_other_player_has_sufficient_funds_with_harbor(self):
        """
        Test what happens when the other player has sufficient funds to be stolen,
        and a constructed harbor.
        """

        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player_card.landmarks.append(landmark)

        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee + 1
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, fee)
                self.assertEqual(self.player_rolled.money, 1)

    def test_other_player_has_partial_funds(self):
        """
        Test what happens when the other player has partial funds to be stolen.
        """

        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player_card.landmarks.append(landmark)

        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee - 1
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, fee - 1)
                self.assertEqual(self.player_rolled.money, 0)

    def test_other_player_has_no_funds(self):
        """
        Test what happens when the other player has no funds to be stolen.
        """

        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player_card.landmarks.append(landmark)

        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 3
                self.player_rolled.money = 0
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, 3)
                self.assertEqual(self.player_rolled.money, 0)

    def test_other_player_has_sufficient_funds_with_cup_bread_bonus(self):
        """
        Test what happens when the other player has sufficient funds to be stolen,
        when the player's cup/bread bonus is active
        """

        landmark = cards.LandmarkHarbor()
        landmark.constructed = True
        self.player_card.landmarks.append(landmark)

        self.player_card.has_bread_cup_bonus = True
        for (card_class, name, fee) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player_card.add_card(card)
                self.player_card.money = 0
                self.player_rolled.money = fee + 2
                card.hit(self.player_rolled)
                self.assertEqual(self.player_card.money, fee + 1)
                self.assertEqual(self.player_rolled.money, 1)

class CardNamedFactoryFamilyTests(BaseCardTests):
    """
    Tests against our regular named FactoryFamily cards.  None of these are
    affected by cup/bread bonuses, and do not require landmarks.
    """

    card_classes = [
            (cards.CardCheeseFactory, 'Cheese Factory', cards.Card.FAMILY_COW, 3),
            (cards.CardFurnitureFactory, 'Furniture Factory', cards.Card.FAMILY_GEAR, 3),
            (cards.CardFruitAndVeg, 'Fruit and Veg', cards.Card.FAMILY_WHEAT, 2),
            (cards.CardFoodWarehouse, 'Food Warehouse', cards.Card.FAMILY_CUP, 2),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        # Get rid of our default cards for the player, so we can control the tests
        # a little better without having to do weird special cases.
        for card in list(self.player.deck):
            self.player.remove_card(card)

    def test_hit_without_any_necessary_cards(self):
        """
        Test what happens when we don't have any of the required cards to pay out.
        """
        for (card_class, name, target_family, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, 0)

    def test_hit_with_one_necessary_card(self):
        """
        Test what happens when we have a single card that matches.
        """
        for (card_class, name, target_family, payout) in self.card_classes:
            with self.subTest(card=name):
                self.player.add_card(self.new_card(
                    name=cards.Card.ENG_FAMILY[target_family],
                    family=target_family,
                ))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

    def test_hit_with_three_necessary_cards(self):
        """
        Test what happens when we have three cards that match.
        """
        for (card_class, name, target_family, payout) in self.card_classes:
            with self.subTest(card=name):
                for i in range(3):
                    self.player.add_card(self.new_card(
                        name=cards.Card.ENG_FAMILY[target_family],
                        family=target_family,
                    ))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout*3)

    def test_hit_with_one_necessary_card_with_cup_bread_bonus(self):
        """
        Test what happens when we have a single card that matches, and the player
        has a cup/bread bonus.  The bonus should not apply, since none of the
        factory cards are CUP or BREAD.
        """
        self.player.has_bread_cup_bonus = True
        for (card_class, name, target_family, payout) in self.card_classes:
            with self.subTest(card=name):
                self.player.add_card(self.new_card(
                    name=cards.Card.ENG_FAMILY[target_family],
                    family=target_family,
                ))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

class CardNamedFactoryCardTests(BaseCardTests):
    """
    Tests against our regular named FactoryCard cards.  These are all
    affected by cup/bread bonuses, and do not require landmarks.
    """

    card_classes = [
            (cards.CardFlowerShop, 'Flower Shop', cards.CardFlowerOrchard, 1),
        ]

    def setUp(self):
        """
        Setup methods.  For many of these we'll need a Player and a Game,
        so let's go ahead and make them.
        """
        self.player = Player(name='Player')
        self.game = Game([self.player],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

    def test_hit_without_any_necessary_cards(self):
        """
        Test what happens when we don't have any of the required cards to pay out.
        """
        for (card_class, name, target_card_type, payout) in self.card_classes:
            with self.subTest(card=name):
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, 0)

    def test_hit_with_one_necessary_card(self):
        """
        Test what happens when we have a single card that matches.
        """
        for (card_class, name, target_card_type, payout) in self.card_classes:
            with self.subTest(card=name):
                self.player.add_card(target_card_type(self.game))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout)

    def test_hit_with_three_necessary_cards(self):
        """
        Test what happens when we have three cards that match.
        """
        for (card_class, name, target_card_type, payout) in self.card_classes:
            with self.subTest(card=name):
                for i in range(3):
                    self.player.add_card(target_card_type(self.game))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout*3)

    def test_hit_with_one_necessary_card_with_cup_bread_bonus(self):
        """
        Test what happens when we have a single card that matches, and the player
        has a cup/bread bonus.  The bonus should apply.
        """
        self.player.has_bread_cup_bonus = True
        for (card_class, name, target_card_type, payout) in self.card_classes:
            with self.subTest(card=name):
                self.player.add_card(target_card_type(self.game))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, payout+1)

    def test_hit_with_three_necessary_cards_with_cup_bread_bonus(self):
        """
        Test what happens when we have three cards that match, and the player
        has a cup/bread bonus.  The bonus should apply.
        """
        self.player.has_bread_cup_bonus = True
        for (card_class, name, target_card_type, payout) in self.card_classes:
            with self.subTest(card=name):
                for i in range(3):
                    self.player.add_card(target_card_type(self.game))
                card = card_class(self.game)
                self.player.add_card(card)
                self.player.money = 0
                card.hit(None)
                self.assertEqual(self.player.money, (payout*3)+1)

class CardTunaBoatTests(BaseCardTests):
    """
    Tests against the Tuna Boat.  Unaffected by cup/bread bonus, but requires a Harbor.
    """

    def setUp(self):
        """
        Setup methods.  Create a two players and a game, and add a TunaBoat and Harbor
        to each player.  Make the Harbors active by default, since that's what most
        of the tests will want.
        """
        self.player = Player(name='Player')
        self.player2 = Player(name='Player 2')
        self.game = Game([self.player, self.player2],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        self.card = cards.CardTunaBoat(self.game)
        self.player.add_card(self.card)

        self.card2 = cards.CardTunaBoat(self.game)
        self.player2.add_card(self.card2)

        self.landmark = cards.LandmarkHarbor()
        self.landmark.constructed = True
        self.player.landmarks.append(self.landmark)

        self.landmark2 = cards.LandmarkHarbor()
        self.landmark2.constructed = True
        self.player2.landmarks.append(self.landmark2)

        self.assertEqual(self.game.tuna_boat_roll, None)

    def test_without_required_landmark(self):
        """
        Test what happens when a tuna boat hits, without the required landmark.
        """
        self.landmark.constructed = False
        self.player.money = 0
        self.card.hit(None)
        self.assertEqual(self.game.tuna_boat_roll, None)
        self.assertEqual(self.player.money, 0)

    def test_with_required_landmark(self):
        """
        Test what happens when a tuna boat hits, with the required landmark.
        """
        self.player.money = 0
        self.card.hit(None)
        self.assertGreaterEqual(self.game.tuna_boat_roll, 2)
        self.assertLessEqual(self.game.tuna_boat_roll, 12)
        self.assertEqual(self.player.money, self.game.tuna_boat_roll)

    def test_with_required_landmark_and_cup_bread_bonus(self):
        """
        Test what happens when a tuna boat hits, with the required landmark and
        a cup/bread bonus.  The bonus should not apply, since the tuna boat
        isn't of the proper family.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        self.card.hit(None)
        self.assertGreaterEqual(self.game.tuna_boat_roll, 2)
        self.assertLessEqual(self.game.tuna_boat_roll, 12)
        self.assertEqual(self.player.money, self.game.tuna_boat_roll)

    def test_two_players_first_with_required_landmark(self):
        """
        Test what happens when a tuna boat hits for two consecutive players, the
        first with the required landmark but the second without.
        """
        self.player.money = 0
        self.player2.money = 0
        self.landmark2.constructed = False
        self.card.hit(None)
        self.assertGreaterEqual(self.game.tuna_boat_roll, 2)
        self.assertLessEqual(self.game.tuna_boat_roll, 12)
        self.assertEqual(self.player.money, self.game.tuna_boat_roll)
        orig_tuna_boat_roll = self.game.tuna_boat_roll
        self.card2.hit(None)
        # Potential for false positives here, of course.  c'est la vie...
        self.assertEqual(self.game.tuna_boat_roll, orig_tuna_boat_roll)
        self.assertEqual(self.player2.money, 0)

    def test_two_players_second_with_required_landmark(self):
        """
        Test what happens when a tuna boat hits for two consecutive players, the
        first without the required landmark but the second with.
        """
        self.player.money = 0
        self.player2.money = 0
        self.landmark.constructed = False
        self.card.hit(None)
        self.assertEqual(self.player.money, 0)
        self.assertEqual(self.game.tuna_boat_roll, None)
        self.card2.hit(None)
        self.assertGreaterEqual(self.game.tuna_boat_roll, 2)
        self.assertLessEqual(self.game.tuna_boat_roll, 12)
        self.assertEqual(self.player2.money, self.game.tuna_boat_roll)

    def test_two_players_both_with_required_landmark(self):
        """
        Test what happens when a tuna boat hits for two consecutive players, both
        with a Harbor.
        """
        self.player.money = 0
        self.player2.money = 0
        self.card.hit(None)
        self.assertGreaterEqual(self.game.tuna_boat_roll, 2)
        self.assertLessEqual(self.game.tuna_boat_roll, 12)
        self.assertEqual(self.player.money, self.game.tuna_boat_roll)
        orig_tuna_boat_roll = self.game.tuna_boat_roll
        self.card2.hit(None)
        # Potential for false positives here, of course.  c'est la vie...
        self.assertEqual(self.game.tuna_boat_roll, orig_tuna_boat_roll)
        self.assertEqual(self.player2.money, orig_tuna_boat_roll)

    def test_with_two_tuna_boats(self):
        """
        Test what happens when a tuna boat hits twice for the same player.
        """
        second_card = cards.CardTunaBoat(self.game)
        self.player.add_card(second_card)
        self.player.money = 0
        self.card.hit(None)
        self.assertGreaterEqual(self.game.tuna_boat_roll, 2)
        self.assertLessEqual(self.game.tuna_boat_roll, 12)
        self.assertEqual(self.player.money, self.game.tuna_boat_roll)
        orig_tuna_boat_roll = self.game.tuna_boat_roll
        second_card.hit(None)
        # Potential for false positives here, of course.  c'est la vie...
        self.assertEqual(self.game.tuna_boat_roll, orig_tuna_boat_roll)
        self.assertEqual(self.player.money, self.game.tuna_boat_roll*2)

class CardStadiumTests(BaseCardTests):
    """
    Tests against the Stadium.
    """

    def setUp(self):
        """
        Setup methods.  Create a three players and a game, and add a Stadium to the
        first.
        """
        self.player = Player(name='Player')
        self.player2 = Player(name='Player 2')
        self.player3 = Player(name='Player 3')
        self.game = Game([self.player, self.player2, self.player3],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        self.stadium = cards.CardStadium(self.game)
        self.player.add_card(self.stadium)

    def test_hit_with_sufficient_funds(self):
        """
        Tests what happens when a Stadium hits, and all other players have sufficient
        funds for it.
        """
        self.player.money = 0
        self.player2.money = 3
        self.player3.money = 3
        self.stadium.hit(None)
        self.assertEqual(self.player.money, 4)
        self.assertEqual(self.player2.money, 1)
        self.assertEqual(self.player3.money, 1)

    def test_hit_with_partial_funds(self):
        """
        Tests what happens when a Stadium hits, and all other players have partial
        funds for it.
        """
        self.player.money = 0
        self.player2.money = 1
        self.player3.money = 1
        self.stadium.hit(None)
        self.assertEqual(self.player.money, 2)
        self.assertEqual(self.player2.money, 0)
        self.assertEqual(self.player3.money, 0)

    def test_hit_with_no_funds(self):
        """
        Tests what happens when a Stadium hits, and all other players have no
        funds for it.
        """
        self.player.money = 3
        self.player2.money = 0
        self.player3.money = 0
        self.stadium.hit(None)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player2.money, 0)
        self.assertEqual(self.player3.money, 0)

    def test_hit_with_sufficient_funds_and_cup_bread_bonus(self):
        """
        Tests what happens when a Stadium hits, and all other players have sufficient
        funds for it.  Player has cup/bread bonus, but that shouldn't apply.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        self.player2.money = 3
        self.player3.money = 3
        self.stadium.hit(None)
        self.assertEqual(self.player.money, 4)
        self.assertEqual(self.player2.money, 1)
        self.assertEqual(self.player3.money, 1)

class CardTVStationTests(BaseCardTests):
    """
    Tests against the TV Station.
    """

    def setUp(self):
        """
        Setup methods.  Create three players and a game, and add a TV Station to the
        first.
        """
        self.player = Player(name='Player')
        self.player2 = Player(name='Player 2')
        self.player3 = Player(name='Player 3')
        self.game = Game([self.player, self.player2, self.player3],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        self.station = cards.CardTVStation(self.game)
        self.player.add_card(self.station)

    def test_hit_add_state_card(self):
        """
        Test to make sure that the TV Station adds itself to the game's list of state_cards.
        """
        self.assertEqual(self.game.state_cards, [])
        self.station.hit(None)
        self.assertEqual(self.game.state_cards, [self.station])

    def test_get_pending_actions(self):
        """
        Test to make sure that the card's get_pending_actions() function returns one
        for each other player
        """
        actions = self.station.get_pending_actions()
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].other_player, self.player2)
        self.assertEqual(actions[1].other_player, self.player3)

    def test_choose_player_with_sufficient_funds(self):
        """
        Test choosing a player who has sufficient funds.
        """
        self.player.money = 0
        self.player2.money = 6
        self.station.hit(None)
        self.assertEqual(self.game.state_cards, [self.station])
        self.station.chose_player(self.player2)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 1)
        self.assertEqual(self.game.state_cards, [])
        self.assertEqual(self.game.state, self.game.STATE_PURCHASE_DECISION)

    def test_choose_player_with_sufficient_funds_with_cup_bread_bonus(self):
        """
        Test choosing a player who has sufficient funds.  Player has cup/bread bonus,
        but that shouldn't change anything since it doesn't apply.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        self.player2.money = 6
        self.station.hit(None)
        self.assertEqual(self.game.state_cards, [self.station])
        self.station.chose_player(self.player2)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 1)
        self.assertEqual(self.game.state_cards, [])
        self.assertEqual(self.game.state, self.game.STATE_PURCHASE_DECISION)

    def test_choose_player_with_partial_funds(self):
        """
        Test choosing a player who has partial funds.
        """
        self.player.money = 0
        self.player2.money = 3
        self.station.hit(None)
        self.assertEqual(self.game.state_cards, [self.station])
        self.station.chose_player(self.player2)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player2.money, 0)
        self.assertEqual(self.game.state_cards, [])
        self.assertEqual(self.game.state, self.game.STATE_PURCHASE_DECISION)

    def test_choose_player_with_no_funds(self):
        """
        Test choosing a player who has no funds.
        """
        self.player.money = 3
        self.player2.money = 0
        self.station.hit(None)
        self.assertEqual(self.game.state_cards, [self.station])
        self.station.chose_player(self.player2)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player2.money, 0)
        self.assertEqual(self.game.state_cards, [])
        self.assertEqual(self.game.state, self.game.STATE_PURCHASE_DECISION)

class CardBusinessCenterTests(BaseCardTests):
    """
    Tests against the Business Center
    """

    def setUp(self):
        """
        Setup methods.  Create three players and a game, add a Business Center to the
        first, and some other cards to all three.  Also wipe out all players' starting
        inventories, so we've got a bit more control.  We'll also add two of the second
        "regular" card that players have.
        """
        self.player = Player(name='Player')
        self.player2 = Player(name='Player 2')
        self.player3 = Player(name='Player 3')
        self.game = Game([self.player, self.player2, self.player3],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        # Get rid of our default cards for the players, so we can control the tests
        # a little better without having to do weird special cases.
        for player in self.game.players:
            for card in list(player.deck):
                player.remove_card(card)

        # p1 will get: Wheat, Ranch x2, Business Center
        self.wheat = cards.CardWheat(self.game)
        self.player.add_card(self.wheat)
        self.ranch = cards.CardRanch(self.game)
        self.player.add_card(self.ranch)
        self.ranch2 = cards.CardRanch(self.game)
        self.player.add_card(self.ranch2)
        self.center = cards.CardBusinessCenter(self.game)
        self.player.add_card(self.center)

        # p2 will get: Bakery, Cafe x2, Stadium
        self.bakery = cards.CardBakery(self.game)
        self.player2.add_card(self.bakery)
        self.cafe = cards.CardCafe(self.game)
        self.player2.add_card(self.cafe)
        self.cafe2 = cards.CardCafe(self.game)
        self.player2.add_card(self.cafe2)
        self.stadium = cards.CardStadium(self.game)
        self.player2.add_card(self.stadium)

        # p3 will get: Forest, Mine x2, TV Station
        self.forest = cards.CardForest(self.game)
        self.player3.add_card(self.forest)
        self.mine = cards.CardMine(self.game)
        self.player3.add_card(self.mine)
        self.mine2 = cards.CardMine(self.game)
        self.player3.add_card(self.mine2)
        self.station = cards.CardTVStation(self.game)
        self.player3.add_card(self.station)

    def test_hit_add_state_card(self):
        """
        Test to make sure that the Business Center adds itself to the game's list of state_cards.
        """
        self.assertEqual(self.game.state_cards, [])
        self.center.hit(None)
        self.assertEqual(self.game.state_cards, [self.center])
        self.assertEqual(self.center.trade_owner, None)
        self.assertEqual(self.center.trade_other, None)

    def test_get_pending_actions(self):
        """
        Test to make sure that the card's get_pending_actions() function returns:
            1) One action for each other player's card, minus any major establishments
            2) One action for each of OUR cards, minus any major establishments
        """
        actions = self.center.get_pending_actions()
        self.assertEqual(len(actions), 6)

        own_targets = []
        other_targets = []
        for action in actions:
            if type(action) == actionlib.ActionChooseOwnCard:
                own_targets.append(action.chosen_card)
            elif type(action) == actionlib.ActionChooseOtherCard:
                other_targets.append(action.chosen_card)
            else:
                self.fail('Unknown action type found: %d' % (type(action)))
        self.assertEqual(len(own_targets), 2)
        self.assertEqual(len(other_targets), 4)
        # We're doing some nonsense with type() here because I don't want to rely
        # on which one of our doubled-card objects we get.  The current implementation
        # would give us the first one added to the player deck, but that could end
        # up changing eventually.
        self.assertEqual(
            [type(x) for x in sorted(own_targets)],
            [type(x) for x in [self.wheat, self.ranch]],
        )
        self.assertEqual(
            [type(x) for x in sorted(other_targets)],
            [type(x) for x in [self.bakery, self.cafe, self.forest, self.mine]],
        )

    def test_choose_own_card(self):
        """
        Test what happens when you choose one of your own cards.  Basically should only set
        a single internal var.
        """
        self.center.hit(None)
        self.center.chose_own_card(self.wheat)
        self.assertEqual(self.center.trade_owner, self.wheat)
        self.assertEqual(self.center.trade_other, None)
        self.assertEqual(self.game.state_cards, [self.center])

    def test_choose_own_card_invalid(self):
        """
        Test what happens when you choose one of your own cards which isn't actually a card
        you own.  Should raise an Exception
        """
        self.center.hit(None)
        with self.assertRaises(Exception):
            self.center.chose_own_card(self.bakery)

    def test_choose_own_card_invalid_major_establishment(self):
        """
        Test what happens when you choose one of your own cards which is a major establishment.
        Should raise an Exception.
        """
        self.center.hit(None)
        with self.assertRaises(Exception):
            self.center.chose_own_card(self.center)

    def test_choose_own_card_twice(self):
        """
        Test what happens when you choose one of your own cards but then change your mind.
        Basically should only set a single internal var.
        """
        self.center.hit(None)
        self.center.chose_own_card(self.wheat)
        self.assertEqual(self.center.trade_owner, self.wheat)
        self.assertEqual(self.center.trade_other, None)
        self.assertEqual(self.game.state_cards, [self.center])
        self.center.chose_own_card(self.ranch)
        self.assertEqual(self.center.trade_owner, self.ranch)
        self.assertEqual(self.center.trade_other, None)
        self.assertEqual(self.game.state_cards, [self.center])

    def test_choose_other_card(self):
        """
        Test what happens when you choose one of someone else's cards.  Basically should only set
        a single internal var.
        """
        self.center.hit(None)
        self.center.chose_other_card(self.bakery)
        self.assertEqual(self.center.trade_other, self.bakery)
        self.assertEqual(self.center.trade_owner, None)
        self.assertEqual(self.game.state_cards, [self.center])

    def test_choose_other_card_invalid(self):
        """
        Test what happens when you choose one of someone else's cards which is actually a card YOU
        own.  Should raise an Exception
        """
        self.center.hit(None)
        with self.assertRaises(Exception):
            self.center.chose_other_card(self.wheat)

    def test_choose_other_card_invalid_major_establishment(self):
        """
        Test what happens when you choose one of someone else's cards which is a major establishment.
        Should raise an Exception
        """
        self.center.hit(None)
        with self.assertRaises(Exception):
            self.center.chose_other_card(self.station)

    def test_choose_other_card_invalid_broken_internal_structure(self):
        """
        Test what happens when you choose one of someone else's cards which isn't actually a card
        they own (though nor is it yours).  This really shouldn't be possible; we have to purposefully
        break the internal structure in order to get this to trigger.  Should raise an Exception
        """
        self.center.hit(None)
        self.player2.deck.remove(self.bakery)
        with self.assertRaises(Exception):
            self.center.chose_other_card(self.bakery)

    def test_choose_other_card_twice(self):
        """
        Test what happens when you choose one of someone else's cards but then change your mind.
        Basically should only set a single internal var.
        """
        self.center.hit(None)
        self.center.chose_other_card(self.bakery)
        self.assertEqual(self.center.trade_other, self.bakery)
        self.assertEqual(self.center.trade_owner, None)
        self.assertEqual(self.game.state_cards, [self.center])
        self.center.chose_other_card(self.cafe)
        self.assertEqual(self.center.trade_other, self.cafe)
        self.assertEqual(self.center.trade_owner, None)
        self.assertEqual(self.game.state_cards, [self.center])

    def test_perform_trade_no_duplicates(self):
        """
        Test to make sure that a trade can happen properly.  First up, with no duplicate cards
        in play.
        """
        self.center.hit(None)
        self.center.chose_own_card(self.wheat)
        self.center.chose_other_card(self.bakery)
        # More type() trickery here so we're not relying on internal deck implementation.  In
        # particular I'm not positive that we can rely on the double-ranches and double-cafes
        # to remain sorted the way I have them listed (though for now it'd have been fine do
        # do without)
        self.assertEqual(
            [type(x) for x in sorted(self.player.deck)],
            [type(x) for x in [self.ranch, self.ranch2, self.bakery, self.center]]
        )
        self.assertEqual(
            [type(x) for x in sorted(self.player2.deck)],
            [type(x) for x in [self.wheat, self.cafe, self.cafe2, self.stadium]]
        )
        self.assertEqual(self.game.state_cards, [])
        self.assertEqual(self.game.state, self.game.STATE_PURCHASE_DECISION)

    def test_perform_trade_with_duplicates(self):
        """
        Test to make sure that a trade can happen properly.  First up, trading cards which
        have duplicates.
        """
        self.center.hit(None)
        self.center.chose_own_card(self.ranch)
        self.center.chose_other_card(self.cafe)
        # More type() trickery here so we're not relying on internal deck implementation.
        self.assertEqual(
            [type(x) for x in sorted(self.player.deck)],
            [type(x) for x in [self.wheat, self.ranch2, self.cafe, self.center]]
        )
        self.assertEqual(
            [type(x) for x in sorted(self.player2.deck)],
            [type(x) for x in [self.ranch, self.bakery, self.cafe2, self.stadium]]
        )
        self.assertEqual(self.game.state_cards, [])
        self.assertEqual(self.game.state, self.game.STATE_PURCHASE_DECISION)

class CardPublisherTests(BaseCardTests):
    """
    Tests against the Publisher
    """

    def setUp(self):
        """
        Setup methods.  Create four players and a game, and add a Publisher to the
        first, an extra bakery and cafe to the second, and a cafe to the third.
        Wipe the inventory of the fourth completely.
        """
        self.player = Player(name='Player')
        self.player2 = Player(name='Player 2')
        self.player3 = Player(name='Player 3')
        self.player4 = Player(name='Player 4')
        self.game = Game([self.player, self.player2, self.player3, self.player4],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        self.publisher = cards.CardPublisher(self.game)
        self.player.add_card(self.publisher)

        self.player2.add_card(cards.CardBakery(self.game))
        self.player2.add_card(cards.CardCafe(self.game))

        self.player3.add_card(cards.CardCafe(self.game))

        for card in list(self.player4.deck):
            self.player4.remove_card(card)

    def test_hit_with_sufficient_funds(self):
        """
        Test a Publisher hit when all other players have sufficient funds to pay out.
        """

        self.player.money = 0
        self.player2.money = 4
        self.player3.money = 3
        self.player4.money = 3
        self.publisher.hit(None)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 1)
        self.assertEqual(self.player3.money, 1)
        self.assertEqual(self.player4.money, 3)

    def test_hit_with_sufficient_funds_and_cup_bread_bonus(self):
        """
        Test a Publisher hit when all other players have sufficient funds to pay out.
        Cup/Bread bonus is active but should not alter the result.
        """

        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        self.player2.money = 4
        self.player3.money = 3
        self.player4.money = 3
        self.publisher.hit(None)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 1)
        self.assertEqual(self.player3.money, 1)
        self.assertEqual(self.player4.money, 3)

    def test_hit_with_partial_funds(self):
        """
        Test a Publisher hit when all other players have partial funds to pay out.
        """

        self.player.money = 0
        self.player2.money = 2
        self.player3.money = 1
        self.player4.money = 3
        self.publisher.hit(None)
        self.assertEqual(self.player.money, 3)
        self.assertEqual(self.player2.money, 0)
        self.assertEqual(self.player3.money, 0)
        self.assertEqual(self.player4.money, 3)

    def test_hit_with_no_funds(self):
        """
        Test a Publisher hit when no other players have any funds.
        """

        self.player.money = 2
        self.player2.money = 0
        self.player3.money = 0
        self.player4.money = 3
        self.publisher.hit(None)
        self.assertEqual(self.player.money, 2)
        self.assertEqual(self.player2.money, 0)
        self.assertEqual(self.player3.money, 0)
        self.assertEqual(self.player4.money, 3)

class CardTaxOfficeTests(BaseCardTests):
    """
    Tests against the Tax Office
    """

    def setUp(self):
        """
        Setup methods.  Create two players and a game, and add a Tax Office to the
        first.
        """
        self.player = Player(name='Player')
        self.player2 = Player(name='Player 2')
        self.game = Game([self.player, self.player2],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)

        self.office = cards.CardTaxOffice(self.game)
        self.player.add_card(self.office)

    def test_hit_with_sufficient_funds(self):
        """
        Test a hit when a player has at least ten coins.
        """
        self.player.money = 0
        self.player2.money = 10
        self.office.hit(None)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 5)

    def test_hit_with_sufficient_funds_and_cup_bread_bonus(self):
        """
        Test a hit when a player has at least ten coins.  The player has a cup/bread
        bonus but that shouldn't change anything.
        """
        self.player.has_bread_cup_bonus = True
        self.player.money = 0
        self.player2.money = 10
        self.office.hit(None)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 5)

    def test_hit_with_insufficient_funds(self):
        """
        Test a hit when a player only has 9 coins.
        """
        self.player.money = 0
        self.player2.money = 9
        self.office.hit(None)
        self.assertEqual(self.player.money, 0)
        self.assertEqual(self.player2.money, 9)

    def test_hit_with_odd_funds(self):
        """
        Test a hit when a player has an odd number of coins - should round down.
        """
        self.player.money = 0
        self.player2.money = 11
        self.office.hit(None)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player2.money, 6)

class LandmarkTests(unittest.TestCase):
    """
    Tests for our basic Landmark class
    """

    def create_landmark(self, name, player=None, desc=None, short_desc=None,
            cost=2, can_deconstruct=True, starts_constructed=False):
        """
        Helper app so we can pretend that more fields are optional than actually
        are.
        """
        return cards.Landmark(
            name=name,
            player=player,
            desc=desc,
            short_desc=short_desc,
            cost=cost,
            can_deconstruct=can_deconstruct,
            starts_constructed=starts_constructed)

    def test_repr_name(self):
        """
        repr() of a Landmark should result in its name
        """
        l = self.create_landmark(name='Landmark Name')
        self.assertEqual(repr(l), 'Landmark Name')

    def test_sort_cost(self):
        """
        Landmarks should be sorted by cost.
        """
        l1 = self.create_landmark(name='Cheap Landmark', cost=1)
        l2 = self.create_landmark(name='Expensive Landmark', cost=60)
        self.assertEqual(sorted([l2, l1]), [l1, l2])

    def test_unimplemented_construction(self):
        """
        Trying to construct an unimplemented Landmark should throw an exception
        """
        l1 = self.create_landmark(name='Landmark')
        with self.assertRaises(Exception):
            l1.construct()

    def test_unimplemented_deconstruction(self):
        """
        Trying to deconstruct an unimplemented Landmark should throw an exception
        """
        l1 = self.create_landmark(name='Landmark')
        with self.assertRaises(Exception):
            l1.deconstruct()

    def test_starts_unconstructed(self):
        """
        Generally, landmarks should start unconstructed
        """
        l = self.create_landmark(name='Landmark')
        self.assertEqual(l.constructed, False)

    def test_starts_constructed(self):
        """
        Some landmarks start constructed, though.  This should raise an Exception
        on our unimplemented base class, though.
        """
        with self.assertRaises(Exception):
            l = self.create_landmark(name='Landmark', starts_constructed=True)

class NamedLandmarkTests(unittest.TestCase):
    """
    Tests for our various named landmarks.
    """

    start_constructed = [
        cards.LandmarkCityHall,
    ]
    start_unconstructed = [
        cards.LandmarkHarbor,
        cards.LandmarkTrainStation,
        cards.LandmarkShoppingMall,
        cards.LandmarkAmusementPark,
        cards.LandmarkRadioTower,
        cards.LandmarkAirport,
    ]

    def setUp(self):
        """
        These tests will require a Player object, so create one.
        """
        self.player = Player(name='Player')
        self.assertEqual(self.player.coin_if_broke, False)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, False)
        self.assertEqual(self.player.can_roll_two_dice, False)
        self.assertEqual(self.player.has_bread_cup_bonus, False)
        self.assertEqual(self.player.extra_turn_on_doubles, False)
        self.assertEqual(self.player.can_reroll_once, False)
        self.assertEqual(self.player.gets_ten_coins_for_not_building, False)

    def test_starts_constructed(self):
        """
        Tests for all our landmarks which are supposed to start constructed
        """
        for l_type in self.start_constructed:
            with self.subTest(landmark=l_type):
                l = l_type(self.player)
                self.assertEqual(l.constructed, True)

    def test_starts_unconstructed(self):
        """
        Tests for all our landmarks which are supposed to start unconstructed
        """
        for l_type in self.start_unconstructed:
            with self.subTest(landmark=l_type):
                l = l_type(self.player)
                self.assertEqual(l.constructed, False)

    def test_construct_cityhall(self):
        """
        Tests City Hall construction
        """
        l = cards.LandmarkCityHall(self.player)
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.coin_if_broke, l)

    def test_deconstruct_cityhall(self):
        """
        Tests City Hall deconstruction - Nothing should happen (since this one can't
        be deconstructed)
        """
        l = cards.LandmarkCityHall(self.player)
        l.deconstruct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.coin_if_broke, l)

    def test_construct_harbor(self):
        """
        Harbor construction
        """
        l = cards.LandmarkHarbor(self.player)
        l.construct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, l)

    def test_deconstruct_harbor(self):
        """
        Harbor deconstruction
        """
        l = cards.LandmarkHarbor(self.player)
        l.construct()
        l.deconstruct()
        self.assertEqual(l.constructed, False)
        self.assertEqual(self.player.dice_add_to_ten_or_higher, False)

    def test_construct_train_station(self):
        """
        Train Station construction
        """
        l = cards.LandmarkTrainStation(self.player)
        l.construct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.can_roll_two_dice, l)

    def test_deconstruct_train_station(self):
        """
        Train Station deconstruction
        """
        l = cards.LandmarkTrainStation(self.player)
        l.construct()
        l.deconstruct()
        self.assertEqual(l.constructed, False)
        self.assertEqual(self.player.can_roll_two_dice, False)

    def test_construct_shopping_mall(self):
        """
        Shopping Mall construction
        """
        l = cards.LandmarkShoppingMall(self.player)
        l.construct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.has_bread_cup_bonus, l)

    def test_deconstruct_shopping_mall(self):
        """
        Shopping Mall deconstruction
        """
        l = cards.LandmarkShoppingMall(self.player)
        l.construct()
        l.deconstruct()
        self.assertEqual(l.constructed, False)
        self.assertEqual(self.player.has_bread_cup_bonus, False)

    def test_construct_amusement_park(self):
        """
        Amusement Park construction
        """
        l = cards.LandmarkAmusementPark(self.player)
        l.construct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.extra_turn_on_doubles, l)

    def test_deconstruct_amusement_park(self):
        """
        Amusement Park deconstruction
        """
        l = cards.LandmarkAmusementPark(self.player)
        l.construct()
        l.deconstruct()
        self.assertEqual(l.constructed, False)
        self.assertEqual(self.player.extra_turn_on_doubles, False)

    def test_construct_radio_tower(self):
        """
        Radio Tower construction
        """
        l = cards.LandmarkRadioTower(self.player)
        l.construct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.can_reroll_once, l)

    def test_deconstruct_radio_tower(self):
        """
        Radio Tower deconstruction
        """
        l = cards.LandmarkRadioTower(self.player)
        l.construct()
        l.deconstruct()
        self.assertEqual(l.constructed, False)
        self.assertEqual(self.player.can_reroll_once, False)

    def test_construct_airport(self):
        """
        Airport construction
        """
        l = cards.LandmarkAirport(self.player)
        l.construct()
        self.assertEqual(l.constructed, True)
        self.assertEqual(self.player.gets_ten_coins_for_not_building, l)

    def test_deconstruct_airport(self):
        """
        Airport deconstruction
        """
        l = cards.LandmarkAirport(self.player)
        l.construct()
        l.deconstruct()
        self.assertEqual(l.constructed, False)
        self.assertEqual(self.player.gets_ten_coins_for_not_building, False)

class ExpansionTests(unittest.TestCase):
    """
    Tests for our Expansion objects.
    """

    def setUp(self):
        """
        Create a couple Expansion objects we can use throughout these tests.
        """
        self.e1 = cards.Expansion(
            name='One',
            deck_regular=[(6, cards.CardWheat)],
            deck_major=[cards.CardStadium],
            landmarks=[cards.LandmarkHarbor],
            )
        self.e2 = cards.Expansion(
            name='Two',
            deck_regular=[(6, cards.CardBakery)],
            deck_major=[cards.CardTVStation],
            landmarks=[cards.LandmarkAirport],
            )

    def test_addition(self):
        """
        Tests adding two Expansion objects to each other.
        """
        e = self.e1 + self.e2
        self.assertEqual(e.name, 'One + Two')
        self.assertEqual(e.deck_regular, [(6, cards.CardWheat), (6, cards.CardBakery)])
        self.assertEqual(e.deck_major, [cards.CardStadium, cards.CardTVStation])
        self.assertEqual(e.landmarks, [cards.LandmarkHarbor, cards.LandmarkAirport])

    def test_generate_deck_two_players(self):
        """
        Generate a deck based on two players.  Some of our data structures here are
        a little wonky since we're trying to isolate the generate_deck() function,
        which would otherwise get called automatically during Game() initialization.
        """
        game = Game([Player(name='One'), Player(name='Two')],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)
        deck = self.e1.generate_deck(game)
        self.assertEqual(
            [type(x) for x in sorted(deck)],
            [cards.CardWheat, cards.CardWheat, cards.CardWheat,
                cards.CardWheat, cards.CardWheat, cards.CardWheat,
                cards.CardStadium, cards.CardStadium]
        )

    def test_generate_deck_three_players(self):
        """
        Generate a deck based on three players.  Some of our data structures here are
        a little wonky since we're trying to isolate the generate_deck() function,
        which would otherwise get called automatically during Game() initialization.
        """
        game = Game([Player(name='One'), Player(name='Two'), Player(name='Three')],
                cards.Expansion(name='empty',
                    deck_regular=[],
                    deck_major=[],
                    landmarks=[]),
                MarketBase)
        deck = self.e1.generate_deck(game)
        self.assertEqual(
            [type(x) for x in sorted(deck)],
            [cards.CardWheat, cards.CardWheat, cards.CardWheat,
                cards.CardWheat, cards.CardWheat, cards.CardWheat,
                cards.CardStadium, cards.CardStadium, cards.CardStadium]
        )
