#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import random

class Action(object):
    """
    Class describing an action a user can take.  A bit silly to have
    a base class like this, really - pretty much everything is implemented
    in subclasses.
    """

    def __init__(self, desc, player):
        self.desc = desc
        self.player = player
        self.game = player.game

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

    def __init__(self, player, num_to_reroll=1):
        """
        Roll the die
        """
        self.num_to_reroll = num_to_reroll
        if num_to_reroll is None:
            verb = 'Reroll'
        else:
            verb = 'Roll'
        super(ActionRollOne, self).__init__(desc='%s One Die' % (verb),
            player=player)

    def _rolled_dice(self, roll):
        """
        This is pulled out so that we can definitively test that cards are being hit.
        """
        self.game.rolled_dice = 1
        self.game.roll_result = roll
        self.player.rolled_doubles = False
        self.game.add_event('Player "%s" rolled one die and got a %d' % (self.player, roll))
        self.game.player_rolled(roll, self.num_to_reroll)

    def _action_body(self):
        roll = random.randint(1, 6)
        self._rolled_dice(roll)

class ActionRollTwo(Action):
    """
    Action to roll two single dice
    """

    def __init__(self, player, num_to_reroll=2):
        """
        Roll the dice
        """
        self.num_to_reroll = num_to_reroll
        if num_to_reroll is None:
            verb = 'Reroll'
        else:
            verb = 'Roll'
        super(ActionRollTwo, self).__init__(desc='%s Two Dice' % (verb),
            player=player)

    def _rolled_dice(self, roll1, roll2):
        """
        This is pulled out into its own function so that the rolled_doubles
        logic can be tested without having to deal with random numbers.
        """
        self.game.rolled_dice = 2
        if roll1 == roll2:
            self.player.rolled_doubles = True
        else:
            self.player.rolled_doubles = False
        total = roll1 + roll2
        self.game.rolled_dice = 2
        self.game.roll_result = total
        self.game.add_event('Player "%s" rolled two dice and got a %d (%d & %d)' % (self.player, total, roll1, roll2))
        self.game.player_rolled(total, self.num_to_reroll)

    def _action_body(self):
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        self._rolled_dice(roll1, roll2)

class ActionKeepRoll(Action):
    """
    Action to keep the roll you made (Radio Tower)
    """

    def __init__(self, player, roll, allow_addition=True):
        """
        Roll the dice
        """
        self.roll = roll
        self.allow_addition = allow_addition
        super(ActionKeepRoll, self).__init__(desc='Keep your die roll of %d' % (roll),
            player=player)

    def _action_body(self):
        self.game.add_event('Player "%s" kept the die roll of %d' % (self.player, self.roll))
        self.game.player_rolled(self.roll, None, self.allow_addition)

class ActionAddToRoll(Action):
    """
    Action to add 2 to the dice roll
    """

    def __init__(self, player, roll, num_to_add=2):
        """
        Add to roll
        """
        self.roll = roll
        self.num_to_add = num_to_add
        super(ActionAddToRoll, self).__init__(desc='Add %d to roll (result: %d)' % (num_to_add, roll + num_to_add),
            player=player)

    def _action_body(self):
        new_roll = self.roll + self.num_to_add
        self.game.add_event('Player "%s" added %d to roll, to make the roll: %d' % (self.player, self.num_to_add, new_roll))
        self.game.player_rolled(new_roll, None, False)

class ActionSkipBuy(Action):
    """
    Action to not actually buy anything.  (Exciting!)
    """

    def __init__(self, player):
        """
        Skip the buy phase
        """
        super(ActionSkipBuy, self).__init__(desc="Don't buy anything",
            player=player)

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

    def __init__(self, player, card):
        """
        Buy the specified card
        """
        self.card = card
        super(ActionBuyCard, self).__init__(desc="Buy Card: $%d for %s (%s) %s [%s]" % (card.cost, card, card.short_desc, card.activations, card.family_str()),
            player=player)

    def _action_body(self):
        if self.card.cost > self.player.money:
            raise Exception('Player "%s" ($%d in bank) cannot afford card "%s" (cost: $%d)' % (
                self.player, self.player.money,
                self.card, self.card.cost))
        self.player.money -= self.card.cost
        self.game.add_event('Player "%s" bought card "%s" for %d.' % (self.player, self.card, self.card.cost))
        self.player.add_card(self.game.market.take_card(self.card))
        self.game.buy_finished()

class ActionBuyLandmark(Action):
    """
    Action to buy a landmark.
    """

    def __init__(self, player, landmark):
        """
        Buy the specified landmark
        """
        self.landmark = landmark
        super(ActionBuyLandmark, self).__init__(desc="Construct Landmark: %s for %d" % (landmark, landmark.cost),
            player=player)

    def _action_body(self):
        if self.landmark.cost > self.player.money:
            raise Exception('Player "%s" ($%d in bank) cannot afford landmark "%s" (cost: $%d)' % (
                self.player, self.player.money,
                self.landmark, self.landmark.cost))
        self.player.money -= self.landmark.cost
        self.landmark.construct()
        self.game.add_event('Player "%s" constructed landmark "%s" for %d.' % (self.player, self.landmark, self.landmark.cost))
        if not self.game.check_victory(self.player):
            self.game.buy_finished()

class ActionChoosePlayer(Action):
    """
    Action to choose one of the other players
    """

    def __init__(self, player, card, other_player):
        """
        Choose a player
        """
        self.card = card
        self.other_player = other_player
        super(ActionChoosePlayer, self).__init__(desc='Choose player "%s" (%d coin(s)) (from %s)' % (other_player, other_player.money, card),
            player=player)

    def _action_body(self):
        self.card.chose_player(self.other_player)

class ActionChooseOwnCard(Action):
    """
    Action to choose a card of our own
    """

    def __init__(self, player, calling_card, chosen_card):
        """
        Choose a card
        """
        self.calling_card = calling_card
        self.chosen_card = chosen_card
        super(ActionChooseOwnCard, self).__init__(desc='Choose your card to trade: %s (from %s)' % (chosen_card, calling_card),
            player=player)

    def _action_body(self):
        self.calling_card.chose_own_card(self.chosen_card)

class ActionChooseOtherCard(Action):
    """
    Action to choose someone else's card
    """

    def __init__(self, player, calling_card, chosen_card):
        """
        Choose a card
        """
        self.calling_card = calling_card
        self.chosen_card = chosen_card
        super(ActionChooseOtherCard, self).__init__(desc='Choose %s\'s card to receive: %s (for %s)' % (chosen_card.owner, chosen_card, calling_card),
            player=player)

    def _action_body(self):
        self.calling_card.chose_other_card(self.chosen_card)
