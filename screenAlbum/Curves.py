from operator import itemgetter

from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line
from kivy.properties import ListProperty, BooleanProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout

#from generalcommands import interpolate

from kivy.lang.builder import Builder

from screenAlbum.interpolate import Interpolate

Builder.load_string("""
<Curves>:
""")


class Curves(FloatLayout):
    """Widget for viewing and generating color curves information."""

    points = ListProperty()  #List of curves points
    current_point = ListProperty()  #
    moving = BooleanProperty(False)  #
    touch_range = NumericProperty(0.1)  #
    scroll_timeout = NumericProperty()  #
    curve = ListProperty()  #
    resolution = 256  #Horizontal resolution of the curve
    bytes = 256  #Vertical resolution of the curve

    def __init__(self, **kwargs):
        super(Curves, self).__init__(**kwargs)
        self.bind(pos=self.refresh, size=self.refresh)
        self.points = [[0, 0], [1, 1]]

    def on_size(self, *_):
        self.refresh()

    def reset(self):
        """Clears the canvas and sets up the default curve."""

        self.points = [[0, 0], [1, 1]]
        self.refresh()

    def refresh(self, *_):
        """Sorts and redraws points on the canvas."""

        if len(self.points) < 2:
            self.reset()
        self.points = sorted(self.points, key=itemgetter(0))
        self.points[0][0] = 0
        self.points[-1][0] = 1

        canvas = self.canvas
        canvas.clear()
        canvas.before.add(Color(0, 0, 0))
        canvas.before.add(Rectangle(size=self.size, pos=self.pos))
        self.generate_curve()
        self.draw_line(canvas)

        for point in self.points:
            self.draw_point(canvas, point)

        if self.parent:
            if self.parent.parent:
                if self.parent.parent.parent:
                    image = self.parent.parent.parent.owner.viewer.edit_image
                    if self.points == [[0, 0], [1, 1]]:
                        image.curve = []
                    else:
                        image.curve = self.curve

    def relative_to_local(self, point):
        """Convert relative coordinates (0-1) into window coordinates.
        Argument:
            point: List, [x, y] coordinates.
        Returns: List, [x, y] coordinates.
        """

        x = point[0]*self.width + self.pos[0]
        y = point[1]*self.height + self.pos[1]
        return [x, y]

    def local_to_relative(self, point):
        """Convert window coordinates into relative coordinates (0-1).
        Argument:
            point: List, [x, y] coordinates.
        Returns: List, [x, y] coordinates.
        """

        x = (point[0] - self.pos[0])/self.width
        y = (point[1] - self.pos[1])/self.height
        return [x, y]

    def draw_line(self, canvas):
        """Draws the canvas display line from the current curves data.
        Argument:
            canvas: A Kivy canvas object
        """

        canvas.add(Color(1, 1, 1))
        step = self.width/self.resolution
        x = 0
        points = []
        vscale = self.height/(self.bytes-1)
        for point in self.curve:
            points.append(x + self.pos[0])
            points.append((point*vscale) + self.pos[1])
            x = x+step
        canvas.add(Line(points=points))

    def draw_point(self, canvas, point):
        """Draws a curve edit point graphic on the canvas.
        Arguments:
            canvas: A Kivy canvas object
            point: List containing relative coordinates of the point, x, y
        """

        size = 20
        real_point = self.relative_to_local(point)
        app = App.get_running_app()
        if point == self.current_point:
            color = app.theme.selected
        else:
            color = (1, 1, 1, 1)
        source = 'data/curve_point.png'
        canvas.add(Color(rgba=color))
        canvas.add(Rectangle(source=source, pos=(real_point[0]-(size/2), real_point[1]-(size/2)), size=(size, size)))

    def add_point(self, point):
        """Adds a new point to the curve and regenerates and redraws the curve.
        Argument:
            point: List containing relative coordinates of the point, x, y
        """

        x = point[0]
        y = point[1]

        #dont allow illegal values for x or y
        if x > 1 or y > 1 or x < 0 or y < 0:
            return

        #dont allow point on an x position that already exists
        for point in self.points:
            if point[0] == x:
                return
        self.points.append([x, y])
        self.current_point = [x, y]
        self.refresh()

    def remove_point(self):
        """Removes the last moved point and regenerates and redraws the curve."""

        if self.current_point:
            for index, point in enumerate(self.points):
                if point[0] == self.current_point[0] and point[1] == self.current_point[1]:
                    self.points.pop(index)
        self.refresh()

    def generate_curve(self):
        """Regenerates the curve data based on self.points."""

        app = App.get_running_app()
        self.curve = []
        resolution = self.resolution - 1
        total_bytes = self.bytes - 1
        interpolation = app.interpolation

        x = 0
        index = 0
        previous_point = False
        start_point = self.points[index]

        while x < resolution:
            if index < (len(self.points)-2):
                next_point = self.points[index+2]
            else:
                next_point = False
            stop_point = self.points[index+1]
            stop_x = int(stop_point[0]*resolution)
            distance = stop_x - x
            start_y = start_point[1] * total_bytes
            stop_y = stop_point[1] * total_bytes
            if previous_point != False:
                previous_y = previous_point[1] * total_bytes
                previous_distance = (start_point[0] - previous_point[0]) * total_bytes
            else:
                previous_y = None
                previous_distance = distance
            if next_point != False:
                next_y = next_point[1] * total_bytes
                next_distance = (next_point[0] - stop_point[0]) * total_bytes
            else:
                next_distance = distance
                next_y = None
            interpolate = Interpolate(start_y, stop_y, distance, 0, total_bytes)
            if interpolation == 'Catmull-Rom':
                interpolate.set_before(previous_y)
                interpolate.set_before_distance(previous_distance)
                interpolate.set_after(next_y)
                interpolate.set_after_distance(next_distance)
                interpolate.set_mode('catmull')
                ys = interpolate.interpolate_method()
                #ys = interpolate(start_y, stop_y, distance, 0, total_bytes, before=previous_y, before_distance=previous_distance, after=next_y, after_distance=next_distance, mode='catmull')
            elif interpolation == 'Cubic':
                interpolate.set_before(previous_y)
                interpolate.set_before_distance(previous_distance)
                interpolate.set_after(next_y)
                interpolate.set_after_distance(next_distance)
                interpolate.set_mode('Cubic')
                ys = interpolate.interpolate_method()
                #ys = interpolate(start_y, stop_y, distance, 0, total_bytes, before=previous_y, before_distance=previous_distance, after=next_y, after_distance=next_distance, mode='cubic')
            elif interpolation == 'Cosine':
                interpolate.set_mode('cosine')
                ys = interpolate.interpolate_method()
                #ys = interpolate(start_y, stop_y, distance, 0, total_bytes, mode='cosine')
            else:
                ys = interpolate.interpolate_method()
                #ys = interpolate(start_y, stop_y, distance, 0, total_bytes)
            self.curve = self.curve + ys
            x = stop_x
            index = index + 1
            previous_point = start_point
            start_point = stop_point
        self.curve.append(self.points[-1][1] * total_bytes)

    def near_x(self, first, second):
        """Check if two points on the x axis are near each other using self.touch_range.
        Arguments:
            first: First point
            second: Second point
        Returns: True or False
        """

        aspect = self.width/self.height
        touch_range = self.touch_range / aspect

        if abs(second-first) <= touch_range:
            return True
        else:
            return False

    def near_y(self, first, second):
        """Check if two points on the y axis are near each other using self.touch_range.
        Arguments:
            first: First point
            second: Second point
        Returns: True or False
        """

        touch_range = self.touch_range

        if abs(second-first) <= touch_range:
            return True
        else:
            return False

    def on_touch_down(self, touch):
        """Intercept touches and begin moving points.
        Will also modify scrolling in the parent scroller widget to improve usability.
        """

        edit_scroller = self.parent.parent.parent.owner.ids['editScroller']
        self.scroll_timeout = edit_scroller.scroll_timeout  #cache old scroll timeout

        #Handle touch
        if self.collide_point(*touch.pos):
            edit_scroller.scroll_timeout = 0  #Temporarily modify scrolling in parent widget
            self.moving = True
            point = self.local_to_relative(touch.pos)
            for existing in self.points:
                if self.near_x(point[0], existing[0]) and self.near_y(point[1], existing[1]):
                    #touch is over an existing point, select it so it can start to move
                    self.current_point = existing
                    self.refresh()
                    return

            self.add_point(point)
            return True

    def on_touch_move(self, touch):
        """Intercept touch move events and move point if one is active."""

        if self.collide_point(*touch.pos):
            new_point = self.local_to_relative(touch.pos)
            if self.moving:
                #We were already moving a point
                for index, point in enumerate(self.points):
                    if point[0] == self.current_point[0]:
                        too_close = False
                        for other_point in self.points:
                            if other_point != point:
                                if self.near_x(other_point[0], new_point[0]) and self.near_y(other_point[1], new_point[1]):
                                    too_close = True
                        if point[0] == 0:
                            new_point[0] = 0
                        elif new_point[0] <= 0:
                            too_close = True
                        if point[0] == 1:
                            new_point[0] = 1
                        elif new_point[0] >= 1:
                            too_close = True

                        if not too_close:
                            self.points[index] = new_point
                            self.current_point = new_point
                        self.refresh()
                        break
            return True

    def on_touch_up(self, touch):
        """Touch is released, turn off move mode regardless of if touch is over widget or not."""

        edit_scroller = self.parent.parent.parent.owner.ids['editScroller']
        edit_scroller.scroll_timeout = self.scroll_timeout  #Reset parent scroller object to normal operation
        self.moving = False
        if self.collide_point(*touch.pos):
            return True