"""Adjacency checker for axis-aligned rectangles.

Detects if two rectangles are adjacent (share an edge/partial edge)
and classifies the adjacency subtype.

Examples:
[(0, 0, 3, 4), (3, 0, 6, 4)]    # proper
[(0, 0, 3, 6), (3, 1, 6, 5)]    # sub-line
[(0, 0, 3, 4), (3, 2, 6, 6)]    # partial
[(0, 0, 2, 2), (5, 0, 7, 2)]    # none

Math Concept:
    Find the touching vertical line x = a and then check the 1D overlap of y intervals
    Find the touching horizontal line y = b and then check the 1D overlap of x intervals
"""

from __future__ import annotations

from ..rectangle import Rectangle
from ..strategies import AdjacencyStrategy, AdjacencyType
from ..util import EPS


class AAAdjacency(AdjacencyStrategy):
    """Axis-aligned adjacency using side coordinate + interval overlap."""

    def check(self, a: Rectangle, b: Rectangle) -> AdjacencyType:
        """Determine adjacency by comparing side coordinates.

        For axis-aligned rectangles the corner layout is:
            p1 = bottom-left,  p2 = bottom-right,
            p3 = top-right,    p4 = top-left

        So the coordinate mapping is:
            x_min = p1.x,  x_max = p3.x
            y_min = p1.y,  y_max = p3.y

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            The most specific AdjacencyType found across all sides.
        """
        # Check vertical adjacency (left/right sides touching)
        # A's right side touches B's left side
        if abs(a.p3.x - b.p1.x) < EPS:
            result = self._classify_overlap(a.p1.y, a.p3.y, b.p1.y, b.p3.y)
            if result != AdjacencyType.NONE:
                return result

        # B's right side touches A's left side
        if abs(b.p3.x - a.p1.x) < EPS:
            result = self._classify_overlap(a.p1.y, a.p3.y, b.p1.y, b.p3.y)
            if result != AdjacencyType.NONE:
                return result

        # Check horizontal adjacency (top/bottom sides touching)
        # A's top side touches B's bottom side
        if abs(a.p3.y - b.p1.y) < EPS:
            result = self._classify_overlap(a.p1.x, a.p3.x, b.p1.x, b.p3.x)
            if result != AdjacencyType.NONE:
                return result

        # B's top side touches A's bottom side
        if abs(b.p3.y - a.p1.y) < EPS:
            result = self._classify_overlap(a.p1.x, a.p3.x, b.p1.x, b.p3.x)
            if result != AdjacencyType.NONE:
                return result

        return AdjacencyType.NONE

    @staticmethod
    def _classify_overlap(
        a_min: float, a_max: float, b_min: float, b_max: float
    ) -> AdjacencyType:
        """Classify the overlap of two 1D intervals on a shared axis.

        Args:
            a_min: Start of interval A.
            a_max: End of interval A.
            b_min: Start of interval B.
            b_max: End of interval B.

        Returns:
            PROPER if intervals are identical, SUB_LINE if one contains
            the other, PARTIAL if they partially overlap, NONE if no overlap.
        """
        overlap = max(0.0, min(a_max, b_max) - max(a_min, b_min))

        if overlap <= 0:
            return AdjacencyType.NONE

        # Proper: intervals are exactly the same
        if abs(a_min - b_min) < EPS and abs(a_max - b_max) < EPS:
            return AdjacencyType.PROPER

        # Sub-line: one interval fully contains the other
        if (a_min <= b_min + EPS and b_max <= a_max + EPS) or (
            b_min <= a_min + EPS and a_max <= b_max + EPS
        ):
            return AdjacencyType.SUB_LINE

        # Partial: intervals overlap but neither contains the other
        return AdjacencyType.PARTIAL
