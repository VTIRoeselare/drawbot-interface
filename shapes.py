# The arduino accepts commands in 1/10 millimeters
UNIT = 10

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and (self.x1 == other.x1) \
            and (self.y1 == other.y1) \
            and (self.x2 == other.x2) \
            and (self.y2 == other.y2)

    def __ne__(self, other):
        return not self.__eq__(other)

    def instruction(self):
        return [
            'M {0} {1}'.format(self.x1 * UNIT, self.y1 * UNIT),
            'L {0} {1}'.format(self.x2 * UNIT, self.y2 * UNIT)
        ]


class Rect:
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    # Translate a rectangle to 4 lines
    def instruction(self):
       instructions = []
       instructions.append('M ' + str(float(self.x) * UNIT) + ' ' + str(float(self.y) * UNIT))
       instructions.append('L ' + str(float(self.x + self.width) * UNIT) + ' ' + str(float(self.y) * UNIT)) 
       instructions.append('L ' + str(float(self.x + self.width) * UNIT) + ' ' + str(float(self.y + self.height) * UNIT))
       instructions.append('L ' + str(float(self.x) * UNIT) + ' ' + str(float(self.y + self.height) * UNIT))  
       instructions.append('L ' + str(float(self.x) * UNIT) + ' ' + str(float(self.y) * UNIT))
       return instructions

class Polygon:
    # Example value: points="750,600 629.7,659.4 600,792.9 683.2,900 816.8,900 900,792.9 870.3,659.4        "
    def __init__(self, points):
        self.points = points.strip().split()

        # Add starting point to the back to get the last line
        self.points.append(self.points[0])
        self.points = list(map(lambda x: x.split(','), self.points))

    def instruction(self):
        instructions = []
        instructions.append('M ' + str(float(self.points[0][0]) * UNIT) + ' ' + str(float(self.points[0][1]) * UNIT))
        for i, point in enumerate(self.points[1:]):
            instructions.append('L ' + str(float(self.points[i][0]) * UNIT) + ' ' + str(float(self.points[i][1]) * UNIT))
        instructions.append('L ' + str(float(self.points[0][0]) * UNIT) + ' ' + str(float(self.points[0][1]) * UNIT))

        return instructions
