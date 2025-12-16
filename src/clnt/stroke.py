"""
Ronny Getz
stroke
"""

from style import *
from PyQt6 import QtGui
from PyQt6.QtCore import QPoint


class Stroke(object):
    def __init__(self, points, times, pen_color, pen_size, id):
        """constructor"""
        if any(isinstance(point, QPoint) for point in points):
            self.points = points
        else:
            new_points = []
            for p in points:
                new_points.append(QPoint(*p))
            self.points = new_points
        self.times = times
        if isinstance(pen_color, QtGui.QColor):
            self.pen_color = pen_color
        else:
            self.pen_color = QtGui.QColor(pen_color)
        self.pen_size = pen_size
        self.selected = False
        self.id = id

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

    def __dict__(self):
        """convert stroke to dictionary"""
        points_l = []
        for p in self.points:
            points_l.append((p.x(), p.y()))
        stroke_dict = {
            "points": points_l,
            "times": self.times,
            "pen_color": self.pen_color.name(),
            "pen_size": self.pen_size,
            "id": self.id
        }
        return stroke_dict
