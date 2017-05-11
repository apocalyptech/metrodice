#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import math
import random

from . import game as gamelib

class Card(object):
    """
    Class describing a generic card.  Actual rules will be implemented
    in subclasses.
    """

    (COLOR_BLUE,
        COLOR_GREEN,
        COLOR_RED,
        COLOR_PURPLE) = range(4)

    ENG_COLOR = {
            COLOR_BLUE: 'Blue',
            COLOR_GREEN: 'Green',
            COLOR_RED: 'Red',
            COLOR_PURPLE: 'Purple',
        }

    (FAMILY_WHEAT,
        FAMILY_COW,
        FAMILY_GEAR,
        FAMILY_BREAD,
        FAMILY_FACTORY,
        FAMILY_FRUIT,
        FAMILY_CUP,
        FAMILY_MAJOR,
        FAMILY_BOAT) = range(9)

    ENG_FAMILY = {
            FAMILY_WHEAT: 'Wheat',
            FAMILY_COW: 'Cow',
            FAMILY_GEAR: 'Gear',
            FAMILY_BREAD: 'Bread',
            FAMILY_FACTORY: 'Factory',
            FAMILY_FRUIT: 'Fruit',
            FAMILY_CUP: 'Cup',
            FAMILY_MAJOR: 'Major Establishment',
            FAMILY_BOAT: 'Boat',
        }

    def __init__(self, game, name, desc, short_desc, color, family, cost, activations):
        self.game = game
        self.name = name
        self.desc = desc
        self.short_desc = short_desc
        self.cost = cost
        self.family = family
        self.activations = activations
        self.color = color
        self.owner = None

    def __lt__(self, other):
        """
        Comparator operator, for sorting
        """

        # First the easy one - compare our first activation number
        if self.activations[0] < other.activations[0]:
            return True
        if self.activations[0] > other.activations[0]:
            return False

        # At this point we know that the first number is the same; sort
        # ranges after singles
        if len(self.activations) < len(other.activations):
            return True
        if len(self.activations) > len(other.activations):
            return False

        # Finally, the only other tiebreaker should be card color.
        # Our sort order here will actually be determined by the order
        # the colors are defined in, above.
        return (self.color < other.color)

    def __repr__(self):
        return self.name

    def color_str(self):
        return self.ENG_COLOR[self.color]

    def family_str(self):
        return self.ENG_FAMILY[self.family]

    def required_landmark(self):
        return None

    def hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled).
        This is mostly a wrapper for any prerequisites which may exist.
        """
        if self.required_landmark() is not None:
            if not self.owner.has_landmark(self.required_landmark()):
                return
        return self._hit(player_rolled)

    def _hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled)
        """
        raise Exception('Not implemented!')

    def does_bread_cup_bonus_apply(self):
        """
        Does a bread+cup bonus (from Shopping Mall) apply?
        """
        if self.owner.has_bread_cup_bonus and (self.family == Card.FAMILY_BREAD or self.family == Card.FAMILY_CUP):
            return True
        else:
            return False

class CardBasicPayout(Card):
    """
    A "basic" card which just has a simple payout.
    """

    def __init__(self, game, name, desc, short_desc, color, family, cost, payout, activations):
        self.payout = payout
        super(CardBasicPayout, self).__init__(
            game=game,
            name=name,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
        )

    def _hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled).
        """
        to_pay = self.payout
        if self.does_bread_cup_bonus_apply():
            to_pay += 1
        self.owner.money += to_pay
        self.game.add_event('Player "%s" received %d coins for a %s (new total: %d)' % (self.owner, to_pay, self, self.owner.money))

class CardFactoryFamily(Card):
    """
    A "factory" card whose payout depends on other card families you have
    """

    def __init__(self, game, name, desc, short_desc, color, family, cost, target_family, payout, activations):
        self.target_family = target_family
        self.payout = payout
        super(CardFactoryFamily, self).__init__(
            game=game,
            name=name,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
        )

    def _hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled).
        """
        num_matches = 0
        for card in self.owner.deck:
            if card.family == self.target_family:
                num_matches += 1
        to_pay = self.payout * num_matches
        if self.does_bread_cup_bonus_apply():
            to_pay += 1
        if to_pay > 0:
            self.owner.money += to_pay
            self.game.add_event('Player "%s" received %d coins for a %s (new total: %d)' % (self.owner, to_pay, self, self.owner.money))

class CardFactoryCard(Card):
    """
    A "factory" card whose payout depends on other card types you have.  Very similar
    to CardFactoryFamily.
    """

    def __init__(self, game, name, desc, short_desc, color, family, cost, target_card, payout, activations):
        self.target_card_type = type(target_card)
        self.payout = payout
        super(CardFactoryCard, self).__init__(
            game=game,
            name=name,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
        )

    def _hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled).
        """
        num_matches = 0
        for card in self.owner.deck:
            if type(card) == self.target_card_type:
                num_matches += 1
        to_pay = self.payout * num_matches
        if self.does_bread_cup_bonus_apply():
            to_pay += 1
        if to_pay > 0:
            self.owner.money += to_pay
            self.game.add_event('Player "%s" received %d coins for a %s (new total: %d)' % (self.owner, to_pay, self, self.owner.money))

class CardBasicRed(Card):
    """
    A "basic" red card which just has a simple fee.
    """

    def __init__(self, game, name, desc, short_desc, color, family, cost, fee, activations):
        self.fee = fee
        super(CardBasicRed, self).__init__(
            game=game,
            name=name,
            desc=desc,
            short_desc=short_desc,
            color=color,
            family=family,
            cost=cost,
            activations=activations,
        )

    def _hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled).
        """
        to_steal = self.fee
        if self.does_bread_cup_bonus_apply():
            to_steal += 1
        to_steal = min(to_steal, player_rolled.money)
        if to_steal > 0:
            self.owner.money += to_steal
            player_rolled.money -= to_steal
            self.game.add_event('Player "%s" received %d coins from "%s" from a %s (new total: %d)' % (self.owner, to_steal, player_rolled, self, self.owner.money))

class CardWheat(CardBasicPayout):

    def __init__(self, game):
        super(CardWheat, self).__init__(
            game=game,
            name='Wheat',
            desc="Get 1 coin from the bank, on anyone's turn.",
            short_desc='1 coin',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_WHEAT,
            cost=1,
            payout=1,
            activations=[1],
        )

class CardRanch(CardBasicPayout):

    def __init__(self, game):
        super(CardRanch, self).__init__(
            game=game,
            name='Ranch',
            desc="Get 1 coin from the bank, on anyone's turn.",
            short_desc='1 coin',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_COW,
            cost=1,
            payout=1,
            activations=[2],
        )

class CardBakery(CardBasicPayout):

    def __init__(self, game):
        super(CardBakery, self).__init__(
            game=game,
            name='Bakery',
            desc="Get 1 coin from the bank, on your turn only.",
            short_desc='1 coin',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_BREAD,
            cost=1,
            payout=1,
            activations=[2,3],
        )

class CardCafe(CardBasicRed):

    def __init__(self, game):
        super(CardCafe, self).__init__(
            game=game,
            name='Café',
            desc="Get 1 coin from the player who rolled the dice.",
            short_desc='1 coin',
            color=Card.COLOR_RED,
            family=Card.FAMILY_CUP,
            cost=2,
            fee=1,
            activations=[3],
        )

class CardConvenienceStore(CardBasicPayout):

    def __init__(self, game):
        super(CardConvenienceStore, self).__init__(
            game=game,
            name='Convenience Store',
            desc="Get 3 coins from the bank, on your turn only.",
            short_desc='3 coins',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_BREAD,
            cost=2,
            payout=3,
            activations=[4],
        )

class CardForest(CardBasicPayout):

    def __init__(self, game):
        super(CardForest, self).__init__(
            game=game,
            name='Forest',
            desc="Get 1 coin from the bank, on anyone's turn.",
            short_desc='1 coin',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_GEAR,
            cost=3,
            payout=1,
            activations=[5],
        )

class CardStadium(Card):

    def __init__(self, game):
        super(CardStadium, self).__init__(
            game=game,
            name='Stadium',
            desc="Get 2 coin from all players, on your turn only.",
            short_desc='2 coins/player',
            color=Card.COLOR_PURPLE,
            family=Card.FAMILY_MAJOR,
            cost=6,
            activations=[6],
        )

    def _hit(self, player_rolled):
        """
        Two coins from all players!
        """
        for player in self.game.players:
            if player != self.owner:
                to_steal = min(2, player.money)
                if to_steal > 0:
                    self.owner.money += to_steal
                    player.money -= to_steal
                    self.game.add_event('Player "%s" received %d coins from "%s" from a %s (new total: %d)' % (self.owner, to_steal, player, self, self.owner.money))

class CardTVStation(Card):

    def __init__(self, game):
        super(CardTVStation, self).__init__(
            game=game,
            name='TV Station',
            desc="If this is your turn, take 5 coins from any one player.",
            short_desc='5 coins/1 player',
            color=Card.COLOR_PURPLE,
            family=Card.FAMILY_MAJOR,
            cost=7,
            activations=[6],
        )

    def _hit(self, player_rolled):
        """
        Five coins from a single player
        """
        self.game.add_state_card(self)

    def get_pending_actions(self):
        """
        Gets a list of pending actions for this card
        """
        actions = []
        for player in self.game.players:
            if player != self.owner:
                actions.append(gamelib.ActionChoosePlayer(self.owner, self.game, self, player))
        return actions

    def chose_player(self, action, other_player):
        """
        The user chose a player to steal from
        """
        to_steal = min(5, other_player.money)
        if to_steal > 0:
            self.owner.money += to_steal
            other_player.money -= to_steal
            self.game.add_event('Player "%s" received %d coins from "%s" from a %s (new total: %d)' % (self.owner, to_steal, other_player, self, self.owner.money))
        self.game.remove_state_card(self)
        self.game.finish_roll()

class CardBusinessCenter(Card):

    def __init__(self, game):
        super(CardBusinessCenter, self).__init__(
            game=game,
            name='Buiness Center',
            desc="If this is your turn, trade one non [Major] establishment with another player.",
            short_desc='trade cards',
            color=Card.COLOR_PURPLE,
            family=Card.FAMILY_MAJOR,
            cost=8,
            activations=[6],
        )
        self.trade_owner = None
        self.trade_other = None

    def _hit(self, player_rolled):
        """
        Trade some cards!
        """
        self.trade_owner = None
        self.trade_other = None
        self.game.add_state_card(self)

    def get_pending_actions(self):
        """
        Gets a list of pending actions for this card
        """
        actions = []

        if self.trade_owner is None:
            seen_types = {}
            for card in self.owner.deck:
                if card.family != Card.FAMILY_MAJOR and type(card) not in seen_types:
                    actions.append(gamelib.ActionChooseOwnCard(self.owner, self.game, self, card))
                seen_types[type(card)] = True

        if self.trade_other is None:
            for player in self.game.players:
                if player != self.owner:
                    seen_types = {}
                    for card in player.deck:
                        if card.family != Card.FAMILY_MAJOR and type(card) not in seen_types:
                            actions.append(gamelib.ActionChooseOtherCard(self.owner, self.game, self, card))
                        seen_types[type(card)] = True

        return actions

    def chose_own_card(self, action, trade_owner):
        """
        The user chose a player to steal from
        """
        self.game.add_event('Chose your own "%s" card for trade (from %s)' % (trade_owner, self))
        self.trade_owner = trade_owner
        self.check_finished()

    def chose_other_card(self, action, trade_other):
        """
        The user chose a player to steal from
        """
        self.game.add_event('Chose %s\'s card "%s" card for trade (from %s)' % (trade_other.owner, trade_other, self))
        self.trade_other = trade_other
        self.check_finished()

    def check_finished(self):
        """
        Check to see if we've got a from/to
        """
        if self.trade_owner is not None and self.trade_other is not None:

            # Report, before we actually do the work.
            self.game.add_event('%s traded card "%s" for %s\'s card "%s"' % (self.owner, self.trade_owner,
                self.trade_other.owner, self.trade_other))

            # Move our own card to the other person's inventory
            self.trade_other.owner.add_card(self.trade_owner)

            # Move the other person's card to our inventory
            self.owner.add_card(self.trade_other)

            # And finish up.
            self.game.remove_state_card(self)
            self.game.finish_roll()

class CardCheeseFactory(CardFactoryFamily):

    def __init__(self, game):
        super(CardCheeseFactory, self).__init__(
            game=game,
            name='Cheese Factory',
            desc="If this is your turn, get 3 coins from the bank for each [Cow] establishment that you own.",
            short_desc='3 coins/cow',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_FACTORY,
            cost=5,
            target_family=Card.FAMILY_COW,
            payout=3,
            activations=[7],
        )

class CardFurnitureFactory(CardFactoryFamily):

    def __init__(self, game):
        super(CardFurnitureFactory, self).__init__(
            game=game,
            name='Furniture Factory',
            desc="If this is your turn, get 3 coins from the bank for each [Gear] establishment that you own.",
            short_desc='3 coins/gear',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_FACTORY,
            cost=3,
            target_family=Card.FAMILY_GEAR,
            payout=3,
            activations=[8],
        )

class CardFruitAndVeg(CardFactoryFamily):

    def __init__(self, game):
        super(CardFruitAndVeg, self).__init__(
            game=game,
            name='Fruit and Vegetable Market',
            desc="If this is your turn, get 2 coins from the bank for each [Wheat] establishment that you own.",
            short_desc='2 coins/wheat',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_FRUIT,
            cost=2,
            target_family=Card.FAMILY_WHEAT,
            #payout=10,
            #activations=list(range(1,13)),
            payout=2,
            activations=[11,12],
        )

class CardMine(CardBasicPayout):

    def __init__(self, game):
        super(CardMine, self).__init__(
            game=game,
            name='Mine',
            desc="Get 5 coins from the bank, on anyone's turn.",
            short_desc='5 coins',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_GEAR,
            cost=6,
            payout=5,
            activations=[9],
        )

class CardFamilyRestaurant(CardBasicRed):

    def __init__(self, game):
        super(CardFamilyRestaurant, self).__init__(
            game=game,
            name='Family Restaurant',
            desc="Get 2 coins from the player who rolled the dice.",
            short_desc='2 coins',
            color=Card.COLOR_RED,
            family=Card.FAMILY_CUP,
            cost=3,
            fee=2,
            activations=[9,10],
        )

class CardAppleOrchard(CardBasicPayout):

    def __init__(self, game):
        super(CardAppleOrchard, self).__init__(
            game=game,
            name='Apple Orchard',
            desc="Get 3 coins from the bank, on anyone's turn.",
            short_desc='3 coins',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_WHEAT,
            cost=3,
            payout=3,
            activations=[10],
        )

class CardSushiBar(CardBasicRed):

    def __init__(self, game):
        super(CardSushiBar, self).__init__(
            game=game,
            name='Sushi Bar',
            desc="If you have a harbor, you get 3 coins from the player who rolled the dice.",
            short_desc='w/ harbor, 3 coins',
            color=Card.COLOR_RED,
            family=Card.FAMILY_CUP,
            cost=4,
            fee=3,
            activations=[1],
        )

    def required_landmark(self):
        return LandmarkHarbor()

class CardFlowerOrchard(CardBasicPayout):

    def __init__(self, game):
        super(CardFlowerOrchard, self).__init__(
            game=game,
            name='Flower Orchard',
            desc="Get 1 coin from the bank, on anyone's turn.",
            short_desc='1 coin',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_WHEAT,
            cost=2,
            payout=1,
            activations=[4],
        )

class CardFlowerShop(CardFactoryCard):

    def __init__(self, game):
        super(CardFlowerShop, self).__init__(
            game=game,
            name='Flower Shop',
            desc='Get 1 coin from the bank for each Flower Orchard you own, on your turn only.',
            short_desc='1 coin/flower orchard',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_BREAD,
            cost=1,
            target_card=CardFlowerOrchard(game),
            payout=1,
            activations=[6],
        )

class CardPizzaJoint(CardBasicRed):

    def __init__(self, game):
        super(CardPizzaJoint, self).__init__(
            game=game,
            name='Pizza Joint',
            desc="Get 1 coin from the player who rolled the dice.",
            short_desc='1 coin',
            color=Card.COLOR_RED,
            family=Card.FAMILY_CUP,
            cost=1,
            fee=1,
            activations=[7],
        )

class CardPublisher(Card):

    def __init__(self, game):
        super(CardPublisher, self).__init__(
            game=game,
            name='Publisher',
            desc='Get 1 coin from each player for each [Cup] and [Bread] establishment they have, on your turn only.',
            short_desc='1 coin/cup+bread/all players',
            color=Card.COLOR_PURPLE,
            family=Card.FAMILY_MAJOR,
            cost=5,
            activations=[7],
        )

    def _hit(self, player_rolled):
        """
        One coin from all players for each Cup and Bread they have.
        """
        for player in self.game.players:
            if player != self.owner:
                num_cards = 0
                for card in player.deck:
                    if card.family == Card.FAMILY_CUP or card.family == Card.FAMILY_BREAD:
                        num_cards += 1
                to_steal = min(num_cards, player.money)
                if to_steal > 0:
                    self.owner.money += to_steal
                    player.money -= to_steal
                    self.game.add_event('Player "%s" received %d coins from "%s" from a %s (new total: %d)' % (self.owner, to_steal, player, self, self.owner.money))

class CardTaxOffice(Card):

    def __init__(self, game):
        super(CardTaxOffice, self).__init__(
            game=game,
            name='Tax Office',
            desc='Take half (rounded down) of the coins from each player who has 10 coins or more, on your turn only.',
            short_desc='half from players w/ 10+ coins',
            color=Card.COLOR_PURPLE,
            family=Card.FAMILY_MAJOR,
            cost=4,
            activations=[8,9],
        )

    def _hit(self, player_rolled):
        """
        Half coins from each player who's got 10 or more.
        """
        for player in self.game.players:
            if player != self.owner:
                if player.money >= 10:
                    to_steal = math.floor(player.money / 2)
                    self.owner.money += to_steal
                    player.money -= to_steal
                    self.game.add_event('Player "%s" received %d coins from "%s" from a %s (new total: %d)' % (self.owner, to_steal, player, self, self.owner.money))

class CardHamburgerStand(CardBasicRed):

    def __init__(self, game):
        super(CardHamburgerStand, self).__init__(
            game=game,
            name='Hamburger Stand',
            desc="Get 1 coin from the player who rolled the dice.",
            short_desc='1 coin',
            color=Card.COLOR_RED,
            family=Card.FAMILY_CUP,
            cost=1,
            fee=1,
            activations=[8],
        )

class CardMackerelBoat(CardBasicPayout):

    def __init__(self, game):
        super(CardMackerelBoat, self).__init__(
            game=game,
            name='Mackerel Boat',
            desc="If you have a Harbor, get 3 coins from the bank on anyone's turn.",
            short_desc='w/ harbor, 3 coins',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_BOAT,
            cost=2,
            payout=3,
            activations=[8],
        )

    def required_landmark(self):
        return LandmarkHarbor()

class CardFoodWarehouse(CardFactoryFamily):

    def __init__(self, game):
        super(CardFoodWarehouse, self).__init__(
            game=game,
            name='Food Warehouse',
            desc='Get 2 coins from the bank for each [Cup] establishment that you own, on your turn only.',
            short_desc='2 coins/cup',
            color=Card.COLOR_GREEN,
            family=Card.FAMILY_FACTORY,
            cost=2,
            target_family=Card.FAMILY_CUP,
            payout=2,
            activations=[12,13],
        )

class CardTunaBoat(Card):
    """
    Tuna Boat!
    """

    def __init__(self, game):
        super(CardTunaBoat, self).__init__(
            game=game,
            name='Tuna Boat',
            desc="On anyone's turn: The current player rolls 2 dice.  If you have a harbor you get as many coins as the dice total.",
            short_desc='w/ harbor, 2 dice -> coins',
            color=Card.COLOR_BLUE,
            family=Card.FAMILY_BOAT,
            cost=5,
            activations=[12,13,14],
        )

    def required_landmark(self):
        return LandmarkHarbor()

    def _hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled).  The tuna
        boat roll is saved up in the main Game object so that it can be reused across
        multiple Tuna Boat activations.  This variable should be cleared out as soon
        as the rolling phase is done.
        """
        if self.game.tuna_boat_roll is None:
            roll1 = random.randint(1, 6)
            roll2 = random.randint(1, 6)
            self.game.tuna_boat_roll = roll1 + roll2
            self.game.add_event('Tuna Boat roll results: %d + %d = %d' % (roll1, roll2, self.game.tuna_boat_roll))
        self.owner.money += self.game.tuna_boat_roll
        self.game.add_event('Player "%s" received %d coins for a %s (new total: %d)' % (self.owner, self.game.tuna_boat_roll, self, self.owner.money))

class Landmark(object):
    """
    Base class for Landmarks, the "goal" cards of the game.  This base
    class is practically empty - all the actual functionality will have
    to be implemented in subclasses.
    """

    def __init__(self, player, name, desc, short_desc, cost, can_deconstruct=True, starts_constructed=False):
        self.player = player
        self.name = name
        self.desc = desc
        self.short_desc = short_desc
        self.cost = cost
        self.can_deconstruct = can_deconstruct
        self.constructed = starts_constructed
        if starts_constructed:
            self._construct_action()

    def __lt__(self, other):
        return (self.cost < other.cost)

    def __repr__(self):
        return self.name

    def construct(self):
        self.constructed = True
        self._construct_action()

    def deconstruct(self):
        if self.can_deconstruct:
            self.constructed = False
            self._deconstruct_action()

    def _construct_action(self):
        raise Exception('Not implemented!')

    def _deconstruct_action(self):
        raise Exception('Not implemented!')

class LandmarkCityHall(Landmark):
    """
    City Hall Landmark
    """

    def __init__(self, player=None):
        super(LandmarkCityHall, self).__init__(player=player,
            name='City Hall',
            desc='Immediately before buying establishments, if you have 0 coins, get 1 from the bank.',
            short_desc='1 coin if broke',
            cost=0,
            can_deconstruct=False,
            starts_constructed=True)

    def _construct_action(self):
        self.player.coin_if_broke = self

class LandmarkHarbor(Landmark):
    """
    Harbor Landmark
    """

    def __init__(self, player=None):
        super(LandmarkHarbor, self).__init__(player=player,
            name='Harbor',
            desc='If the dice total is 10 or more, you may add 2 to the total, on your turn only.',
            short_desc='+2 to 10+ dice',
            cost=2)

    def _construct_action(self):
        self.player.dice_add_to_ten_or_higher = self

    def _deconstruct_action(self):
        self.player.dice_add_to_ten_or_higher = False

class LandmarkTrainStation(Landmark):
    """
    Train Station Landmark
    """

    def __init__(self, player=None):
        super(LandmarkTrainStation, self).__init__(player=player,
            name='Train Station',
            desc='Roll 1 or 2 dice.',
            short_desc='2 dice',
            cost=4)

    def _construct_action(self):
        self.player.can_roll_two_dice = self

    def _deconstruct_action(self):
        self.player.can_roll_two_dice = False

class LandmarkShoppingMall(Landmark):
    """
    Shopping Mall Landmark
    """

    def __init__(self, player=None):
        super(LandmarkShoppingMall, self).__init__(player=player,
            name='Shopping Mall',
            desc='Earn +1 coin from your own [Cup] and [Bread] establishments',
            short_desc='cup/bread bonus',
            cost=10)

    def _construct_action(self):
        self.player.has_bread_cup_bonus = self

    def _deconstruct_action(self):
        self.player.has_bread_cup_bonus = False

class LandmarkAmusementPark(Landmark):
    """
    Amusement Park Landmark
    """

    def __init__(self, player=None):
        super(LandmarkAmusementPark, self).__init__(player=player,
            name='Amusement Park',
            desc='If you roll matching dice, take another turn after this one.',
            short_desc='extra turn on doubles',
            cost=16)

    def _construct_action(self):
        self.player.extra_turn_on_doubles = self

    def _deconstruct_action(self):
        self.player.extra_turn_on_doubles = False

class LandmarkRadioTower(Landmark):
    """
    Radio Tower Landmark
    """

    def __init__(self, player=None):
        super(LandmarkRadioTower, self).__init__(player=player,
            name='Radio Tower',
            desc='Once every turn, you can choose to re-roll your dice',
            short_desc='reroll dice',
            cost=22)

    def _construct_action(self):
        self.player.can_reroll_once = self

    def _deconstruct_action(self):
        self.player.can_reroll_once = False

class LandmarkAirport(Landmark):
    """
    Airport Landmark
    """

    def __init__(self, player=None):
        super(LandmarkAirport, self).__init__(player=player,
            name='Airport',
            desc='If you build nothing on your turn, you get 10 coins from the bank.',
            short_desc='10 coins for not building',
            cost=30)

    def _construct_action(self):
        self.player.gets_ten_coins_for_not_building = self

    def _deconstruct_action(self):
        self.player.gets_ten_coins_for_not_building = False
