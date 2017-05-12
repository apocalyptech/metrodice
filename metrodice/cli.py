#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

import sys
import colorama

from .gamelib import Player, Game
from .cards import Card

class CLI(object):
    """
    CLI to playing Machi Koro.  Pretty basic.
    """

    def __init__(self):

        colorama.init(autoreset=False)

        self.players = []
        self.players.append(Player(name='CJ'))
        self.players.append(Player(name='Bob'))
        self.game  = Game(self.players)
        
        error_msg = None
        while True:
            sys.stdout.write(colorama.Back.BLACK)
            sys.stdout.write(colorama.Fore.WHITE)
            print('='*80)
            sys.stdout.write(colorama.Style.RESET_ALL)
            self.show_player_state(self.game.current_player)
            print()
            self.show_market(self.game.current_player)
            print()
            print('Current State: %s' % (self.game.state_str()))
            if error_msg is not None:
                sys.stdout.write(colorama.Fore.RED)
                print('ERROR: %s' % (error_msg))
                sys.stdout.write(colorama.Style.RESET_ALL)
                error_msg = None
            sys.stdout.write(colorama.Fore.YELLOW)
            for event in self.game.consume_events():
                print('INFO: %s' % (event))
            sys.stdout.write(colorama.Style.RESET_ALL)
            if self.game.state == Game.STATE_GAME_OVER:
                return
            print('Possible Actions:')
            allowed_choices = set('q')
            for (idx, state) in enumerate(self.game.actions_available):
                print('  %d. %s' % (idx+1, state.desc))
                allowed_choices.add(str(idx+1))
            print('  q. Quit Game')
            print()
            sys.stdout.write('%s%s%s (%s%d%s)> ' % (
                colorama.Fore.MAGENTA,
                self.game.current_player,
                colorama.Style.RESET_ALL,
                colorama.Fore.GREEN,
                self.game.current_player.money,
                colorama.Style.RESET_ALL,
            ))
            sys.stdout.flush()
            response = sys.stdin.readline()
            response = response.strip()
            if response not in allowed_choices:
                error_msg = 'Unknown choice "%s"' % (response)
            else:
                try:
                    choice_idx = int(response)
                    choice_idx -= 1
                    self.game.actions_available[choice_idx].do_action()
                except ValueError as e:
                    if response == 'q':
                        print('Exiting!')
                        return

    def card_colorama(self, card):
        if card.color == Card.COLOR_BLUE:
            return colorama.Fore.BLUE
        elif card.color == Card.COLOR_RED:
            return colorama.Fore.RED
        elif card.color == Card.COLOR_GREEN:
            return colorama.Fore.GREEN
        elif card.color == Card.COLOR_PURPLE:
            return colorama.Fore.MAGENTA

    def show_player_state(self, player):
        """
        Shows the given player state
        """
        player_str = 'Player: %s' % (player.name)
        sys.stdout.write(colorama.Fore.MAGENTA)
        print('-'*len(player_str))
        print(player_str)
        print('-'*len(player_str))
        sys.stdout.write(colorama.Fore.GREEN)
        print('Money: %d' % (player.money))
        sys.stdout.write(colorama.Style.RESET_ALL)
        print('Landmarks:')
        for landmark in sorted(player.landmarks):
            if landmark.constructed:
                sys.stdout.write(colorama.Style.BRIGHT)
                print(' * %s (%s)' % (landmark, landmark.short_desc))
                sys.stdout.write(colorama.Style.RESET_ALL)
            else:
                if landmark.cost > player.money:
                    sys.stdout.write(colorama.Fore.WHITE)
                    sys.stdout.write(colorama.Style.DIM)
                print(' * %s (%s) - cost: %d' % (landmark, landmark.short_desc, landmark.cost))
                sys.stdout.write(colorama.Style.RESET_ALL)

        # This bit is dumb; massaging our list of cards into a more market-like
        # structure
        print('Cards:')
        inventory = {}
        for card in player.deck:
            card_type = type(card)
            if card_type in inventory:
                inventory[card_type].append(card)
            else:
                inventory[card_type] = [card]
        inventory_flip = {}
        for cardlist in inventory.values():
            inventory_flip[cardlist[0]] = len(cardlist)

        for card in sorted(inventory_flip.keys()):
            sys.stdout.write(self.card_colorama(card))
            print(' * %dx %s %s (%s)' % (inventory_flip[card], card.activations, card, card.short_desc))
            sys.stdout.write(colorama.Style.RESET_ALL)

    def show_market(self, player):
        """
        Shows what's available at the market.
        """
        print('Market')
        print('------')
        cards_available = self.game.market.cards_available()
        for card in sorted(cards_available.keys()):
            count = cards_available[card]
            if card.cost > self.game.current_player.money:
                sys.stdout.write(colorama.Fore.WHITE)
                sys.stdout.write(colorama.Style.DIM)
            elif card.family == Card.FAMILY_MAJOR and player.has_card(card):
                sys.stdout.write(colorama.Fore.WHITE)
                sys.stdout.write(colorama.Style.DIM)
            else:
                sys.stdout.write(self.card_colorama(card))
            print(' * %dx %s %s (%s) - cost: %d' % (count, card.activations, card, card.short_desc, card.cost))
            sys.stdout.write(colorama.Style.RESET_ALL)
