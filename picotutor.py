#!/usr/bin/env python3

# Copyright (C) 2013-2019 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
#                         Jürgen Précour (LocutusOfPenguin@posteo.de)
#                         Molli (and thanks to Martin  for his opening
#                         identification code)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import chess
import chess.uci
import chess.engine
import math
from random import choice
from random import randint
from dgt.util import PicoComment

# PicoTutor Constants
import picotutor_constants as c

"""
c.LOW_DEPTH            = 5  ## for obvious moves calculation
c.DEEP_DEPTH           = 19
c.NUM_THREADS          = 1

c.VERY_BAD_MOVE_TH     = 2.2 ## diff curr to best move
c.BAD_MOVE_TH          = 1.3 ## diff curr to best move
c.DUBIOUS_TH           = 0.3 ## ?!

c.VERY_GOOD_MOVE_TH    = 0 ## diff to best move
c.GOOD_MOVE_TH         = 0.3 ## diff to best move
c.INTERESTING_TH       = 0.3 ## !?

c.POS_INCREASE         = 0.5 ## for history diffs and ?!
c.POS_DECREASE         = -0.5 ## for history diffs and !?

c.VERY_GOOD_IMPROVE_TH = 2.0 ## for low_deep_diff
c.GOOD_IMPROVE_TH      = 1.5 ## for low_deep_diff
c.UNCLEAR_DIFF         = 0.7 ## unclear position & move


    http://www2.eng.cam.ac.uk/~tpl/chess/annotation.html
    
    Computers and Chess Annotation
    
    Δ1 -    The difference between move value at min. ply for the current move and best move.
    
    Δ2 -    The difference between move value at max. ply for the current move and best move.
    
    ΔS -    The difference between the current move's value at max. and min. ply.
    
    G1 -    The model's gradient at min. ply
    
    G2 -    The model's gradient at max. ply
    
    K - The model's curvature.
    
    Classification occurs as follows:
    
    Blunders (?, ??) are characterised as being clearly much worse than the optimal move in a given position. Hence, we define a move as a blunder if both Δ1 and Δ2 are greater than a certain threshold - for example, I have found thresholds of 50 for ? and 150 for ?? to work well in test games.
    
    Exceptional Moves (!, !!) are always ultimately good moves (hence Δ2 must either be small, or, especially in the case of !!, zero), and show improvement with ply (ie. ΔS is positive and, in the case of !!, greater than a positive threshold). We need to take care that the move is not too obviously good - thus we require Δ1 to be greater than a threshold, such that the move was not clearly the best at first glance. We also don't want the move to rapidly become good, as this makes the move's goodness clear to the player without very intensive evaluation - we therefore require the model's curvature to be concave, linear, or at most shallowly convex, otherwise the move's true nature becomes clear at relatively low ply.
    
    Unclear Moves (?!, !?) need to be both sufficiently good/bad-seeming to warrant a mark, and sufficiently volatile to warrant denotation as being unclear. We detect the apparent initial interest in the move by a high magnitude of G1 - very positive initial gradient makes a move look as though it might be exceptional (!?), while very negative initial gradient makes the move look as though it might be a blunder (?!). We detect the volatility by the curvature - we demand that the curvature be both high in magnitude and acting in the opposite direction to the initial gradient. Finally, we need the max. ply value to be reasonably close to the initial value for the move (ie. the magnitude of ΔS needs to be low) - if it's a lot higher, then the move is better described as exceptional, if a lot lower, the move is more accurately a blunder.
    
    
    
    [Objectively] best move - the move which (as far as can be determined) leads to the best possible position
    Good move - a move which (as far as can be determined) is close to being the objectively best move
    Obvious move - a move which using an n-ply analysis (where n is small) is good
    Easy move - a move which using an n-ply analysis (where n is small) is close to the best move using an n-ply analysis
    Risky move - a move which leads to a much more unclear position
    Double-edged move - leading to a complicated position
    Quiet move - a move which doesn't lead to a more unclear position and doesn't have an immediate threat.
    
    ! - a move which is much better than the alternatives and not obvious
    !! - a move which is much better than the alternatives and not at all obvious
    ? - a move which is much worse than at least one alternative
    ?? - a blunder: a move which is much worse than at least one alternative, converting a win into a draw/loss or a draw into a loss
    !? - not objectively best, but good for pragmatic reasons.
    ?! - far from objectively best, but maybe good for pragmatic reasons.
    
    
    
    Unclear position - a position where few obvious moves are good.
    
    Complicated position - a position where some of the obvious moves are good and some bad.
    
"""

class PicoTutor:
    
    def __init__(self, i_engine_path = '/opt/picochess/engines/armv7l/a-stockf', i_player_color = chess.WHITE, i_fen = '', i_comment_file = '', i_lang = 'en'):
        self.log_file_name  = "picotutor-log.txt"
        self.log_file = ''
        self.user_color = i_player_color
        self.max_valid_moves = 200
        self.engine_path = i_engine_path
        self.engine = chess.uci.popen_engine(i_engine_path)
        self.engine2 = chess.uci.popen_engine(i_engine_path)
        self.engine.uci()
        self.engine2.uci()
        self.engine.setoption({"MultiPV": self.max_valid_moves})
        self.engine.setoption({"Contempt": 0})
        self.engine.setoption({"Threads": c.NUM_THREADS})
        self.engine2.setoption({"MultiPV": self.max_valid_moves})
        self.engine2.setoption({"Contempt": 0})
        self.engine2.setoption({"Threads": c.NUM_THREADS})
        self.engine.isready()
        self.engine2.isready()
        self.info_handler = chess.uci.InfoHandler()
        self.info_handler2 = chess.uci.InfoHandler()
        self.engine.info_handlers.append(self.info_handler)
        self.engine2.info_handlers.append(self.info_handler2)
        self.history = []
        self.history2 = []
        self.history.append((0, chess.Move.null(), 0.00, 0))
        self.history2.append((0, chess.Move.null(), 0.00, 0))
        self.pv_best_move = []
        self.pv_user_move = []
        self.pv_best_move2 = []
        self.pv_user_move2 = []
        self.hint_move = chess.Move.null()
        self.mate = 0
        self.legal_moves = []
        self.legal_moves2 = []
        self.op=[]
        self.last_inside_book_moveno = 0
        self.alt_best_moves = []
        self.comments = []
        self.comment_no = 0
        self.comments_all = []
        self.comment_all_no = 0
        self.lang = i_lang
        self.pos = False
        self.watcher_on = True
        self.coach_on = False
        self.explorer_on = False
        self.comments_on = False
        
        self.open_log()
        
        try:
            self.book_data = open("chess-eco_pos.txt").readlines()
        except:
            self.log("ECO opening book not found!")
            self.book_data = []
        
        try:
            self.book_fen_data = open("opening_name_fen.txt").readlines()
        except:
            self.log("ECO FEN opening book not found!")
            self.book_fen_data = []
        
        self.log("comment_file %s" % i_comment_file)
        if i_comment_file:
            try:
                self.comments = open(i_comment_file).readlines()
            except:
                self.log("Game commentary file not found!")
                self.comments = []

            if self.comments:
                self.comment_no = len(self.comments)
                self.log("found %s comments" % self.comment_no)
                    
        try:
            general_comment_file = '/opt/picochess/engines/armv7l/general_game_comments_' + i_lang + '.txt'
            self.comments_all = open(general_comment_file).readlines()
        except:
            self.log("General game commentary file not found!")
            self.comments_all = []
        
        if self.comments_all:
            self.comment_all_no = len(self.comments_all)
            self.log("found %s comments" % self.comment_all_no)
    
        if i_fen:
            self.board = chess.Board(i_fen)
        else:
            self.board = chess.Board() ## starting position if no other set_position command comes

    def set_status(self, watcher=False, coach=False, explorer=False, comments=False):
        
        if (self.watcher_on or self.coach_on):
            self.watcher_on = watcher
            self.coach_on = coach
            self.explorer_on = explorer
            self.comments_on = comments
            if (watcher or coach):
                self.reset()
            else:
                self.stop()
        else:
            self.watcher_on = watcher
            self.coach_on = coach
            self.explorer_on = explorer
            self.comments_on = comments
            if (watcher or coach):
                self.reset()
            else:
                pass

    def get_game_comment(self, pico_comment=PicoComment.COM_OFF, com_factor=0):
        self.log("**** start get game comment")
        self.log("pico_comment= %s" % pico_comment)
        self.log("com_factor= %s" % str(com_factor))
        max_range= 0
        max_range_all= 0
        range_fac = 0
        
        if com_factor == 0:
            return ''
        range_fac = round(100/com_factor)
        max_range = self.comment_no * range_fac
        max_range_all = self.comment_all_no * range_fac
            
        if pico_comment == PicoComment.COM_ON_ENG:
        ## get a comment by pure chance
            if self.comments and self.comment_no > 0:
                index = randint(0, max_range)
                if index > self.comment_no-1:
                      return ''
                self.log("found game comment %s" % self.comments[index])
                return self.comments[index]
            else:
                return ''
        elif pico_comment == PicoComment.COM_ON_ALL:
            ## get a comment by pure chance
            self.log("General Comment")
            if self.comments and self.comment_no > 0:
                index = randint(0, max_range)
                if index > self.comment_no-1:
                    return ''
                self.log("found game comment %s" % self.comments[index])
                return self.comments[index]
            else:
                if self.comments_all and self.comment_all_no > 0:
                    index = randint(0, max_range_all)
                    if index > self.comment_all_no-1:
                        return ''
                    self.log("found game comment %s" % self.comments_all[index])
                    return self.comments_all[index]
                else:
                    return ''

    def init_comments(self, i_comment_file):
        self.comments = []
        self.comment_no = 0
        self.log("new comment_file %s" % i_comment_file)
        if i_comment_file:
            try:
                self.comments = open(i_comment_file).readlines()
            except:
                self.log("Game commentary file not found!")
                self.comments = []
            
            if self.comments:
                self.comment_no = len(self.comments)
                self.log("found %s comments" % self.comment_no)

        else:
            self.comments = []

    def get_opening(self):

        diff = self.board.fullmove_number - self.last_inside_book_moveno
        inside_book_opening = False
        
        self.log("++++++++++get_opening start++++++++++++")
        
        id = '', '', ''
        
        if self.op == [] or diff > 2:
            return(id[2], id[0], id[1], inside_book_opening)

        played = '%s' % (' '.join(self.op))
        
        ##self.log("played:%s", played)
        
        for l in self.book_data:
            h5 = l.split('"')
            if len(h5) > 5:
                eco, name, mv = h5[1], h5[3], h5[5]
                
                if played[:len(mv)] == mv:
                    ##self.log("match1")
                    if len(mv) > len(id[1]):
                        id = name, mv, eco
                        ##self.log("match2")
        
        halfmoves = 2 * self.board.fullmove_number
        
        if self.board.turn:
            halfmoves -= 2
        else:
            halfmoves -= 1
        if halfmoves < 0:
            halfmoves = 0
        
        self.log("halfmoves:%s" % halfmoves)

        try:
            help = id[1].split()
        except:
            help = ''

        if halfmoves <= len(help):
            inside_book_opening = True
            self.last_inside_book_moveno = self.board.fullmove_number
        else:
            ## try opening name based on FEN
            op_name = ''
            i_book = False
          
            op_name, i_book = self.get_fen_opening()
            if i_book and op_name:
                id = op_name, id[1], id[2]
                ##id[2] = '??'
                inside_book_opening = True
                self.last_inside_book_moveno = self.board.fullmove_number
            else:
                inside_book_opening = False

        self.log("insidebook: %s" % inside_book_opening)
        if id[0]:
            self.log("opening: %s" % id[0])
        
        ##self.log("eco=%s, name=%s, moves=%s, book=%s", id[2], id[0], id[1], inside_book_opening)
        self.log("+++++++++get_opening end+++++++++++++")
        return(id[2], id[0], id[1], inside_book_opening)
  
    def get_fen_opening(self):
        
        inside_book_opening = False
        
        self.log("++++++++++++get_fen_opening start++++++++++++")
        
        fen = self.board.board_fen()
        
        self.log("get_fen_opening fen= %s" % fen)
        
        if not fen:
            return("", False)
    
        index = 0
        op_name = ''
        
        for line in self.book_fen_data:
            line_list = line.split()
            if line_list[0] == fen:
                op_name = self.book_fen_data[index+1]
                break
            index = index + 1
                
        if op_name:
            self.log("opening: %s" % op_name)
            self.log("+++++++ get_opening end +++++++++")
            return (op_name, True)
        else:
            self.log("get_opening end")
            return ("", False)

    def open_log(self):
        try:
            self.log_file = open(self.log_file_name, 'w')
        except:
            self.log_file = ''
            print("# Could not create log file")
    
    def log(self, x):
        pass
        """
        if self.log:
           
            self.log_file.write("< %s\n" % x)
            self.log_file.flush()
        """
    
    def reset(self):
        self.pos = False
        self.log("Tutor reset / newgame")
        self.legal_moves = []
        self.legal_moves2 = []
        self.op = []
        self.user_color = chess.WHITE
        self.board = chess.Board()
        
        self.stop()
        
        self.engine = chess.uci.popen_engine(self.engine_path)
        self.engine2 = chess.uci.popen_engine(self.engine_path)
        self.engine.uci()
        self.engine2.uci()
        self.engine.setoption({"MultiPV": self.max_valid_moves})
        self.engine.setoption({"Contempt": 0})
        self.engine.setoption({"Threads": c.NUM_THREADS})
        self.engine2.setoption({"MultiPV": self.max_valid_moves})
        self.engine2.setoption({"Contempt": 0})
        self.engine2.setoption({"Threads": c.NUM_THREADS})
        self.engine.isready()
        self.engine2.isready()
        self.info_handler = chess.uci.InfoHandler()
        self.info_handler2 = chess.uci.InfoHandler()
        self.engine.info_handlers.append(self.info_handler)
        self.engine2.info_handlers.append(self.info_handler2)
        self.engine.position(self.board)
        self.engine2.position(self.board)
        
        self.history = []
        self.history2 = []
        self.history.append((0, chess.Move.null(), 0.00, 0))
        self.history2.append((0, chess.Move.null(), 0.00, 0))
        
        self.alt_best_moves = []
        self.pv_best_move = []
        self.pv_user_move = []
        self.hint_move = chess.Move.null()
        self.mate = 0
    
    def set_user_color(self, i_user_color):
        self.log("Tutor engine set_user_color: %s" %  i_user_color)

        self.pause()
        self.history = []
        self.history2 = []
        self.history.append((0, chess.Move.null(), 0.00, 0))
        self.history2.append((0, chess.Move.null(), 0.00, 0))
        self.legal_moves = []
        self.legal_moves2 = []
        self.hint_move = chess.Move.null()
        self.mate = 0
        self.pv_best_move = []
        self.pv_user_move = []
        self.hint_move = chess.Move.null()
        self.mate = 0
        
        self.user_color = i_user_color
        if  self.user_color == self.board.turn and self.board.fullmove_number > 1:
            self.start()

    def get_user_color(self):
        return(self.user_color)
        
    def set_position(self, i_fen, i_turn = chess.WHITE):
        self.log("Tutor engine set_position")
        if not(self.coach_on or self.watcher_on):
            return
        self.reset()
        
        self.board = chess.Board(i_fen)
        chess.Board.turn = i_turn
        self.engine.position(self.board)
        ##self.engine.isready()
        self.engine2.position(self.board)
        ##self.engine2.isready()
        self.pos = True
        
        if self.board.turn == self.user_color:
            ## if it is user player's turn then start analyse engine
            ## otherwise it is computer opponents turn and anaylze negine
            ## should be paused
            self.start()
        else:
            self.pause()
     

    def push_move(self, i_uci_move):
        self.log("------------------------------------")
        self.log("Tutor engine push")
        if not i_uci_move in self.board.legal_moves:
            self.log("Move is invalid: %s" % i_uci_move)
            return(False)
        
        self.op.append(self.board.san(i_uci_move))
        self.board.push(i_uci_move)
        
        if not(self.coach_on or self.watcher_on):
            return(True)
        
        self.pause()
        self.engine.position(self.board)
        self.engine.isready()
        self.engine2.position(self.board)
        self.engine2.isready()
        self.log("Valid move: %s" % i_uci_move)
        
        if self.board.turn == self.user_color:
            ## if it is user player's turn then start analyse engine
            ## otherwise it is computer opponents turn and analysis engine
            ## should be paused
            ##if not self.board.is_game_over():
            self.start()
        else:
            self.eval_legal_moves()  ## take snapshot of current evaluation
            self.eval_legal_moves2()
            self.eval_user_move(i_uci_move) ## determine & save evaluation of user move
            self.eval_user_move2(i_uci_move) ## determine & save evaluation of user move
    
        return(True)

    def pop_last_move(self):
        self.log("Tutor engine pop")
        back_move = chess.Move.null()
        self.legal_moves = []
        self.legal_moves2 = []
        
        if self.board.move_stack:
    
            back_move = self.board.pop()
            try:
                if self.op:
                    self.op.pop()
            except:
                self.op = []
            
            if not(self.coach_on or self.watcher_on):
                return chess.Move.null()
            
            self.pause()
            self.engine.position(self.board)
            self.engine.isready()
            self.engine2.position(self.board)
            self.engine2.isready()
            self.log('backmove =%s' % back_move)
            try:
                if self.history:
                    pop_move = self.history.pop()
                    if pop_move != back_move:
                        self.history.push(pop_move)
            except:
                self.history = []
                self.history.append((0, chess.Move.null(), 0.00, 0))
            
            try:
                if self.history2 and self.board.turn != self.user_color:
                    pop_move = self.history2.pop()
                    if pop_move != back_move:
                        self.history2.push(pop_move)
            except:
                self.history2 = []
                self.history2.append((0, chess.Move.null(), 0.00, 0))
            
            
            if self.board.turn == self.user_color:
                ## if it is user player's turn then start analyse engine
                ## otherwise it is computer opponents turn and analyze negine
                ## should be paused
                self.start()
            else:
                self.eval_legal_moves()
                self.eval_legal_moves2()
            
            self.log("Tutor engine pop END")
        return back_move
    
    def get_stack(self):
        return(self.board.move_stack)
    
    def get_move_counter(self):
        return(self.board.fullmove_number)
    
    def start(self):
        ## after newgame event
        if self.engine2:
            self.engine2.position(self.board)
            self.engine2.go(depth=c.LOW_DEPTH, async_callback=True)
        
        if self.engine:
            self.engine.position(self.board)
            self.engine.go(depth=c.DEEP_DEPTH, async_callback=True)
        self.log("Tutor engine started")
    
    def pause(self):
        ## during thinking time of opponent tutor should be paused
        ## after the user move has been pushed
        if self.engine:
            self.engine.stop()
        if self.engine2:
            self.engine2.stop()
        self.log("Tutor engine paused")
    
    def stop(self):
        if self.engine:
            self.engine.stop()
            self.engine.quit()
            self.engine = None
            self.info_handler = None
        if self.engine2:
            self.engine2.stop()
            self.engine2.quit()
            self.engine2 = None
            self.info_handler2 = None
        self.log("Tutor engine stopped")
    
    def print_score(self):
        if self.board.turn:
            print('White to move...')
        else:
            print('Black to move...')
            print(self.info_handler.info["pv"])
            print(self.info_handler.info["score"])

    def eval_user_move(self, user_move):
        if not(self.coach_on or self.watcher_on):
            return
        pv_no = 0
        eval = 0
        mate = 0
        loop_move = chess.Move.null()
        j = 0
        while loop_move != user_move and j < len(self.legal_moves):
            (pv_no, loop_move, eval, mate) = self.legal_moves[j]
            j = j + 1

        ## add score to history list
        if loop_move == chess.Move.null() or loop_move != user_move:
            self.history.append((pv_no, user_move, eval, mate))
        else:
            self.history.append((pv_no, loop_move, eval, mate))
        if j > 0 and pv_no > 0:
            self.pv_best_move = self.info_handler.info["pv"][1]
            self.pv_user_move = self.info_handler.info["pv"][pv_no]
        else:
            self.pv_best_move = []
            self.pv_user_move = []
        
        self.log("History:")
        self.log(self.history)
        self.log("----------------------------------")
        self.log("PV Best line: %s" % str(self.pv_best_move))
        self.log("PV User line: %s" % str(self.pv_user_move))


    def eval_user_move2(self, user_move):
        if not(self.coach_on or self.watcher_on):
            return
        pv_no = 0
        eval = 0
        mate = 0
        loop_move = chess.Move.null()
        j = 0
        while loop_move != user_move and j < len(self.legal_moves2):
            (pv_no, loop_move, eval, mate) = self.legal_moves2[j]
            j = j + 1
        
        ## add score to history list
        if loop_move == chess.Move.null() or loop_move != user_move:
            self.history2.append((pv_no, user_move, eval, mate))
        else:
            self.history2.append((pv_no, loop_move, eval, mate))
        
        if j > 0 and pv_no > 0:
            self.pv_best_move2 = self.info_handler2.info["pv"][1]
            self.pv_user_move2 = self.info_handler2.info["pv"][pv_no]
        else:
            self.pv_best_move2 = []
            self.pv_user_move2 = []
        
        self.log("History2:")
        self.log(self.history2)
        self.log("----------------------------------")
        self.log("PV Best line2: %s" % str(self.pv_best_move2))
        self.log("PV User line2: %s" % str(self.pv_user_move2))

    def sort_score(self, tupel):
        return tupel[2]

    def eval_legal_moves(self):
        if not(self.coach_on or self.watcher_on):
            return
        ##with self.info_handler:
        self.log("Analyzing moves...")
        self.legal_moves = []
        best_score = -999
        self.alt_best_moves = []
        
        pv_list = self.info_handler.info["pv"]
        
        if pv_list:
            
            ##self.log("PVs:")
            ##self.log(pv_list)
            self.log("...........................................")
            
            for pv_key, pv_list in pv_list.items():
                ##self.log("%s.Zug" %j)
                ##self.log(self.info_handler.info["pv"][j][0])
                if self.info_handler.info["score"][pv_key]:
                    score_val = self.info_handler.info["score"][pv_key]
                    move = chess.Move.null()
                    
                    score = 0
                    mate = 0
                    ##self.log(self.info_handler.info["score"][j].cp/100)
                    if score_val.cp:
                        score = score_val.cp/100
                        ##if self.user_color == chess.BLACK:
                            ##score = (-1) * score
                    if pv_list[0]:
                        move = pv_list[0]
                    if score_val.mate:
                        mate = int(score_val.mate)
                        if mate < 0:
                            score = -999
                        elif mate > 0:
                            score = 999
                    self.legal_moves.append((pv_key, move, score, mate))
                    if score >= best_score:
                        best_score = score
        
            ## collect possible good alternative moves
            self.legal_moves.sort(key = self.sort_score, reverse = True)
            for (pv_key, move, score, mate) in self.legal_moves:
                if move:
                    diff = abs(best_score - score)
                    if diff <= 0.2:
                        self.alt_best_moves.append(move)
        
        self.log("Legal Moves:")
        self.log(self.legal_moves)

        self.log("ALt. best moves:")
        self.log(self.alt_best_moves)

    def eval_legal_moves2(self):
        if not(self.coach_on or self.watcher_on):
            return
        ##with self.info_handler:
        self.log("Analyzing moves2...")
        self.legal_moves2 = []
        
        pv_list = self.info_handler2.info["pv"]
        
        if pv_list:
        
            ##self.log("PVs:")
            ##self.log(pv_list)
            self.log("...........................................")
            
            for pv_key, pv_list in pv_list.items():
                ##self.log("%s.Zug" %j)
                ##self.log(self.info_handler.info["pv"][j][0])
                if self.info_handler2.info["score"][pv_key]:
                    score_val = self.info_handler2.info["score"][pv_key]
                    move = chess.Move.null()
                    score = 0
                    mate = 0
                    ##self.log(self.info_handler.info["score"][j].cp/100)
                    if score_val.cp:
                        score = score_val.cp/100
                        ##if self.user_color == chess.BLACK:
                        ##score = -1 * score
                    if pv_list[0]:
                        move = pv_list[0]
                    if score_val.mate:
                        mate = int(score_val.mate)
                        if mate < 0:
                            score = -999
                        elif mate > 0:
                            score = 999
                    self.legal_moves2.append((pv_key, move, score, mate))
    
        self.legal_moves2.sort(key = self.sort_score, reverse = True)
        self.log("Legal Moves2:")
        self.log(self.legal_moves2)

    def get_user_move_eval(self):
        if not(self.coach_on or self.watcher_on):
            return
        self.log("Tutor get_user_move_eval")
        eval_string = ''
        best_mate = 0
        best_score = 0
        best_move = chess.Move.null()
        best_pv = []
        
        ## user move score and previoues score
        if len(self.history) > 1:
            try:
                current_pv, current_move, current_score, current_mate = self.history[-1]  ## last evaluation = for current user move
            except:
                current_pv = []
                current_move = chess.Move.null()
                current_score = 0.0
                current_mate = ''
                eval_string = ''
                return eval_string, self.mate, self.hint_move
            
            try:
                before_pv, before_move, before_score, before_mate  = self.history[-2]
            except:
                before_pv = []
                before_move = chess.Move.null()
                before_score = 0.0
                before_mate = ''
                eval_string = ''
                return eval_string, self.mate, self.hint_move
    
        else:
            current_pv = []
            current_move = chess.Move.null()
            current_score = 0.0
            current_mate = ''
            before_pv = []
            before_move = chess.Move.null()
            before_score = 0.0
            before_mate = ''
            eval_string = ''
            return eval_string, self.mate, self.hint_move
        
        self.log("**************************************")
        self.log("User move evaluation")
        self.log("**************************************")
        
        if current_pv:
            self.log("current_pv %s" % current_pv)
        if current_score:
            self.log("current_score %s" % current_score)
        if current_mate:
            self.log("current_mate %s" % current_mate)
        if before_pv:
            self.log("before_pv %s" % before_pv)
        if before_score:
            self.log("before_score %s" % before_score)
        if before_mate:
            self.log("before_mate %s" % before_mate)
        
        ## best deep engine score/move
        if self.legal_moves:
            best_pv, best_move, best_score, best_mate = self.legal_moves[0] ## tupel (pv,move,score,mate)

        if best_pv:
            self.log("best pv %s" % best_pv)
        if best_move:
            self.log("best move %s" % best_move)
        if best_score:
            self.log("best score %s" % best_score)
        if best_mate:
            self.log("best mate %s" % best_mate)
        
        ##calculate diffs based on low depth search for obvious moves
        if len(self.history2) > 0:
            try:
                low_pv, low_move, low_score, low_mate = self.history2[-1]  ## last evaluation = for current user move
            except:
                low_pv = []
                low_move = chess.Move.null()
                low_score = 0.0
                low_mate = ''
                eval_string = ''
                return eval_string, self.mate, self.hint_move
        else:
            low_pv = []
            low_move = chess.Move.null()
            low_score = 0.0
            low_mate = ''
            eval_string = ''
            return eval_string, self.mate, self.hint_move

        best_low_diff   = best_score - low_score
        best_deep_diff  = best_score - current_score
        deep_low_diff   = current_score - low_score
        score_hist_diff = current_score - before_score

        self.log("best_low_diff %s" % best_low_diff)
        self.log("best_deep_diff %s" % best_deep_diff)
        self.log("deep_low_diff %s" % deep_low_diff)
        self.log("score_hist_diff %s" % score_hist_diff)
        
        ## count legal moves in current position (for this we have to undo the user move)
        board_copy = self.board.copy()
        board_copy.pop()
        legal_no = len(list(board_copy.legal_moves))
        
        ###############################################################
        ## 1. bad moves
        ###############################################################
        eval_string = ''
        
        # Blunder ??
        ##if D1 > c.VERY_c.BAD_MOVE_TH and D2 > c.VERY_BAD_MOVE_TH:
        if best_deep_diff > c.VERY_BAD_MOVE_TH and legal_no:
            eval_string = '??'
        
        # Mistake ?
        ##elif D1 > c.BAD_MOVE_TH and D2 > BAD_MOVE_TH:
        elif best_deep_diff > c.BAD_MOVE_TH: ## and  best_low_diff  > BAD_MOVE_TH:
            eval_string = '?'
        
        # Dubious
        elif best_deep_diff > c.DUBIOUS_TH and abs(deep_low_diff) > c.UNCLEAR_DIFF and score_hist_diff > c.POS_INCREASE:
            eval_string = '?!'

        if eval_string != '':
            self.log("Intermediate Calc: bad: %s" % eval_string)
            
        ###############################################################
        ## 2. good moves
        ##############################################################
        eval_string2 = ''

        # very good moves
        if best_deep_diff <= c.VERY_GOOD_MOVE_TH and deep_low_diff > c.VERY_GOOD_IMPROVE_TH:
            if (best_score == 999 and (best_mate == current_mate)) and legal_no <= 2:
                pass
            else:
                eval_string2 = '!!'
            
        # good move
        elif best_deep_diff <= c.GOOD_MOVE_TH and deep_low_diff > c.GOOD_IMPROVE_TH and legal_no > 1:
            eval_string2 = '!'

        ## interesting move
        elif best_deep_diff < c.INTERESTING_TH and abs(deep_low_diff) > c.UNCLEAR_DIFF and score_hist_diff < c.POS_DECREASE:
            eval_string2 = '!?'

        if eval_string2 != '':
            self.log("Intermediate Calc: good: %s" % eval_string2)
            if eval_string == '':
                eval_string = eval_string2

        ## information return in addition:
        ## threat move / bestmove/ pv line of user and best pv line so picochess can comment on that as well
        ## or call a pico talker method with that information
        self.mate = current_mate
        self.hint_move = best_move

        self.log("eval_string %s" % eval_string)

        return eval_string, self.mate, self.hint_move

        
    def get_user_move_info(self):
        if not(self.coach_on or self.watcher_on):
            return
        self.log("Tutor get_user_move_info")
        return self.mate, self.hint_move, self.pv_best_move, self.pv_user_move 

    def get_pos_analysis(self):
        if not(self.coach_on or self.watcher_on):
            return
        self.log("**************************************")
        self.log("Tutor get_pos_analysis")
        ## calculate material / position / mobility / development / threats / best move / best score
        ## call a picotalker method with these information
        mate = 0
        score = 0
        
        self.eval_legal_moves()   ## take snapshot of current evaluation
        self.eval_legal_moves2()  ## take snapshot of current evaluation
        
        try:
            best_move = self.info_handler.info["pv"][1][0]
        except:
            best_move = ''
        
        try:
            best_score = self.info_handler.info["score"][1]
        except:
            best_score = 0
        
        if best_score.cp:
            score = best_score.cp/100
        if best_score.mate:
            mate = best_score.mate
        
        try:
            pv_best_move = self.info_handler.info["pv"][1]
        except:
            pv_best_move = []
        
        if mate > 0:
            score = 999
        elif mate < 0:
            score = -999

        self.log("Tutor engine best_move = %s" % str(best_move))
        self.log("Tutor engine best_score = %s" % str(score))
        self.log("Tutor engine mate = %s" % str(mate))
        return best_move, score, mate, pv_best_move, self.alt_best_moves
