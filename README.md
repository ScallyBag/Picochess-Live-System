PicoChess
=========

Picochess 2.01 (personal edition) 
--------------------------------
Picochess V 0.9N with the following changes/enhancements: 

Following enhancements to the 0.9N version have been implemented:

        0.  Version set to 1.0 (finally ;-)
        1.  Voice announcements even if time < 1 minute
        2.  Possibility to continue playing even if one player runs out of time
        3.  Pre-Moves: Computer and user moves can be done in rapid sequence
            (no need to wait for registration of computer move). Even the
            own move could be played before computer move - it doesn't matter
        4.  New flexible ponder mode: no more checks if valid moves, position can
            be setup without any restrictions (of course it must be a legal one)
            Makes analysis and playing different variants much easier
        5.  Remote mode working again (without room handling, see menu.py)
        __________________________________________________________________________ 
        
        6.  Version set to 2.0 
        7.  Framework for adding (more or less funny) speech comments based on
            various events
        8.  Rolling display of time/score/depth/hintmove in Ponder On or Normal Mode
        9.  Continue directly after start with an interrupted game if board still shows
            last position by reading the last games pgn file
        10. New cool training mode with training options (with big thanks to Wilhelm!!!)
        11. Configuration parameters for all 1.00/2.00 enhancements in picochess.ini
        12. Various bug fixes (eg. pressing the outer buttons for quick restart
            instead of shutdown like it was intended, calc. error in evaluation)
            Again: big thanks to Wilhelm!
        13. Renaming of the play modes! Now we have:
            New mode name                                         Old mode name
            a5 NORMAL (rolling info display off by default)       NORMAL
            b5 PONDER ON (rolling info display on by default)     BRAIN
            c5 MOVE HINT                                          ANALYSIS
            d5 EVAL.SCORE                                         KIBITZ
            e5 OBSERVE                                            OBSERVE
            f5 ANALYSIS (flexible option on by default)           PONDER
            g5 TRAINING (this is new in 2.00)                       -
            h5 REMOTE (working again from 1.00 on)                REMOTE
        14. Version set to 2.01
        15. Support of changing the voice volume via menu option and picochess.ini
        
        
If you don't want to replicate/replace the whole repository on your Pi and only if you are already on my personal picochess version 1.0, you only need to replace the following files in the picochess directory:

Files to be replaced in…

... /opt/picochess:
- picochess.py
- picochess.ini  (just adjust your own one and add the new lines at the end of the default picochess.ini.example_v2 )
- utilities.py
- timecontrol.py
- pgn.py
- server.py

… /opt/picochess/dgt:
- display.py
- menu.py
- pi.py
- translate.py
- translate_old.py (use this one instead of translate.py if you want to keep the old mode names)
- util.py
- api.py

… /opt/picochess/talker:
- picotalker.py

Unfortunately picochess (version 0.9N and this 2.0 version) is at the moment not compatible to python-chess version 24.0 and higher so don't upgrade python-chess.
You even should stay with 22.1 version because of incompatibilties with web server display and elo engines.  
 

[![Join the chat at https://gitter.im/picochess/Lobby](https://badges.gitter.im/picochess/Lobby.svg)](https://gitter.im/picochess/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Stand alone chess computer based on [Raspberry Pi](http://www.raspberrypi.org/) and [DGT electronic chess board](http://www.dgtprojects.com/index.php/products/electronic-boards).

See [installation instructions](http://docs.picochess.org/en/latest/installation.html), [manual](http://docs.picochess.org), and [website](http://www.picochess.org).

[![Code Health](https://landscape.io/github/jromang/picochess/master/landscape.png)](https://landscape.io/github/jromang/picochess/master) [![Documentation Status](https://readthedocs.org/projects/picochess/badge/?version=latest)](https://readthedocs.org/projects/picochess/?badge=latest)
