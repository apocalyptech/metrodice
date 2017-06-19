#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import random

from . import cards, markets, actionlib

class Player(object):
    """
    Class to hold a single player
    """

    def __init__(self, name):
        self.name = name
        self.game = None
        self.money = 3
        self.deck = []
        self.landmarks = []
        self.rolled_doubles = False

        # Main card list is stored in self.deck, but we'll
        # use a little dict as well so we can look up card "hits"
        # after die rolls, rather than having to loop through all
        # cards.  Not that it really matters given the size of
        # our data, but whatever.
        self.deck_dict = {n: [] for n in range(1, 15)}

        # Abilities unlocked by Landmarks.  False when not unlocked,
        # or the Landmark object if they are.  (So that we can report
        # which Landmark caused an effect without having to hardcode
        # the Landmark effects anywhere but the Landmark classes
        # themselves.)
        self.coin_if_broke = False
        self.dice_add_to_ten_or_higher = False
        self.can_roll_two_dice = False
        self.has_bread_cup_bonus = False
        self.extra_turn_on_doubles = False
        self.can_reroll_once = False
        self.gets_ten_coins_for_not_building = False

    def game_setup(self, game):
        """
        Sets up various variables we can only get from the Game
        object.
        """

        self.game = game

        # Landmarks
        for landmark in game.expansion.landmarks:
            self.landmarks.append(landmark(self))

        # Starting Deck
        self.add_card(cards.CardWheat(game))
        self.add_card(cards.CardBakery(game))

    def has_card(self, compare_card):
        """
        Returns True if the player has at least one of the specified
        card.  This is a bit lame due to our implementation of deck.
        """
        for card in self.deck:
            if type(card) == type(compare_card):
                return True
        return False

    def has_landmark(self, compare_landmark):
        """
        Returns True if the player has constructed the given landmark.
        `compare_landmark` should be a type, not an instance.
        """
        for landmark in self.landmarks:
            if type(landmark) == compare_landmark:
                return landmark.constructed
        return False

    def __repr__(self):
        return self.name

    def process_roll(self, roll, color, player_rolled):
        """
        Process a roll - hit on any cards matching the rolled number and
        color.  The player who actually rolled the dice is passed in as
        well, in case there are interactions to be had (mostly just for
        reds).
        """
        for card in self.deck_dict[roll]:
            if card.color == color:
                card.hit(player_rolled)

    def add_card(self, card):
        """
        Adds a card to our deck.
        """
        # Remove from existing owner's deck, if applicable.
        if card.owner is not None:
            card.owner.remove_card(card)

        # Now add it to our own
        card.owner = self
        self.deck.append(card)
        for num in card.activations:
            self.deck_dict[num].append(card)

    def remove_card(self, card):
        """
        Removes a card from our deck
        """
        self.deck.remove(card)
        for num in card.activations:
            self.deck_dict[num].remove(card)

    def has_won(self):
        """
        Check to see if we've won or not
        """
        for landmark in self.landmarks:
            if not landmark.constructed:
                return False
        return True

class Game(object):
    """
    The main class which controls game logic.
    """

    (STATE_TURN_BEGIN,
        STATE_ASK_REROLL,
        STATE_ASK_ADD_TO_ROLL,
        STATE_ESTABLISHMENT_CHOICE,
        STATE_PURCHASE_DECISION,
        STATE_GAME_OVER,
        ) = range(6)

    ENG_STATE = {
            STATE_TURN_BEGIN: 'Beginning of turn',
            STATE_ASK_REROLL: 'Asking if player wants to re-roll',
            STATE_ASK_ADD_TO_ROLL: 'Asking if player wants to add +2 to dice roll',
            STATE_ESTABLISHMENT_CHOICE: 'Waiting for player to make Establishment decision',
            STATE_PURCHASE_DECISION: 'Waiting for player to make purchase decision',
            STATE_GAME_OVER: 'Game Over',
        }

    def __init__(self, players, expansion, market):
        """
        Initialization.  Set things up!  The Expansion/Market stuff
        is just hardcoded for now.
        """

        # Set up our _events list early, in case an expansion or market
        # wants to leave us a message (though we will discard them afterwards)
        self._events = []

        # Now set up the main vars
        self.players = players
        self.expansion = expansion
        self.market = market(self, self.expansion)

        # Populate various player bits which rely on expansion and market
        for player in self.players:
            player.game_setup(self)

        # Clear out any events which may have been generated
        self._events = []

        # Set up our state
        self.current_player_idx = 0
        self.current_player = self.players[0]
        self.state = self.STATE_TURN_BEGIN
        self.state_cards = []
        self.rolled_dice = 0
        self.roll_result = 0
        self.actions_available = []
        self.tuna_boat_roll = None
        self.set_up_available_actions()

    def set_up_available_actions(self):
        """
        Sets up what actions are available to the current user, given the
        state of the game.  Populates those choices in our State object,
        and returns them, as well.
        """
        actions = []

        if self.state == Game.STATE_TURN_BEGIN:
            actions.append(actionlib.ActionRollOne(self.current_player))
            if self.current_player.can_roll_two_dice:
                actions.append(actionlib.ActionRollTwo(self.current_player))

        elif self.state == Game.STATE_PURCHASE_DECISION:
            actions.append(actionlib.ActionSkipBuy(self.current_player))
            cards_available = self.market.cards_available()
            for card in sorted(cards_available.keys()):
                count = cards_available[card]
                if count > 0 and self.current_player.money >= card.cost:
                    if card.family == cards.Card.FAMILY_MAJOR and self.current_player.has_card(card):
                        continue
                    actions.append(actionlib.ActionBuyCard(self.current_player, card))
            for landmark in sorted(self.current_player.landmarks):
                if not landmark.constructed and self.current_player.money >= landmark.cost:
                    actions.append(actionlib.ActionBuyLandmark(self.current_player, landmark))

        elif self.state == Game.STATE_ASK_REROLL:
            actions.append(actionlib.ActionKeepRoll(self.current_player, self.roll_result))
            if self.rolled_dice == 1:
                actions.append(actionlib.ActionRollOne(self.current_player, num_to_reroll=None))
            elif self.rolled_dice == 2:
                actions.append(actionlib.ActionRollTwo(self.current_player, num_to_reroll=None))
            else:
                raise Exception('Unkown number of dice rolled: {}'.format(self.rolled_dice))

        elif self.state == Game.STATE_ASK_ADD_TO_ROLL:
            actions.append(actionlib.ActionKeepRoll(self.current_player, self.roll_result, False))
            actions.append(actionlib.ActionAddToRoll(self.current_player, self.roll_result))

        elif self.state == Game.STATE_ESTABLISHMENT_CHOICE:
            for card in self.state_cards:
                actions.extend(card.get_pending_actions())

        self.actions_available = actions
        return actions

    def state_str(self):
        """
        Returns a string representation of the game state
        """
        return self.ENG_STATE[self.state]

    def add_event(self, event):
        """
        Adds an event to our event list (ie: something the user will want to know about)
        """
        self._events.append(event)

    def consume_events(self):
        """
        Returns a copy of our event list and then clears out our own event list.
        """
        events = [x for x in self._events]
        self._events = []
        return events

    def players_counterclockwise(self, player):
        """
        Convenience function to loop through the players list counter-clockwise,
        starting at (and omitting) the given player.  The only time this is likely to
        ever get called is for processing red cards (on self.current_player's turn),
        so it's maybe silly to abstract it.  Ah well.
        """
        players_rev = list(reversed(self.players))
        player_idx = players_rev.index(player)
        return players_rev[player_idx+1:] + players_rev[:player_idx]

    def player_rolled(self, roll, dice_rolled, allow_addition=True):
        """
        Process what happens when a player rolls dice and gets a number.  `dice_rolled` should
        be the number of dice rolled if the player might be eligible for a reroll.  Pass in
        `None` to `dice_rolled` to prevent any rerolls.
        """

        # Step 0: If the player has the required Landmark, see if they want
        # to re-roll.
        if dice_rolled is not None and self.current_player.can_reroll_once:
            self.state = Game.STATE_ASK_REROLL
            return

        # Step 0.5: If the player has the required Landmark, see if they want
        # to add 2 to the roll, if it's already 10 or higher
        if allow_addition and roll >= 10 and self.current_player.dice_add_to_ten_or_higher:
            self.state = Game.STATE_ASK_ADD_TO_ROLL
            return

        # Step 1: Reds - process other players' hands
        for player in self.players_counterclockwise(self.current_player):
            player.process_roll(roll, cards.Card.COLOR_RED, self.current_player)

        # Step 2: Blues - process all player's hands
        for player in self.players:
            player.process_roll(roll, cards.Card.COLOR_BLUE, self.current_player)

        # Step 2.5: Clear out any Tuna Boat roll that we may have held on to.
        self.tuna_boat_roll = None

        # Step 3: Greens - process current player's hand
        self.current_player.process_roll(roll, cards.Card.COLOR_GREEN, self.current_player)

        # Step 4: Purples - process current player's hand
        self.current_player.process_roll(roll, cards.Card.COLOR_PURPLE, self.current_player)

        # Step X: Advance the game state, if we can
        self.finish_roll()

    def finish_roll(self):
        """
        Done with the rolling step.
        """
        if len(self.state_cards) == 0:
            self.state = Game.STATE_PURCHASE_DECISION
            if self.current_player.coin_if_broke and self.current_player.money == 0:
                self.add_event('Player "{}" recieved 1 coin due to {}'.format(self.current_player, self.current_player.coin_if_broke))
                self.current_player.money = 1
        else:
            self.state = Game.STATE_ESTABLISHMENT_CHOICE

    def buy_finished(self):
        """
        The current player is through buying things.
        """
        if self.current_player.rolled_doubles and self.current_player.extra_turn_on_doubles:
            self.add_event('Player "{}" takes another turn because of rolling doubles'.format(self.current_player))
        else:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            self.current_player = self.players[self.current_player_idx]
            self.add_event('Turn change: player "{}"'.format(self.current_player))
        self.state_cards = []
        self.state = Game.STATE_TURN_BEGIN

    def add_state_card(self, card):
        """
        Adds a state card that still needs processing.
        """
        if card not in self.state_cards:
            self.state_cards.append(card)

    def remove_state_card(self, card):
        """
        Removes a state card which no longer needs processing
        """
        if card in self.state_cards:
            self.state_cards.remove(card)

    def check_victory(self, player):
        """
        Checks to see if the given player has won the game.  If so, set our
        state appropriately.
        """
        if player.has_won():
            self.add_event('Player "{}" has constructed all landmarks and won the game!'.format(player))
            self.state = Game.STATE_GAME_OVER
            return True
        else:
            return False

