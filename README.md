Metro Dice
==========

Metro Dice is an implementation of the board game Machi Koro, by Masao
Suganuma and published by IDW Games, Grounding Inc, and Pandasaurus Games
in the U.S., and many others elsewhere.

https://boardgamegeek.com/boardgame/143884/machi-koro

Currently there is only a manky CLI client, suitable for use inside a text
terminal.  At the moment it's only a pass-and-play program, so if you
wanted to play with a friend you'd have to be sitting right next to each
other, at which point you may as well just play a physical Machi Koro
instead, yeah?  I suppose you could share a tmux or screen session.

Metro Dice is programmed in Python (currently only tested in Python 3,
though I don't think I'm using anything which would cause problems in
Python 2).  The CLI client uses Python's "colorama" module for coloration.
Note that at the moment it assumes a terminal with black text and a white
background.

Metro Dice is currently barely even a prototype.  It was programmed
barreling headlong into the code without much, if any, thought as to
overall architecture and sensibility.  At the moment, the players,
expansion to use, and market style to use are just hardcoded up at the
top of the `CLI` class.  There are no unit tests, and extremely
questionable implementation details abound.  About the only thing that can
be said in its favor is that it *does* work, and that at least there's a
bare minimum of backend/frontend separation (implementing a GUI frontend
shouldn't require any modifications to `game.py` or `cards.py`).

At the moment it implements the base Machi Koro game plus the *Harbor*
expansion, which is the mode that's enabled by default.  It additionally
supports using a *Bright Lights, Big City* style market, though you'll have
to change the definition in `CLI` to enable that.  I'll likely be
adding in *Millionaire's Row* cards as well, and probably a full *Bright
Lights, Big City* setting.  Also, you know, making it an actually
reasonable app instead of a glorified bit of spaghetti.
