PicoChess
=========

Picochess 2.0 (personal edition) 
--------------------------------
Picochess V 0.9N with the following changes/enhancements: 



If you don't want to replicate/replace the whole repository on your Pi and only if you are already on my personal picochess version 1.0, you only need to replace the following files in the picochess directory:

Files to be replaced in…

... /opt/picochess:
- picochess.py
- picochess.ini  (just adjust your own one and add the new lines at the end of the default picochess.ini.example_v2 )
- utilities.py
- timecontrol.py

… /opt/picochess/dgt:
- display.py
- menu.py
- pi.py
- translate.py
- translate_old.py (use this one instead of translate.py if you want to keep the old mode names)
- util.py

… /opt/picochess/talker:
- picotalker.py

Unfortunately picochess (version 0.9N and this 2.0 version) is at the moment not compatible to python-chess version 24.0 and higher so don't upgrade python-chess.
You even should stay with 22.1 version because of incompatibilties with web server display and elo engines.  
 

[![Join the chat at https://gitter.im/picochess/Lobby](https://badges.gitter.im/picochess/Lobby.svg)](https://gitter.im/picochess/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Stand alone chess computer based on [Raspberry Pi](http://www.raspberrypi.org/) and [DGT electronic chess board](http://www.dgtprojects.com/index.php/products/electronic-boards).

See [installation instructions](http://docs.picochess.org/en/latest/installation.html), [manual](http://docs.picochess.org), and [website](http://www.picochess.org).

[![Code Health](https://landscape.io/github/jromang/picochess/master/landscape.png)](https://landscape.io/github/jromang/picochess/master) [![Documentation Status](https://readthedocs.org/projects/picochess/badge/?version=latest)](https://readthedocs.org/projects/picochess/?badge=latest)
