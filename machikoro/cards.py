#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

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

    def hit(self, player_rolled):
        """
        Perform the action on the card (ie: this number has been rolled)
        """
        raise Exception('Not implemented!')

    def does_bread_cup_bonus_apply(self):
        """
        Does a bread+cup bonus (from Shopping Mall) apply?
        """
        if self.owner.has_bread_cup_bonus() and (self.family == Card.FAMILY_BREAD or self.family == Card.FAMILY_CUP):
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

    def hit(self, player_rolled):
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

    def hit(self, player_rolled):
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

    def hit(self, player_rolled):
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

    def hit(self, player_rolled):
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

    def hit(self, player_rolled):
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

    def hit(self, player_rolled):
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

class Landmark(object):
    """
    Base class for Landmarks, the "goal" cards of the game.  This base
    class is practically empty - all the actual functionality will have
    to be implemented in subclasses.
    """

    def __init__(self, name, desc, short_desc, cost):
        self.name = name
        self.desc = desc
        self.short_desc = short_desc
        self.cost = cost
        self.constructed = self.starts_constructed()

    def __lt__(self, other):
        return (self.cost < other.cost)

    def __repr__(self):
        return self.name

    def construct(self):
        self.constructed = True

    def starts_constructed(self):
        return False

    def allows_two_dice(self):
        return False

    def bread_cup_bonus(self):
        return False

    def extra_turn_on_doubles(self):
        return False

    def allows_one_reroll(self):
        return False

class LandmarkTrainStation(Landmark):
    """
    Train Station Landmark
    """

    def __init__(self):
        super(LandmarkTrainStation, self).__init__(name='Train Station',
            desc='Roll 1 or 2 dice.',
            short_desc='2 dice',
            cost=2)

    def allows_two_dice(self):
        return True

class LandmarkShoppingMall(Landmark):
    """
    Shopping Mall Landmark
    """

    def __init__(self):
        super(LandmarkShoppingMall, self).__init__(name='Shopping Mall',
            desc='Earn +1 coin from your own [Cup] and [Bread] establishments',
            short_desc='cup/bread bonus',
            cost=10)

    def bread_cup_bonus(self):
        return True

class LandmarkAmusementPark(Landmark):
    """
    Amusement Park Landmark
    """

    def __init__(self):
        super(LandmarkAmusementPark, self).__init__(name='Amusement Park',
            desc='If you roll matching dice, take another turn after this one.',
            short_desc='extra turn on doubles',
            cost=16)

    def extra_turn_on_doubles(self):
        return True

class LandmarkRadioTower(Landmark):
    """
    Radio Tower Landmark
    """

    def __init__(self):
        super(LandmarkRadioTower, self).__init__(name='Radio Tower',
            desc='Once every turn, you can choose to re-roll your dice',
            short_desc='reroll dice',
            cost=22)

    def allows_one_reroll(self):
        return True
