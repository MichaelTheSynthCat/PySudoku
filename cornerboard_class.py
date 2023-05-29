# Object representing a corner of a square
class Corner:
    def __init__(self, x, y, value='', symbol=None, size=1, color="black", idn=None):
        self.id = idn
        self.pos = [x, y]
        self.value = value
        self.symbol = symbol
        self.size = size
        self.color = color

    def info(self):
        output = "Corner {} at {}".format(self.id, self.pos)+" with value {}".format(str(self.value))
        return output

    def __str__(self):
        return str(self.value)

# Container for all corner-objects
# Upon initialization creates all corner-objects
class Cornerboard:
    def __init__(self, columns, rows, value='', symbol=None, size=1, color="black",):
        self.data = []
        self.dimensions = [columns, rows]
        for r in range(rows):
            self.data.append([])
            for c in range(columns):
                self.data[r].append(Corner(c, r, value=value, symbol=symbol, size=size, color=color, idn=c+r*columns))

    # debug info
    def makelog(self):
        for r in range(self.dimensions[1]):
            for c in range(self.dimensions[0]):
                print(self.data[r][c].info())