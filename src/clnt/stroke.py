"""
Ronny Getz
Stroke: list of points, times, pen color/size; hit-test and serialization.
"""
from PyQt6 import QtGui
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QColor

from style import (
    LINE_POINT_END,
    LINE_POINT_START,
    POINT_BEFORE,
    SAME_POINT,
    SECOND_POINT,
    SQUARE_ROOT,
    SQUARED,
)


class Stroke(object):
    """Single stroke: points, timestamps, pen color/size, id; contains_point and __dict__."""

    def __init__(self, points, times, pen_color, pen_size, id):
        """Build stroke from points (QPoint or (x,y)), times, pen, id; selected=False."""
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
        self.id = int(id)

    def contains_point(self, pt, tolerance):
        """Return True if pt is within tolerance of any segment of the stroke."""
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
        """Return dict with points, times, pen_color (hex), pen_size, id for serialization."""
        points_l = []
        for p in self.points:
            points_l.append((p.x(), p.y()))
        stroke_dict = {
            "points": points_l,
            "times": self.times,
            "pen_color": self.pen_color.name(QColor.NameFormat.HexArgb),
            "pen_size": self.pen_size,
            "id": self.id
        }
        return stroke_dict
