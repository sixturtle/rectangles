"""Containment analysis for general (possibly rotated) rectangles.

Determines whether one rectangle is wholly contained within another
using the point-in-polygon test (cross-product same-side method).

Math Concept:
    A rectangle B is inside rectangle A if and only if all four corners
    of B pass the point-in-polygon test against A's boundary.
    See math_concepts.md § 2 (2D Cross Product) for details.
"""

from __future__ import annotations

from ..rectangle import Rectangle
from ..strategies import ContainmentStrategy
from ..util import Util


class GeneralContainment(ContainmentStrategy):
    """General containment via point-in-polygon for rotated rects."""

    def check(self, a: Rectangle, b: Rectangle) -> str:
        """Describe the containment relationship between two rectangles.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            One of "A contains B", "B contains A", or "No containment".
        """
        if self._contains(a, b):
            return "A contains B"
        if self._contains(b, a):
            return "B contains A"

        return "No containment"

    @staticmethod
    def _contains(outer: Rectangle, inner: Rectangle) -> bool:
        """Check whether all corners of *inner* lie inside *outer*.

        Args:
            outer: The potentially enclosing rectangle.
            inner: The potentially enclosed rectangle.

        Returns:
            True if every corner of *inner* is inside or on the
            boundary of *outer*.
        """
        outer_vertices = [outer.p1, outer.p2, outer.p3, outer.p4]
        return all(
            Util.point_in_polygon(corner, outer_vertices)
            for corner in [inner.p1, inner.p2, inner.p3, inner.p4]
        )
