# Object representing a square
class Square:

    def __init__(self, x, y, value='', symbol='None', color='black', background=None, idn=None):
        self.id = idn
        self.pos = [x, y]
        self.value = value
        self.symbol = symbol
        self.color = color
        self.background = background

    def move(self, x=None, y=None):
        if x is None:
            x = self.pos[0]
        if y is None:
            y = self.pos[1]
        self.pos = [x, y]

    def info(self):
        output = "Square {} at {}".format(self.id, self.pos)+" with value {}".format(str(self.value))
        return output

    def __str__(self):
        return str(self.value)

# Container for all squares
# Upon initialization creates all squares
class SquareBoard:
    def __init__(self, columns, rows, value='', symbol='None', color='#ffffff', background='#ffffff'):
        self.data = []
        self.dimensions = [columns, rows]
        for r in range(rows):
            self.data.append([])
            for c in range(columns):
                self.data[r].append(Square(c, r, value=value, symbol=symbol, color=color, background=background, idn=c+r*columns))

    def makelog(self):
        for r in range(self.dimensions[1]):
            for c in range(self.dimensions[0]):
                print(self.data[r][c].info())

    def printchart(self):
        for r in range(self.dimensions[1]):
            for c in range(self.dimensions[0]):
                print(self.data[r][c], end=" ")
            print()

