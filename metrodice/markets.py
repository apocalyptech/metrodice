#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import random

from . import cards
from .eventlib import *

class MarketBase(object):
    """
    The base 'market' class which is used to populate the available
    cards to buy.  Technically this should be a part of the expansion,
    but I'd prefer the flexibility to be able to mix and match, esp.
    given that the market distribution in After Dark is rather interesting.
    To override, subclass and override `_populate_initial()` and
    `_check_replace()`
    """

    def __init__(self, game, expansion=None, name='Base Market', deck=None):
        self.name = name
        self.game = game
        if deck is not None:
            self.deck = list(deck)
        elif expansion is not None:
            self.deck = expansion.generate_deck(game)
        else:
            raise Exception('One of expansion or deck must be passed to MarketBase.__init__')
        self.available = {}
        self._populate_initial()

    def __repr__(self):
        return self.name

    def _add_to_available(self, card):
        """
        Adds the specified card to our list of available cards
        """
        if type(card) in self.available:
            self.available[type(card)].append(card)
        else:
            self.available[type(card)] = [card]

    def _populate_initial(self):
        """
        Initial population.  In the base game this means make everything
        available.
        """
        for card in self.deck:
            self._add_to_available(card)

    def _check_replace(self):
        """
        Checks our Market to see if we need to repopulate anything.  In the
        base game, where we have literally all cards available, there is
        nothing to do here since we don't have a draw deck to grab from.
        """
        pass

    def take_card(self, card):
        """
        Takes a card from the market (note that the actual financial
        transaction must happen outside this routine, as we only manage
        the actual market itself.)
        """
        card_type = type(card)
        if card_type not in self.available:
            raise Exception('Card "{}" is not found in the market'.format(
                card))
        to_return = self.available[card_type].pop()
        if len(self.available[card_type]) == 0:
            del self.available[card_type]
        self._check_replace()
        return to_return

    def cards_available(self):
        """
        Returns a dictionary - the key is an available card, and the value is
        the number of those cards available to buy.
        """
        ret_dict = {}
        for cardlist in self.available.values():
            ret_dict[cardlist[0]] = len(cardlist)
        return ret_dict

class MarketHarbor(MarketBase):
    """
    The market according to the Harbor expansion.  Will keep a pool of ten
    types of cards available, and replenish as needed.
    """

    def __init__(self, game, expansion=None, deck=None, pile_limit=10):
        self.pile_limit = pile_limit
        super(MarketHarbor, self).__init__(
            game=game,
            name='Harbor Market',
            expansion=expansion,
            deck=deck,
        )

    def _populate_initial(self):
        """
        Initial population.  Mostly just shuffle and then call our
        usual market-filling routine.
        """
        random.shuffle(self.deck)
        self._check_replace()

    def _check_replace(self):
        """
        Fills our market until we have ten unique piles of cards.  Since
        the market is always changing, also provide notification to the
        user about what's been dealt out.
        """
        while (len(self.deck) > 0) and (len(self.available) < self.pile_limit):
            new_card = self.deck.pop()
            self.game.add_event(EventMarketCardAdded(new_card))
            self._add_to_available(new_card)

class MarketBrightLights(MarketBase):
    """
    The market according to the Bright Lights, Big City version.  This one
    keeps three "separate" pools of cards available - five "regular" which
    hit on 1-6, five "regular" which hit on 7+, and two major establishments.
    We're implementing that as three separate MarketHarbor markets, internally.
    """

    def __init__(self, game, expansion=None, deck=None):
        super(MarketBrightLights, self).__init__(
            game=game,
            name='Bright Lights, Big City Market',
            expansion=expansion,
            deck=deck,
        )

    def _populate_initial(self):
        """
        Initial population.  Mostly just shuffle and then call our
        usual market-filling routine.
        """
        low_cards = []
        major_establishments = []
        high_cards = []

        # Sort into three different piles
        for card in self.deck:
            if card.family == cards.Card.FAMILY_MAJOR:
                major_establishments.append(card)
            elif card.activations[0] > 6:
                high_cards.append(card)
            else:
                low_cards.append(card)

        # Store this all internally as some MarketHarbor objects.
        # This is rather improper but IMO is less messy than some
        # other ways of doing it.
        self.stock_low = MarketHarbor(self.game, deck=low_cards, pile_limit=5)
        self.stock_major = MarketHarbor(self.game, deck=major_establishments, pile_limit=2)
        self.stock_high = MarketHarbor(self.game, deck=high_cards, pile_limit=5)
        self.markets = [self.stock_low, self.stock_major, self.stock_high]

        # And do our initial population
        self._check_replace()

    def _check_replace(self):
        """
        Passthrough to our three submarkets
        """
        for market in self.markets:
            market._check_replace()

    def take_card(self, card):
        """
        Take a card.  Rather than looping through, we'll go right after
        the pool we're interested in.
        """
        if card.family == cards.Card.FAMILY_MAJOR:
            return self.stock_major.take_card(card)
        elif card.activations[0] > 6:
            return self.stock_high.take_card(card)
        else:
            return self.stock_low.take_card(card)

    def cards_available(self):
        """
        Have to combine our market outputs here.
        """
        ret_dict = {}
        for market in self.markets:
            for (card, count) in market.cards_available().items():
                ret_dict[card] = count
        return ret_dict
