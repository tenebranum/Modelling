class Block(object):
    def __init__(self, **kwargs):
        self.y = kwargs.get('y', 0)
        self.step = kwargs.get('step', 1)

    def calculate_y(self):
        return self.y

    def __add__(self, other):
        result = self.calculate_y() + other.calculate_y()
        block = Block(y=result, step=self.step)
        return block

    def __mul__(self, other):
        if type(other) is DelayBlock:
            other.append(self.calculate_y())
            result = other.calculate_y()
            block = Block(y=result, step=self.step)
        else:
            other.step = self.calculate_y()
            result = other.calculate_y()
            block = Block(y=result, step=self.step)
        return block


class APBlock(Block):
    def __init__(self, **kwargs):
        super(APBlock, self).__init__(**kwargs)
        self.y_values = [0,]
        self.delta = kwargs.get('delta', 1)
        self.k = kwargs.get('k', 1)
        self.T = kwargs.get('T', 1)

    def calculate_y(self):
        value = float(self.k * self.delta * self.step + self.T * self.y_values[-1])/(self.T + self.delta)
        self.y = value
        self.insert_y(-1, value)
        return value

    def insert_y(self, position, y):
        if int(position) == -1:
            self.y_values.append(y)
        else:
            self.y_values.insert(int(position), y)
        if len(self.y_values) > 2:
            self.y_values.pop(0)


class DelayBlock(Block):
    def __init__(self, **kwargs):
        super(DelayBlock, self).__init__(**kwargs)
        self.delta = kwargs.get('delta', 1)
        self.delay = kwargs.get('delay', 0)
        self.y_values = [0,]

    def append(self, y):
        self.y_values.append(y)
        if len(self.y_values) - 1 > int(self.delay / self.delta):
            self.y_values.pop(0)

    def calculate_y(self):
        try:
            position = int(self.delay / self.delta)
            position = -1 if position == 0 else position + 1
            return self.y_values[-position]
        except:
            return self.y_values[0]


class PBlock(Block):
    def __init__(self, **kwargs):
        super(PBlock, self).__init__(**kwargs)
        self.y = 0
        self.k = kwargs.get('k', 0)
        self.y_values = [0,]

    def calculate_y(self):
        result = self.step * self.k
        self.y = result
        return result


class IBlock(Block):
    def __init__(self, **kwargs):
        super(IBlock, self).__init__(**kwargs)
        self.y = 0
        self.k = kwargs.get('k', 0)
        self.Ti = kwargs.get('Ti', 1)
        self.y_values = [0,]

    def append(self, y):
        self.y_values.append(y)
        if len(self.y_values) > 2:
            self.y_values.pop(0)

    def calculate_y(self):
        y = (self.k * self.step  + self.y_values[-1]) / self.Ti
        self.y = y
        self.append(y)
        return y

