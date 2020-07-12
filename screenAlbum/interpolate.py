import math
from typing import Any


class Interpolate:
    def __init__(self, start, stop, length, minimum, maximum):
        self.__start = start
        self.__stop = stop
        self.__length = length
        self.__minimum = minimum
        self.__maximum = maximum
        self.__before = None
        self.__before_distance = 1
        self.__after = None
        self.__after_distance = 1
        self.__mode = 'linear'

    def set_before(self, before):
        self.__before = before

    def set_before_distance(self, before_distance):
        self.__before_distance = before_distance

    def set_after(self, after):
        self.__after = after

    def set_after_distance(self, after_distance):
        self.__after_distance = after_distance

    def set_mode(self, mode):
        self.__mode = mode

    def interpolate_method(self):
        """Returns a list of a given length, of float values interpolated between two given values.
        Arguments:
            start: Starting Y value.
            stop: Ending Y value.
            length: Integer, the number of steps that will be interpolated.
            minimum: Lowest allowed Y value, any lower values will be clipped to this.
            maximum: Highest allowed Y value, any higher values will be clipped to this.
            before: Used in 'cubic' and 'catmull' modes, the Y value of the previous point before the start point.
                If set to None, it will be extrapolated linearly from the start and stop points.
            before_distance: Distance from the current points that the previous point is.
            after: Used in 'cubic' and 'catmull' modes, the Y value of the next point after the stop point.
                If set to None, it will be extrapolated linearly from the start and stop points.
            after_distance: Distance from the current points that the next point is.
            mode: String, the interpolation mode.  May be set to: 'linear', 'cosine', 'cubic', 'catmull'
        Returns: A list of float values.
        """

        minimum_distance = 40
        if self.length == 0:
            return []
        values = []
        y = self.start
        self.difference = self.stop - self.start
        self.step = self.difference / self.length
        if self.mode == 'cubic' or self.mode == 'catmull':
            if self.before is None:
                self.before = self.start - self.stop
                self.before_distance = self.length
            if self.after is None:
                self.after = self.stop + (self.stop - self.start)
                self.after_distance = self.length
            if self.after_distance < minimum_distance:
                after_distance = minimum_distance
            if self.before_distance < minimum_distance:
                self.before_distance = self.minimum_distance
            self.after_distance = self.after_distance / self.length
            self.before_distance = self.before_distance / self.length
            self.before = self.before / self.before_distance
            self.after = self.after / self.after_distance
        if self.mode == 'catmull':
            a = -0.5 * self.before + 1.5 * self.start - 1.5 * self.stop + 0.5 * self.after
            b = self.before - 2.5 * self.start + 2 * self.stop - 0.5 * self.after
            c = -0.5 * self.before + 0.5 * self.stop
            d = self.start
        elif self.mode == 'cubic':
            a = self.after - self.stop - self.before + self.start
            b = self.before - self.start - a
            c = self.stop - self.before
            d = self.start
        else:
            a = 1
            b = 1
            c = 1
            d = 1
        for x in range(self.length):
            values.append(y)
            if self.mode == 'cubic' or self.mode == 'catmull':
                mu = x / self.length
                muu = mu * mu
                y = (a * mu * muu) + (b * muu) + (c * mu) + d
            elif self.mode == 'cosine':
                mu = x / self.length
                muu = (1 - math.cos(mu * math.pi)) / 2
                y = self.start * (1 - muu) + (self.stop * muu)
            else:
                y = y + self.step
            if y > self.maximum:
                y = self.maximum
            if y < self.minimum:
                y = self.minimum
        return values
