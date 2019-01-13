PicoChess
=========

Picochess 1.0 (personal edition) 
--------------------------------
Picochess V 0.9N with the following changes/enhancements: 

- additional opening books, 
- voice move announcements even if remaining time < 1 min.,
- possibility to continue playing even after running out of time, 
- Pre-moves (no more waiting with own move until computer move has been fully done/registered; you can even play the computer and your move in wrong sequence finally)
- Flexible Ponder Mode: No more validity checks for moves and the position can be set up without pressing any button (of course it must be a legal position). Picochess just scans the current position and will analyze it. Adding switch function to the lever in ponder mode: Change player's turn (white to move or black to move)   
- Remote play is now possible without entering a room/nickname: just switch to remote mode on on the clock/DGTPi and the opponent can enter his move via the webserver (if you forward the 8080 port in your router you can even play via internet).
Switching sides is now also possible in remote mode: just press the lever.


If you don't want to replicate/replace the whole repository on your Pi and only if you are already on picochess version 0.9N, you only need to replace the following files in the picochess directory:

1. 'picochess.py' in '/opt/picochess'
2. 'utilities.py' in '/opt/picochess'
3. 'menu.py' in '/opt/picochess/dgt'
4. 'app.js' in '/opt/picochess/web/picocweb/static/js'

Unfortunately picochess (version 0.9N and this 1.0 version) is at the moment not compatible to python-chess version 24.0 and higher so don't upgrade python-chess.
You even should stay with 22.1 version because of incompatibilties with web server display and elo engines.  
 

[![Join the chat at https://gitter.im/picochess/Lobby](https://badges.gitter.im/picochess/Lobby.svg)](https://gitter.im/picochess/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Stand alone chess computer based on [Raspberry Pi](http://www.raspberrypi.org/) and [DGT electronic chess board](http://www.dgtprojects.com/index.php/products/electronic-boards).

See [installation instructions](http://docs.picochess.org/en/latest/installation.html), [manual](http://docs.picochess.org), and [website](http://www.picochess.org).

[![Code Health](https://landscape.io/github/jromang/picochess/master/landscape.png)](https://landscape.io/github/jromang/picochess/master) [![Documentation Status](https://readthedocs.org/projects/picochess/badge/?version=latest)](https://readthedocs.org/projects/picochess/?badge=latest)
