from field import field
from functools import reduce
import figure as figs
from moves import Moves_history
from copy import deepcopy
from moves import ImpossibleMove, UndoMove, ExitGame

#some change
class Chess(field):
    # start_seq  = ['e2','e4','e7','e5','d1','h5','a7','a6','f1','c4','a6','a5'][::-1]
    # start_seq = ['e2','e4','e7','e5','g1','f3','g8','f6','f1','c4','f8','c5'][::-1]
    # start_seq = ['h2','h4','g7','g5','h4','g5','e7','e5','g5','g6','e8','e7','g6','g7','g8','f6'][::-1]
    start_seq = []
    def __init__(self):
        self.move = 1
        self.turn = "white"
        super().__init__()
        self._moves_history = Moves_history()
        self._color_turn = "white"
        self._in_check = False
        self._GAME_IN_PROCESS = True

    def _make_move(self, from_sq, to_sq):
        if(to_sq in self._possible_moves):
            self._moves_history.push(self[from_sq],
                                     self[to_sq],
                                     from_sq,
                                     to_sq)

            self[to_sq] = self[from_sq]
            self[from_sq] = None
            self[to_sq]._pos = to_sq
        else:
            raise ImpossibleMove("Impossible move")

        # Make sure your King is not in check after move
        if(self._check_for_check(self._color_turn)):
            self[to_sq] = deepcopy(self._moves_history[-1]["captured_piece"])
            self[from_sq] = deepcopy(self._moves_history[-1]["piece"])
            self._moves_history.pop()

            raise ImpossibleMove("ImpossibleMove")
        
        # Remove initial 2-square forward moves from Pawn
        if('p' in self[to_sq].prefix and not self[to_sq]._been_moved):
            self[to_sq].moves = self[to_sq].moves[:-1]
        
        # Check and process castling
        if('K' in self[to_sq].prefix and not self[to_sq]._been_moved):
            if(to_sq in ('g1', 'c1', 'g8', 'c8')):
                if(to_sq[0] == 'g'):
                    fr_rook = 'h' + to_sq[1]
                    to_rook = 'f' + to_sq[1]
                else:
                    fr_rook = 'a' + to_sq[1]
                    to_rook = 'd' + to_sq[1]
                
                print(fr_rook, to_rook)
                print(self[fr_rook], self[fr_rook].prefix)

                if((self[fr_rook] is not None) and ("R" in self[fr_rook].prefix) and \
                        not self[fr_rook]._been_moved):
                    self[to_rook] = self[fr_rook]
                    self[fr_rook] = None
                    self[to_rook]._pos = to_rook
                    self._moves_history[-1:"is_castling"] = True
                    self._moves_history[-1:"castle_rook_from"] = fr_rook
                    self._moves_history[-1:"castle_rook_to"] = to_rook
                else:
                    self[to_sq] = deepcopy(self._moves_history[-1]["captured_piece"])
                    self[from_sq] = deepcopy(self._moves_history[-1]["piece"])
                    self._moves_history.pop()
                    raise ImpossibleMove("ImpossibleMove")
            self[to_sq].moves = self[to_sq].moves[:-2]
                    
        # Check for Pawn promotion
        if('p' in self[to_sq].prefix and to_sq[1] in ('1','8')):
            self[to_sq] = figs.Queen(self[to_sq]._color,
                                     to_sq)
        self[to_sq]._been_moved = 1

    def _undo_move(self):
        if(self._color_turn == "white" and self.move == 1):
            return

        ( (fr, to), moved_piece, capt_piece, is_castle, (fr_rook, to_rook) ) = self._moves_history.pop()

        self[fr] = moved_piece
        self[to] = capt_piece
        
        if(is_castle):
            self[fr_rook] = self[to_rook]
            self[to_rook] = None
            self[fr_rook]._pos = fr_rook

        if(self._color_turn == "white"):
            self.move-=1
        self._color_turn = self.op_color(self._color_turn)
        self._in_check = self._check_for_check(self._color_turn)

    def _get_list_of_figures(self, color=None):
        all_sq = reduce(lambda x, y: x+y,
                        [list(i.values()) for i in self._field.values()])
        all_sq = list(filter(lambda x: x is not None, all_sq))
        if(color):
            return list(filter(lambda x: x._color == color, all_sq))
        return all_sq

    def _update_possible_moves(self, from_sq):
        self._possible_moves = []
        for piece_move in self[from_sq].moves:
            self._possible_moves += piece_move.get_possible(from_sq, self)

        if(not self._possible_moves):
            raise ImpossibleMove("Impossible move")

    def _is_possible_move(self, from_sq, to_sq):
        try:
            self._make_move(from_sq, to_sq)
            if(self._color_turn == "white"):
                self._color_turn = "black"
            else:
                self.move += 1
                self._color_turn = "white"
            self._undo_move()
        except ImpossibleMove as IM:
            return False
        return True


    def _check_for_check(self, color):
        king_piece = next(filter(lambda x: isinstance(x, figs.King),
                                 self._get_list_of_figures(color)))

        for piece in self._get_list_of_figures(self.op_color(color)):
            possible_capt = []
            for piece_move in piece.moves:
                possible_capt += piece_move.get_possible_capture(
                    piece._pos, self)
            if(king_piece._pos in possible_capt):
                return True
        return False

    def _check_for_mate(self, color):
        king_piece = next(filter(lambda x: isinstance(x, figs.King),
                                 self._get_list_of_figures(color)))

        for ind, piece in enumerate(self._get_list_of_figures(color)):
            try:
                self._update_possible_moves(piece._pos)
            except ImpossibleMove as IM:
                continue

            for to in self._possible_moves:
                pos_from = piece._pos
                capt = self[to]
                self[to] = self[pos_from]
                self[pos_from] = None
                self[to]._pos = to

                if(self._check_for_check(color)):
                    self[pos_from] = self[to]
                    self[pos_from]._pos = pos_from
                    self[to] = capt
                else:
                    self[pos_from] = self[to]
                    self[pos_from]._pos = pos_from
                    self[to] = capt
                    return 0
        return 1

    @staticmethod
    def op_color(color):
        if(color == "white"):
            return "black"
        return "white"

    def start_game(self):
        while self._GAME_IN_PROCESS:
            try:
                self._main_loop()
                if(self._color_turn == "white"):
                    self._color_turn = "black"
                else:
                    self.move += 1
                    self._color_turn = "white"

            except ImpossibleMove as VE:
                print("Impossible Move")
                input("Press enter to proceed...")
            except KeyError as KE:
                print("Ошибка ввода")
            except UndoMove as UM:
                print("Undoing last move")
                self._undo_move()
            except ExitGame as EG:
                print("Exiting the game")
                return

        self._render_board()
        print("Game over")
        print(f"{self.op_color(self._color_turn)} is victorious!")
        input("Press enter to exit...")

    def _main_loop(self):
        self._render_board()

        print(f"King in check: {self._in_check}")
        print(f"Move: {self.move}. It's {self._color_turn}'s turn")
        
        if(self.start_seq):
            fr = self.start_seq.pop()
        else:
            fr = input("Which piece to move:").lower()
        
        if("undo" in fr):
            raise UndoMove();
        if("exit" in fr):
            self._GAME_IN_PROCESS = False
            raise ExitGame()
        if(not fr):
            raise ImpossibleMove("ImpossibleMove")
        if(self[fr] is None):
            raise ImpossibleMove("Impossible move")
        if(self[fr]._color != self._color_turn):
            raise ImpossibleMove("Impossible move")

        self._update_possible_moves(fr)
        for ind, to_move in reversed(list(enumerate(self._possible_moves))):
            if(not self._is_possible_move(fr, to_move)):
                del self._possible_moves[ind]
        if(not self._possible_moves):
            raise ImpossibleMove("Impossible move")
        self._render_board(show_possible=1)
        
        if(self.start_seq):
            to = self.start_seq.pop()
        else:
            to = input("Where to move:").lower()

        self._make_move(fr, to)

        self._in_check = self._check_for_check(self.op_color(self._color_turn))

        if(self._in_check):
            if(self._check_for_mate(self.op_color(self._color_turn))):
                self._GAME_IN_PROCESS = False



if __name__ == "__main__":
    game = Chess()
    game.start_game()
