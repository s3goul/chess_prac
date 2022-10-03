from copy import deepcopy


class move():
    _col_names = 'abcdefgh'
    _row_names = '12345678'

    def __init__(self, direction, capture=1, repeat=1, only_capture=0):
        self._dir = direction
        self._capt = capture
        self._rep = repeat
        self._only_cap = only_capture

    def get_possible(self, pos_from, game_obj):
        """ Doesnt check for check to king after move """

        possible_moves = []
        nxt_sq = pos_from
        # print(self._dir)
        while True:
            try:
                for where in self._dir:
                    if(where == "u"):
                        nxt_sq = self._up(nxt_sq)
                    elif(where == "d"):
                        nxt_sq = self._down(nxt_sq)
                    elif(where == "r"):
                        nxt_sq = self._right(nxt_sq)
                    elif(where == "l"):
                        nxt_sq = self._left(nxt_sq)

                if(game_obj[nxt_sq]):
                    if(self._capt and
                            game_obj[nxt_sq]._color != game_obj[pos_from]._color):
                        possible_moves.append(nxt_sq)
                        return possible_moves
                    else:
                        return possible_moves

                if(self._only_cap):
                    return possible_moves

            except IndexError as IR:
                # print("IR")
                return possible_moves

            possible_moves.append(nxt_sq)

            if(not self._rep):
                return possible_moves

    def get_possible_capture(self, pos_from, game_obj):
        if(self._capt):
            return self.get_possible(pos_from, game_obj)
        return []

    def _up(self, pos_from):
        if(not pos_from[1] == '8'):
            return pos_from[0] + str(int(pos_from[1]) + 1)
        raise IndexError("Out of field")

    def _down(self, pos_from):
        if(not pos_from[1] == '1'):
            return pos_from[0] + str(int(pos_from[1]) - 1)
        raise IndexError("Out of field")

    def _right(self, pos_from):
        if(not pos_from[0] == 'h'):
            return self._col_names[self._col_names.find(pos_from[0])+1]+pos_from[1]
        raise IndexError("Out of field")

    def _left(self, pos_from):
        if(not pos_from[0] == 'a'):
            return self._col_names[self._col_names.find(pos_from[0])-1]+pos_from[1]
        raise IndexError("Out of field")


class Moves_history():
    _moves = []
    _moved_pieces = []
    _captured_pieces = []
    _is_castling = []
    _castled_rook_fr_to = []

    def push(self, fr_piece, to_piece, fr, to, is_castling = False, rook_fr = None, rook_to = None):
        self._moves.append((fr, to))
        self._captured_pieces.append(deepcopy(to_piece))
        self._moved_pieces.append(deepcopy(fr_piece))
        self._is_castling.append(deepcopy(is_castling))
        self._castled_rook_fr_to.append([rook_fr, rook_to])

    def __getitem__(self, key):
        return {"from": self._moves[key][0],
                "to": self._moves[key][1],
                "piece": self._moved_pieces[key],
                "captured_piece": self._captured_pieces[key],
                "is_castling": self._is_castling[key],
                "castle_rook_from": self._castled_rook_fr_to[0],
                "castle_rook_to": self._castled_rook_fr_to[1]}

    def __setitem__(self, _slice_object, value):
        index = _slice_object.start
        key = _slice_object.stop

        if(key == "from"):
            self._moves[index][0] = value
        elif(key == "to"):
            self._moves[index][1] = value
        elif(key == "piece"):
            self._moved_pieces[index] = value
        elif(key == "captured_piece"):
            self._captured_pieces[index] = value
        elif(key == "is_castling"):
            self._is_castling[index] = value
        elif(key == "castle_rook_from"):
            self._castled_rook_fr_to[index][0] = value
        elif(key == "castle_rook_to"):
            self._castled_rook_fr_to[index][1] = value
        else:
            raise KeyError()
        

    def pop(self):
        fr_to = self._moves.pop()
        moved_piece = self._moved_pieces.pop()
        capt_piece = self._captured_pieces.pop()
        is_castling = self._is_castling.pop()
        castle_rook_fr_to = self._castled_rook_fr_to.pop()
        return (fr_to, moved_piece, capt_piece, is_castling, castle_rook_fr_to)

class ImpossibleMove(Exception):
    pass

class UndoMove(Exception):
    pass

class ExitGame(Exception):
    pass
