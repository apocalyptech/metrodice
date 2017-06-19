Metro Dice
==========

Metro Dice is an implementation of the board/card game Machi Koro. 
Machi Koro was designed by Masao Suganuma and published by IDW Games,
Grounding Inc, and Pandasaurus Games in the U.S., and many others elsewhere.

https://boardgamegeek.com/boardgame/143884/machi-koro

Currently there's only text-mode clients available.  The preferred one is
a "TUI" (Terminal User Interface), and can be run with `metrodice-tui.py`.
The other is an even-more-basic console app which can be run with
`metrodice-cli.py`.  The TUI app is more featureful, though.  At the
moment, though, they're both only a pass-and-play apps, so if you wanted
to play with a friend you'd have to be sitting right next to each other,
at which point you may as well just play a physical Machi Koro instead,
yeah?  I suppose you could share a tmux or screen session.

Metro Dice is programmed in Python (currently only tested in Python 3,
though I don't think I'm using anything which would cause problems in
Python 2).  The TUI client uses Python's "urwid" module, and the more-basic
CLI app uses Python's "colorama" module for coloring.

Metro Dice is, charitably, a work in progress.  It was programmed
barreling headlong into the code without much, if any, thought as to
overall architecture and sensibility.  At the moment, the players,
expansion to use, and market style to use are just hardcoded up at the
top of the `TextMode` or `CLI` classes (depending on which app you launch).
Extremely questionable implementation details abound.  In its favor, though:

1) It *does* work.
2) There's at least a bare minimum of backend/frontend separation
   (implementing a GUI frontend shouldn't require any modifications to
   the game logic files.
3) Unit tests are coming along - at the moment they cover cards, markets,
   and actions, but is missing the core game library.  It's getting there,
   slowly!

At the moment it implements the base Machi Koro game plus the *Harbor*
expansion, which is the mode that's enabled by default.  It additionally
supports using a *Bright Lights, Big City* style market, though you'll have
to change the definition in `CLI` to enable that.  I'll likely be
adding in *Millionaire's Row* cards as well, and probably a full *Bright
Lights, Big City* setting.  Also, you know, making it an actually
reasonable app instead of a glorified bit of spaghetti.
