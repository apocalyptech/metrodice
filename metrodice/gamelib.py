#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import random

from . import cards

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
            self.deck = deck
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
            raise Exception('Card "%s" is not found in the market' % (
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
            self.game.add_event('Added to the market: %s' % (new_card))
            self._add_to_available(new_card)

class MarketBrightLights(MarketBase):
    """
    The market according to the Bright Lights, Big City version.  This one
    keeps three "separate" pools of cards available - four "regular" which
    hit on 1-6, four "regular" which hit on 7+, and two major establishments.
    types of cards available, and replenish as needed.
    """

    def __init__(self, game, expansion=None, deck=None):
        self.pile_limit = pile_limit
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
        self.stock_low = MarketHarbor(self.game, deck=low_cards, pile_limit=4)
        self.stock_major = MarketHarbor(self.game, deck=major_establishments, pile_limit=2)
        self.stock_high = MarketHarbor(self.game, deck=high_cards, pile_limit=4)
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

class Action(object):
    """
    Class describing an action a user can take.  A bit silly to have
    a base class like this, really - pretty much everything is implemented
    in subclasses.
    """

    def __init__(self, desc, player, game):
        self.desc = desc
        self.player = player
        self.game = game

    def do_action(self):
        """
        Perform the action - note that the bulk of this happens in _action_body().
        This wrapper exists to ensure that we clean up properly, though.
        """
        self._action_body()
        self.game.set_up_available_actions()

    def _action_body(self):
        raise Exception('Action not actually implemented')

class ActionRollOne(Action):
    """
    Action to roll a single die
    """

    def __init__(self, player, game, num_to_reroll=1):
        """
        Roll the die
        """
        self.num_to_reroll = num_to_reroll
        if num_to_reroll is None:
            verb = 'Reroll'
        else:
            verb = 'Roll'
        super(ActionRollOne, self).__init__(desc='%s One Die' % (verb),
            player=player,
            game=game)

    def _action_body(self):
        roll = random.randint(1, 6)
        self.game.rolled_dice = 1
        self.game.roll_result = roll
        self.player.rolled_doubles = False
        self.game.add_event('Player "%s" rolled one die and got a %d' % (self.player, roll))
        self.game.player_rolled(roll, self.num_to_reroll)

class ActionRollTwo(Action):
    """
    Action to roll two single dice
    """

    def __init__(self, player, game, num_to_reroll=2):
        """
        Roll the dice
        """
        self.num_to_reroll = num_to_reroll
        if num_to_reroll is None:
            verb = 'Reroll'
        else:
            verb = 'Roll'
        super(ActionRollTwo, self).__init__(desc='%s Two Dice' % (verb),
            player=player,
            game=game)

    def _action_body(self):
        self.game.rolled_dice = 2
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        if roll1 == roll2:
            self.player.rolled_doubles = True
        else:
            self.player.rolled_doubles = False
        total = roll1 + roll2
        self.game.rolled_dice = 2
        self.game.roll_result = total
        self.game.add_event('Player "%s" rolled two dice and got a %d (%d & %d)' % (self.player, total, roll1, roll2))
        self.game.player_rolled(total, self.num_to_reroll)

class ActionKeepRoll(Action):
    """
    Action to keep the roll you made (Radio Tower)
    """

    def __init__(self, player, game, roll, allow_addition=True):
        """
        Roll the dice
        """
        self.roll = roll
        self.allow_addition = allow_addition
        super(ActionKeepRoll, self).__init__(desc='Keep your die roll of %d' % (roll),
            player=player,
            game=game)

    def _action_body(self):
        self.game.add_event('Player "%s" kept the die roll of %d' % (self.player, self.roll))
        self.game.player_rolled(self.roll, None, self.allow_addition)

class ActionAddToRoll(Action):
    """
    Action to add 2 to the dice roll
    """

    def __init__(self, player, game, roll, num_to_add=2):
        """
        Add to roll
        """
        self.roll = roll
        self.num_to_add = num_to_add
        super(ActionAddToRoll, self).__init__(desc='Add %d to roll (result: %d)' % (num_to_add, roll + num_to_add),
            player=player,
            game=game)

    def _action_body(self):
        new_roll = self.roll + self.num_to_add
        self.game.add_event('Player "%s" added %d to roll, to make the roll: %d' % (self.player, self.num_to_add, new_roll))
        self.game.player_rolled(new_roll, None, False)

class ActionSkipBuy(Action):
    """
    Action to not actually buy anything.  (Exciting!)
    """

    def __init__(self, player, game):
        """
        Skip the buy phase
        """
        super(ActionSkipBuy, self).__init__(desc="Don't buy anything",
            player=player,
            game=game)

    def _action_body(self):
        if self.player.gets_ten_coins_for_not_building:
            self.game.add_event('Player "%s" gets 10 coins for not buying anything (from %s).' % (self.player, self.player.gets_ten_coins_for_not_building))
            self.player.money += 10
        else:
            self.game.add_event('Player "%s" opted not to buy anything.' % (self.player))
        self.game.buy_finished()

class ActionBuyCard(Action):
    """
    Action to buy a card.
    """

    def __init__(self, player, game, card):
        """
        Buy the specified card
        """
        self.card = card
        super(ActionBuyCard, self).__init__(desc="Buy Card: $%d for %s (%s) %s [%s]" % (card.cost, card, card.short_desc, card.activations, card.family_str()),
            player=player,
            game=game)

    def _action_body(self):
        self.player.money -= self.card.cost
        self.player.add_card(self.game.market.take_card(self.card))
        self.game.add_event('Player "%s" bought card "%s" for %d.' % (self.player, self.card, self.card.cost))
        self.game.buy_finished()

class ActionBuyLandmark(Action):
    """
    Action to buy a landmark.
    """

    def __init__(self, player, game, landmark):
        """
        Buy the specified landmark
        """
        self.landmark = landmark
        super(ActionBuyLandmark, self).__init__(desc="Construct Landmark: %s for %d" % (landmark, landmark.cost),
            player=player,
            game=game)

    def _action_body(self):
        self.player.money -= self.landmark.cost
        self.landmark.construct()
        self.game.add_event('Player "%s" constructed landmark "%s" for %d.' % (self.player, self.landmark, self.landmark.cost))
        if not self.game.check_victory(self.player):
            self.game.buy_finished()

class ActionChoosePlayer(Action):
    """
    Action to choose one of the other players
    """

    def __init__(self, player, game, card, other_player):
        """
        Choose a player
        """
        self.card = card
        self.other_player = other_player
        super(ActionChoosePlayer, self).__init__(desc='Choose player "%s" (%d coin(s)) (from %s)' % (other_player, other_player.money, card),
            player=player,
            game=game)

    def _action_body(self):
        self.card.chose_player(self.other_player)

class ActionChooseOwnCard(Action):
    """
    Action to choose a card of our own
    """

    def __init__(self, player, game, calling_card, chosen_card):
        """
        Choose a card
        """
        self.calling_card = calling_card
        self.chosen_card = chosen_card
        super(ActionChooseOwnCard, self).__init__(desc='Choose your card to trade: %s (from %s)' % (chosen_card, calling_card),
            player=player,
            game=game)

    def _action_body(self):
        self.calling_card.chose_own_card(self.chosen_card)

class ActionChooseOtherCard(Action):
    """
    Action to choose someone else's card
    """

    def __init__(self, player, game, calling_card, chosen_card):
        """
        Choose a card
        """
        self.calling_card = calling_card
        self.chosen_card = chosen_card
        super(ActionChooseOtherCard, self).__init__(desc='Choose %s\'s card to receive: %s (for %s)' % (chosen_card.owner, chosen_card, calling_card),
            player=player,
            game=game)

    def _action_body(self):
        self.calling_card.chose_other_card(self.chosen_card)

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
            actions.append(ActionRollOne(self.current_player, self))
            if self.current_player.can_roll_two_dice:
                actions.append(ActionRollTwo(self.current_player, self))

        elif self.state == Game.STATE_PURCHASE_DECISION:
            actions.append(ActionSkipBuy(self.current_player, self))
            cards_available = self.market.cards_available()
            for card in sorted(cards_available.keys()):
                count = cards_available[card]
                if count > 0 and self.current_player.money >= card.cost:
                    if card.family == cards.Card.FAMILY_MAJOR and self.current_player.has_card(card):
                        continue
                    actions.append(ActionBuyCard(self.current_player, self, card))
            for landmark in sorted(self.current_player.landmarks):
                if not landmark.constructed and self.current_player.money >= landmark.cost:
                    actions.append(ActionBuyLandmark(self.current_player, self, landmark))

        elif self.state == Game.STATE_ASK_REROLL:
            actions.append(ActionKeepRoll(self.current_player, self, self.roll_result))
            if self.rolled_dice == 1:
                actions.append(ActionRollOne(self.current_player, self, num_to_reroll=None))
            elif self.rolled_dice == 2:
                actions.append(ActionRollTwo(self.current_player, self, num_to_reroll=None))
            else:
                raise Exception('Unkown number of dice rolled: %d' % (self.rolled_dice))

        elif self.state == Game.STATE_ASK_ADD_TO_ROLL:
            actions.append(ActionKeepRoll(self.current_player, self, self.roll_result, False))
            actions.append(ActionAddToRoll(self.current_player, self, self.roll_result))

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
                self.add_event('Player "%s" recieved 1 coin due to %s' % (self.current_player, self.current_player.coin_if_broke))
                self.current_player.money = 1
        else:
            self.state = Game.STATE_ESTABLISHMENT_CHOICE

    def buy_finished(self):
        """
        The current player is through buying things.
        """
        if self.current_player.rolled_doubles and self.current_player.extra_turn_on_doubles:
            self.add_event('Player "%s" takes another turn because of rolling doubles' % (self.current_player))
        else:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            self.current_player = self.players[self.current_player_idx]
            self.add_event('Turn change: player "%s"' % (self.current_player))
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
            self.add_event('Player "%s" has constructed all landmarks and won the game!' % (player))
            self.state = Game.STATE_GAME_OVER
            return True
        else:
            return False

