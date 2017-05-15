#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:

# Metro Dice interface in urwid
# http://urwid.org/

import sys
import urwid

from . import markets, actionlib
from .gamelib import Player, Game
from .cards import Card, expansion_base, expansion_harbor

class TextApp(object):
    """
    Urwid interface to playing Metro Dice.

    This is all super hideous at the moment, should really have some smarter classes which
    inherit from urwid base classes, etc.  Requires a pretty big xterm too.  It is nevertheless
    nicer to use than what cli.py currently provides.
    """

    def __init__(self):

        self.players = []
        self.players.append(Player(name='CJ'))
        self.players.append(Player(name='Bob'))

        #expansion = expansion_base
        expansion = expansion_base + expansion_harbor

        #market = markets.MarketBase
        market = markets.MarketHarbor
        #market = markets.MarketBrightLights

        self.game  = Game(self.players, expansion, market)

        self.main_header = urwid.Text('', wrap='clip')
        header_widget = urwid.Padding(urwid.AttrMap(self.main_header, 'main_header'))

        self.main_footer = urwid.Text('', wrap='clip')
        footer_widget = urwid.Padding(urwid.AttrMap(self.main_footer, 'main_footer'))

        player_info_containers = []
        self.player_info_piles = {}
        self.player_info_attr = {}
        for player in self.game.players:
            self.player_info_piles[player] = urwid.Pile([])
            self.player_info_attr[player] = urwid.AttrMap(urwid.LineBox(self.player_info_piles[player], title='Player: %s' % (player)), 'player_box')
            player_info_containers.append(self.player_info_attr[player])

        player_info_columns = urwid.Columns(player_info_containers)

        self.market_info_pile = urwid.Pile([])
        market_container = urwid.LineBox(self.market_info_pile, title='Market')

        player_info_pile = urwid.Pile([])
        player_info_pile.contents.append(self.status_line('event_header', 'Events:'))

        self.event_walker = urwid.SimpleFocusListWalker([])
        self.event_listbox = urwid.ListBox(self.event_walker)
        player_info_pile.contents.append((self.event_listbox, ('given', 8)))

        player_info_pile.contents.append((urwid.Divider('-'), ('pack', None)))

        self.action_prompt = urwid.Text(('action_header', 'Available Actions:'), wrap='clip')
        player_info_pile.contents.append((self.action_prompt, ('pack', None)))
        player_info_pile.contents.append((urwid.Divider(), ('pack', None)))
        self.action_walker = urwid.SimpleFocusListWalker([])
        self.action_listbox = urwid.ListBox(self.action_walker)
        player_info_pile.contents.append((self.action_listbox, ('weight', 1)))
        
        market_other_columns = urwid.Columns([market_container, player_info_pile])

        self.main_pile = urwid.Pile([player_info_columns, market_other_columns])
        
        main_frame = urwid.Frame(self.main_pile, header_widget, footer_widget)

        # Set focus into our action menu
        main_frame.focus_position = 'body'
        self.main_pile.focus_position = 1
        market_other_columns.focus_position = 1
        player_info_pile.focus_position = 5

        palette = [
                ('main_header', 'white', 'dark blue'),
                ('main_footer', 'white', 'dark blue'),
                ('player_box', 'white', 'black'),
                ('player_box_current', 'light green', 'black'),
                ('player_box_info', 'white', 'black'),
                ('event_header', 'yellow', 'black'),
                ('event_turn_change', 'light magenta', 'black'),
                ('event_line', 'dark cyan', 'black'),
                ('action_header', 'yellow', 'black'),
                ('money', 'light green', 'black'),
                ('landmark_bought', 'yellow,bold', 'black'),
                ('landmark_available', 'white', 'black'),
                ('landmark_unavailable', 'dark gray', 'black'),
                ('card_green', 'light green', 'black'),
                ('card_blue', 'light blue', 'black'),
                ('card_red', 'light red', 'black'),
                ('card_purple', 'light magenta', 'black'),
                ('card_unavailable', 'dark gray', 'black'),
                ('action_available', 'light green', 'black'),
                ('action_selected', 'black', 'dark green'),
                (None, 'white', 'black'),
            ]

        self.update_display()
        self.loop = urwid.MainLoop(main_frame, palette)
        self.cursor_save = urwid.escape.SHOW_CURSOR
        urwid.escape.SHOW_CURSOR = ''
        self.loop.run()

    def exit_main_loop(self, button):
        """
        Exit the program
        """
        self.loop.screen.write( self.cursor_save )
        raise urwid.ExitMainLoop()

    def update_display(self):
        """
        Updates various things what might need updating
        """
        self.update_header_footer()
        self.update_players()
        self.update_market()
        self.update_events()
        self.update_actions()

    def update_header_footer(self):
        """
        Updates our header and footer
        """
        self.main_header.set_text(
            ' Metro Dice | Using Expansion: %s | Using Market: %s' % (self.game.expansion, self.game.market)
        )
        self.main_footer.set_text(' Current Player: %s | Status: %s' % (self.game.current_player, self.game.state_str()))

    def update_players(self):
        """
        Update our player information
        """
        for player in self.players:

            if player == self.game.current_player:
                self.player_info_attr[player].set_attr_map({None: 'player_box_current'})
            else:
                self.player_info_attr[player].set_attr_map({None: 'player_box'})

            pile_widget = self.player_info_piles[player]
            new_contents = []
            new_contents.append(self.status_line('money', 'Money: $%d' % (player.money)))
            new_contents.append(self.status_line('player_box_info', 'Landmarks:'))
            for landmark in sorted(player.landmarks):
                if landmark.constructed:
                    new_contents.append(self.status_line('landmark_bought', ' * %s (%s)' % (landmark, landmark.short_desc)))
                else:
                    if landmark.cost > player.money:
                        style = 'landmark_unavailable'
                    else:
                        style = 'landmark_available'
                    new_contents.append(self.status_line(style, ' * ($%d) %s (%s)' % (landmark.cost, landmark, landmark.short_desc)))

            # This bit is dumb; massaging our list of cards into a more market-like
            # structure
            new_contents.append(self.status_line('player_box_info', 'Cards:'))
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
                new_contents.append(self.status_line(
                    self.style_card(card),
                    ' * %dx %s %s (%s) [%s]' % (inventory_flip[card], card.activations, card, card.short_desc, card.family_str())
                ))

            pile_widget.contents = new_contents

    def update_market(self):
        """
        Update our market information
        """
        new_contents = []
        cards_available = self.game.market.cards_available()
        for card in sorted(cards_available.keys()):
            count = cards_available[card]
            if card.cost > self.game.current_player.money:
                style='card_unavailable'
            elif card.family == Card.FAMILY_MAJOR and self.game.current_player.has_card(card):
                style='card_unavailable'
            else:
                style=self.style_card(card)
            new_contents.append(self.status_line(
                style,
                ' * $%d %dx %s %s (%s) [%s]' % (card.cost, count, card.activations, card, card.short_desc, card.family_str())
            ))
        self.market_info_pile.contents = new_contents

    def update_events(self):
        """
        Updates our events/errors
        """

        for event in self.game.consume_events():
            if event[:11] == 'Turn change':
                style = 'event_turn_change'
            else:
                style = 'event_line'
            self.event_walker.append(urwid.Text((style, event), wrap='clip'))
            self.event_listbox.focus_position = len(self.event_walker) - 1

    def choose_action(self, button, action):
        """
        Player has chosen an action
        """
        action.do_action()
        self.update_display()

    def update_actions(self):
        """
        Updates the actions we have available
        """

        self.action_prompt.set_text(('action_header', '%s ($%d) - Available Actions:' % (
            self.game.current_player, self.game.current_player.money)))

        # Remove all current actions (this is a bit hokey)
        for button in list(self.action_walker):
            self.action_walker.remove(button)

        # Add new ones.
        for action in self.game.actions_available:
            button = urwid.Button(action.desc)
            if type(action) == actionlib.ActionBuyCard:
                attr_map = self.style_card(action.card)
            else:
                attr_map = 'action_available'
            urwid.connect_signal(button, 'click', self.choose_action, action)
            self.action_walker.append(urwid.AttrMap(button, attr_map, focus_map='action_selected'))

        button = urwid.Button('Quit')
        urwid.connect_signal(button, 'click', self.exit_main_loop)
        self.action_walker.append(urwid.AttrMap(button, 'action_available', focus_map='action_selected'))

    def status_line(self, style, text):
        """
        Returns a single line of status that we'd plug into an urwid.Pile
        """
        return (urwid.Text((style, text), wrap='clip'), ('pack', None))

    def style_card(self, card):
        """
        Returns the style we'll use for the given card
        """
        if card.color == Card.COLOR_BLUE:
            return 'card_blue'
        elif card.color == Card.COLOR_RED:
            return 'card_red'
        elif card.color == Card.COLOR_GREEN:
            return 'card_green'
        elif card.color == Card.COLOR_PURPLE:
            return 'card_purple'
        else:
            return None
