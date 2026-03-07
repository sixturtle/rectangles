"""Optimized intersection for axis-aligned rectangles.

Examples:
[(0, 0, 10, 10), (2, 2, 5, 5)]    # Containment: A contains B
[(0, 0, 10, 10), (0, 0, 10, 10)]  # Overlap: A contains B and B contains A
[(0, 0, 5, 5), (3, 3, 8, 8)]      # Intersection: A and B intersect at (3, 5) and (5, 3)
[(0, 0, 5, 5), (3, 3, 8, 4)]      # Intersection: A and B intersect at (5, 3) and (5, 4)
[(0, 0, 5, 5), (5, 0, 8, 8)]      # Adjacency: A and B touch at the boundary
[(0, 0, 5, 5), (6, 0, 8, 8)]      # Disjoint: A and B do not intersect

Math Concept:
    Exploits the fact that all edges are horizontal or vertical,
    so only perpendicular (H ⟂ V) pairs can produce point
    intersections. Runs in O(1) — 16 constant comparisons.
"""

from enum import Enum

from ..rectangle import Point, Rectangle, Segment
from ..strategies import IntersectionStrategy
from ..util import EPS


class _Orientation(Enum):
    """Orientation of a line segment."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class AAIntersection(IntersectionStrategy):
    """Axis-aligned intersection using H-V segment crossing."""

    def find_points(self, a: Rectangle, b: Rectangle) -> list[Point]:
        """Find intersection points using simple coordinate overlap.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            Sorted list of intersection points.
        """
        x1 = max(a.p1.x, b.p1.x)
        y1 = max(a.p1.y, b.p1.y)

        x2 = min(a.p3.x, b.p3.x)
        y2 = min(a.p3.y, b.p3.y)

        # No overlap (or degenerate line/point contact)
        if x1 >= x2 - EPS or y1 >= y2 - EPS:
            return []

        # Overlap
        candidates = [
            Point(x=x1, y=y1),
            Point(x=x1, y=y2),
            Point(x=x2, y=y1),
            Point(x=x2, y=y2),
        ]
        # Remove shared corners
        points: list[Point] = []
        for pt in candidates:
            self._add_unique(points, pt)

        return sorted(points)

    def _add_unique(self, points: list[Point], pt: Point) -> None:
        """Append p if not already in the list (within tolerance)."""
        for p in points:
            if abs(pt.x - p.x) < EPS and abs(pt.y - p.y) < EPS:
                return
        points.append(pt)

    def _find_points(self, a: Rectangle, b: Rectangle) -> list[Point]:
        """Find intersection points using H-V crossing.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            Sorted list of intersection points.
        """
        segments_a = a.segments
        segments_b = b.segments
        points: set[Point] = set()

        for seg_a in segments_a:
            for seg_b in segments_b:
                ori_a = self._classify(seg_a)
                ori_b = self._classify(seg_b)
                if ori_a == _Orientation.HORIZONTAL and ori_b == _Orientation.VERTICAL:
                    p = self._intersect_h_v(seg_a, seg_b)
                    if p is not None:
                        points.add(p)
                elif (
                    ori_a == _Orientation.VERTICAL and ori_b == _Orientation.HORIZONTAL
                ):
                    p = self._intersect_h_v(seg_b, seg_a)
                    if p is not None:
                        points.add(p)

        return sorted(points)

    @staticmethod
    def _classify(seg: Segment) -> _Orientation:
        """Classify a segment as horizontal or vertical.

        Args:
            seg: The segment to classify.

        Returns:
            HORIZONTAL if y-coordinates are equal, else VERTICAL.
        """
        if seg.p1.y == seg.p2.y:
            return _Orientation.HORIZONTAL
        return _Orientation.VERTICAL

    @staticmethod
    def _intersect_h_v(h: Segment, v: Segment) -> Point | None:
        """Find intersection point of a horizontal and vertical segment.

        A horizontal segment at y=h.p1.y spanning [h.p1.x, h.p2.x] intersects
        a vertical segment at x=v.p1.x spanning [v.p1.y, v.p2.y] if:
          - v.p1.x is strictly within (h.p1.x, h.p2.x)
          - h.p1.y is strictly within (v.p1.y, v.p2.y)

        Strict inequalities avoid counting shared corners/edges as
        intersection points — those are adjacency, not intersection.

        Args:
            h: A horizontal segment.
            v: A vertical segment.

        Returns:
            The intersection point or None if they don't cross.
        """
        x = v.p1.x  # vertical segment's x-coordinate
        y = h.p1.y  # horizontal segment's y-coordinate

        h_min_x = min(h.p1.x, h.p2.x)
        h_max_x = max(h.p1.x, h.p2.x)
        v_min_y = min(v.p1.y, v.p2.y)
        v_max_y = max(v.p1.y, v.p2.y)

        if h_min_x < x < h_max_x and v_min_y < y < v_max_y:
            return Point(x=x, y=y)
        return None
