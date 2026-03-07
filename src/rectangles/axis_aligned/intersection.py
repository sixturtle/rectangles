"""Optimized intersection for axis-aligned rectangles.

Examples:
    [(0, 0, 10, 10), (2, 2, 5, 5)]    # Containment: A contains B
    [(0, 0, 10, 10), (0, 0, 10, 10)]  # Overlap: A contains B and B contains A
    [(0, 0, 5, 5), (3, 3, 8, 8)]      # Intersection: A and B intersect
    [(0, 0, 5, 5), (5, 0, 8, 8)]      # Adjacency: A and B touch at the boundary
    [(0, 0, 5, 5), (6, 0, 8, 8)]      # Disjoint: A and B do not intersect

Math Concept:
    Computes the overlap rectangle via coordinate clamping:
        x_overlap = [max(x1_a, x1_b), min(x2_a, x2_b)]
        y_overlap = [max(y1_a, y1_b), min(y2_a, y2_b)]

    If this produces a valid (non-degenerate) rectangle, its four
    corners are the intersection points.  Runs in O(1).
"""

from ..rectangle import Point, Rectangle
from ..strategies import IntersectionStrategy
from ..util import EPS


class AAIntersection(IntersectionStrategy):
    """Axis-aligned intersection using coordinate-overlap clamping."""

    def find_points(self, a: Rectangle, b: Rectangle) -> list[Point]:
        """Find intersection points using coordinate overlap.

        Computes the overlapping x- and y-intervals of two axis-aligned
        rectangles.  If a valid overlap rectangle exists, returns its
        four distinct corners (deduplicated within floating-point
        tolerance).

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            Sorted list of intersection points, empty if no overlap.
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
        """Append *pt* if not already in the list (within tolerance)."""
        for p in points:
            if abs(pt.x - p.x) < EPS and abs(pt.y - p.y) < EPS:
                return
        points.append(pt)
