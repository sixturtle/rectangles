"""Containment analysis for axis-aligned rectangles.

Determines whether one rectangle is wholly contained within another.

Examples:
[(0, 0, 10, 10), (2, 2, 5, 5)]    # A contains B
[(2, 2, 5, 5), (0, 0, 10, 10)]    # B contains A
[(0, 0, 10, 10), (0, 0, 10, 10)]  # Overlap: A contains B and B contains A
[(0, 0, 5, 5), (3, 3, 8, 8)]      # No containment

Math Concept:
    Check if the inner rectangle's x-interval is contained within the outer
    rectangle's x-interval and the inner rectangle's y-interval is contained
    within the outer rectangle's y-interval.
"""

from __future__ import annotations

from ..rectangle import Rectangle
from ..strategies import ContainmentStrategy


class AAContainment(ContainmentStrategy):
    """Axis-aligned containment using interval comparison."""

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
        """Check whether *inner* is wholly contained within *outer*.

        Args:
            outer: The potentially enclosing rectangle.
            inner: The potentially enclosed rectangle.

        Returns:
            True if *inner* is fully inside *outer*.
        """
        return (
            outer.p1.x <= inner.p1.x
            and inner.p3.x <= outer.p3.x
            and outer.p1.y <= inner.p1.y
            and inner.p3.y <= outer.p3.y
        )
