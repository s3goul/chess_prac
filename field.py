import string
import figure as figs
import os

DEBUG = True
 
class field():
    """ Chess field class """
    
    _black_bg = "\u001b[40m\u001b[37m"
    _white_bg = "\u001b[47m\u001b[30m"
    _col_names = 'abcdefgh'
    _row_names = '87654321'
    _possible_moves = []

    def __init__(self):
        self._create_field()

    def _create_field(self):
        field = {row: {i: None for i in string.digits[1:9]}
                 for row in string.ascii_lowercase[:8]}

        for row, color in (('7', "black"), ("2", "white")):
            for i in string.ascii_lowercase[:8]:
                field[i][row] = figs.Pawn(color, i+row, "p")

        for row, color in (('8', "black"), ("1", "white")):
            field['a'][row] = figs.Rook(color, 'a'+row, 'R')
            field['h'][row] = figs.Rook(color, 'h'+row, 'R')

            field['b'][row] = figs.Knight(color, 'b'+row, 'N')
            field['g'][row] = figs.Knight(color, 'g'+row, 'N')

            field['c'][row] = figs.Bishop(color, 'c'+row, 'B')
            field['f'][row] = figs.Bishop(color, 'f'+row, 'B')

            field['d'][row] = figs.Queen(color, 'd'+row, 'Q')
            field['e'][row] = figs.King(color, 'e'+row, 'K')

        self._field = field

    def _render_board(self, show_possible=0):
        #os.system("clear")
        possible_move_bg = "\u001b[43m"

        print(self._black_bg)

        print("  ", end="")
        for col in self._col_names.upper():
            print(f" {col} ", end="")
        print()
        i = 0
        color = (self._white_bg, self._black_bg)
        empty_square = "   "
        for row in self._row_names:
            print(row, end=" ")
            for col in self._col_names:
                if(show_possible and col+row in self._possible_moves):
                    print(possible_move_bg, end="")
                else:
                    print(color[i], end="")

                if(self._field[col][row]):
                    print(self._field[col][row].prefix, end="")
                else:
                    print(empty_square, end="")
                i = (i+1) % 2
            print(self._black_bg, row)
            i = (i+1) % 2
        print("  ", end="")
        for col in self._col_names.upper():
            print(f" {col} ", end="")
        print()

    def __getitem__(self, value):
        """ Get field piece using 2 letter string e.g. e4 """
        try:
            return self._field[value[0]][value[1]]
        except IndexError as IE:
            raise ValueError("Impossible move") 

    def __setitem__(self, ind, value):
        self._field[ind[0]][ind[1]] = value


if __name__ == "__main__":
    f = field()
