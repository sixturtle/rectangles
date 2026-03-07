"""Intersection analysis for general (possibly rotated) rectangles.

Finds the vertices of the intersection polygon by combining:
    1. Corners of A inside B
    2. Corners of B inside A
    3. Edge-edge crossing points

See math_concepts.md § 2 (cross product) and § 4 (Cramer's Rule).
"""

from __future__ import annotations

from ..rectangle import Point, Rectangle
from ..strategies import IntersectionStrategy
from ..util import Util


class GeneralIntersection(IntersectionStrategy):
    """General intersection via point-in-polygon + edge crossing."""

    def find_points(self, a: Rectangle, b: Rectangle) -> list[Point]:
        """Return the vertices of the intersection region between two rectangles.

        Combines three sources of vertices:
            1. Corners of *a* that lie inside *b*.
            2. Corners of *b* that lie inside *a*.
            3. Points where an edge of *a* crosses an edge of *b*.

        The result is sorted lexicographically by (x, y) and
        deduplicated via ``set``.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            Sorted list of distinct intersection polygon vertices.
            Empty if the rectangles do not overlap.
        """
        points: set[Point] = set()

        corners_a = [a.p1, a.p2, a.p3, a.p4]
        corners_b = [b.p1, b.p2, b.p3, b.p4]

        # 1. Corners of A inside B
        for p in corners_a:
            if Util.point_in_polygon(p, corners_b):
                points.add(p)

        # 2. Corners of B inside A
        for p in corners_b:
            if Util.point_in_polygon(p, corners_a):
                points.add(p)

        # 3. Edge-edge intersections
        for seg_a in a.segments:
            for seg_b in b.segments:
                cross = Util.segments_intersect(seg_a, seg_b)
                if cross is not None:
                    points.add(cross)

        return sorted(points)
