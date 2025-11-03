"""
Ronny Getz
stroke
"""

from style import *


class Stroke(object):
    def __init__(self, points, times, pen_color, pen_size):
        """constructor"""
        self.points = points
        self.times = times
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.selected = False

    def contains_point(self, pt, tolerance):
        """check if the distance from the point to the stroke
         is less than the tolerance"""
        for i in range(SECOND_POINT, len(self.points)):
            p1, p2 = self.points[i-POINT_BEFORE], self.points[i]
            if self.point_line_distance(pt, p1, p2) <= tolerance:
                return True
        return False

    @staticmethod
    def point_line_distance(p, a, b):
        """Return the minimum distance from point p to line segment ab"""
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        px, py = p.x(), p.y()
        dx, dy = bx - ax, by - ay
        if dx == dy == SAME_POINT:
            return ((px - ax)**SQUARED + (py - ay)**SQUARED) ** SQUARE_ROOT
        t = max(LINE_POINT_START,
                min(LINE_POINT_END,
                    ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
        closest_x = ax + t*dx
        closest_y = ay + t*dy
        return (((px - closest_x)**SQUARED + (py - closest_y)**SQUARED) **
                SQUARE_ROOT)
