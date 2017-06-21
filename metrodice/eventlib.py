#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

class Event(object):
    """
    Class describing an event to be sent to any user of the game.  Kind
    of silly to have a base class; I expect basically everything will
    be implemented in the inheriting classes
    """

    def plural(self, number, label):
        """
        >>> e = Event()
        >>> e.plural(0, 'coin')
        '0 coins'
        >>> e.plural(1, 'coin')
        '1 coin'
        >>> e.plural(2, 'coin')
        '2 coins'
        """
        if number == 1:
            return '1 {}'.format(label)
        else:
            return '{} {}s'.format(number, label)

class EventPlayerReceivesCoin(Event):
    """
    Player receives a coin
    """

    def __init__(self, player, num_coins=1,
            cause_card=None, cause_landmark=None, cause_str=None,
            from_player=None, new_total=None):
        self.player = player
        self.num_coins = num_coins
        self.cause_card = cause_card
        self.cause_landmark = cause_landmark
        self.cause_str = cause_str
        self.new_total = new_total
        self.from_player = from_player

    def __str__(self):
        output = ['Player "{}" received {}'.format(self.player,
            self.plural(self.num_coins, 'coin'))]
        if self.from_player:
            output.append('from "{}"'.format(self.from_player))
        if self.cause_str:
            output.append('for {}'.format(self.cause_str))
        if self.cause_landmark:
            output.append('due to "{}"'.format(self.cause_landmark))
        if self.cause_card:
            output.append('for a {}'.format(self.cause_card))
        if self.new_total:
            output.append('(new total: {})'.format(self.new_total))
        return ' '.join(output)

class EventPlayerAnotherTurnRollDoubles(Event):
    """
    Player gets another turn due to rolling doubles
    """

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return 'Player "{}" takes another turn because of rolling doubles'.format(self.player)

class EventTurnChange(Event):
    """
    A new player's turn
    """

    def __init__(self, new_player):
        self.new_player = new_player

    def __str__(self):
        return 'Turn change: player "{}"'.format(self.new_player)

class EventPlayerWon(Event):
    """
    A player won the game
    """

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return 'Player "{}" has constructed all landmarks and won the game!'.format(self.player)

class EventMarketCardAdded(Event):
    """
    A card is added to the market
    """

    def __init__(self, card):
        self.card = card

    def __str__(self):
        return 'Added to the market: {}'.format(self.card)

class EventPlayerRolledOneDie(Event):
    """
    Player rolled a single die
    """

    def __init__(self, player, roll):
        self.player = player
        self.roll = roll

    def __str__(self):
        return 'Player "{}" rolled one die and got a {}'.format(self.player, self.roll)

class EventPlayerRolledTwoDice(Event):
    """
    Player rolled a two dice
    """

    def __init__(self, player, total, roll1, roll2):
        """
        A bit silly to store total, but whatever; it's computed before we get it
        so we may as well pass it through.
        """
        self.player = player
        self.total = total
        self.roll1 = roll1
        self.roll2 = roll2

    def __str__(self):
        return 'Player "{}" rolled two dice and got a {} ({} & {})'.format(
            self.player, self.total, self.roll1, self.roll2)

class EventPlayerKeepsRoll(Event):
    """
    Player opted to keep the roll (rather than re-roll)
    """

    def __init__(self, player, roll):
        self.player = player
        self.roll = roll

    def __str__(self):
        return 'Player "{}" kept the die roll of {}'.format(self.player, self.roll)

class EventPlayerAddedToRoll(Event):
    """
    Player opted to add a to the die roll
    """

    def __init__(self, player, added, new_roll):
        self.player = player
        self.added = added
        self.new_roll = new_roll

    def __str__(self):
        return 'Player "{}" added {} to roll, to make the roll: {}'.format(
            self.player, self.added, self.new_roll)

class EventPlayerDidNotBuy(Event):
    """
    Player opted not to buy anything
    """

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return 'Player "{}" opted not to buy anything.'.format(self.player)

class EventPlayerBoughtCard(Event):
    """
    Player bought a card
    """

    def __init__(self, player, card, cost):
        """
        Could technically just get the cost from the card itself, but perhaps
        in the future players will be able to get a discount or something.
        """
        self.player = player
        self.card = card
        self.cost = cost

    def __str__(self):
        return 'Player "{}" bought card "{}" for ${}.'.format(self.player, self.card, self.cost)

class EventPlayerConstructedLandmark(Event):
    """
    Player constructed a landmark
    """

    def __init__(self, player, landmark, cost):
        """
        Could technically just get the cost from the card itself, but perhaps
        in the future players will be able to get a discount or something.
        """
        self.player = player
        self.landmark = landmark
        self.cost = cost

    def __str__(self):
        return 'Player "{}" constructed landmark "{}" for ${}.'.format(self.player, self.landmark, self.cost)

class EventPlayerChoseOwnCard(Event):
    """
    Player chose their own card for trade
    """

    def __init__(self, player, card, cause):
        self.player = player
        self.card = card
        self.cause = cause

    def __str__(self):
        return '{} chose own "{}" card for trade (from {})'.format(self.player, self.card, self.cause)

class EventPlayerChoseOtherCard(Event):
    """
    Player chose someone else's card for trade
    """

    def __init__(self, player, other_player, card, cause):
        self.player = player
        self.other_player = other_player
        self.card = card
        self.cause = cause

    def __str__(self):
        return '{} chose {}\'s card "{}" card for trade (from {})'.format(
            self.player, self.other_player, self.card, self.cause)

class EventPlayerTradedCard(Event):
    """
    Player traded cards with someone
    """

    def __init__(self, player, card, other_player, other_card):
        self.player = player
        self.card = card
        self.other_player = other_player
        self.other_card = other_card

    def __str__(self):
        return '{} traded card "{}" for {}\'s card "{}"'.format(self.player, self.card,
            self.other_player, self.other_card)

class EventTunaBoatRoll(Event):
    """
    Tuna Boat Roll
    """

    def __init__(self, roll1, roll2, total):
        """
        As with the other roll events above, it's silly to store the total, but it's
        already computed so we'll just pass it on anyway.
        """
        self.roll1 = roll1
        self.roll2 = roll2
        self.total = total

    def __str__(self):
        return 'Tuna Boat roll results: {} + {} = {}'.format(self.roll1, self.roll2, self.total)
