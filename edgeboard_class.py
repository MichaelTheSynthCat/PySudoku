# Object representing an edge of a square
class Edge:
    def __init__(self, x, y, orient, value='', color="black", idn=None):
        self.id = idn
        self.pos = [x, y]
        self.orient = orient
        self.value = value
        self.color = color

    def info(self):
        output = "Line {} at {} with {} orientation".format(self.id, self.pos, self.orient)+" with value {}".format(str(self.value))
        return output

    def __str__(self):
        return str(self.value)

# Container for all edge-objects
# Upon initialization creates all edge-objects
class Edgeboard:
    def __init__(self, columns, rows, orient, value=None, color="black"):
        self.data = []
        self.orient = orient
        self.dimensions = [columns, rows]
        for r in range(rows):
            self.data.append([])
            for c in range(columns):
                self.data[r].append(Edge(c, r, orient=orient, value='', color=color, idn=c+r*columns))

    # debug info
    def makelog(self):
        for r in range(self.dimensions[1]):
            for c in range(self.dimensions[0]):
                print(self.data[r][c].info())


