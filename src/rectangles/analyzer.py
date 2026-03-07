"""Facade that auto-selects analysis strategies based on rectangle type."""

from __future__ import annotations

from .axis_aligned import AAAdjacency, AAContainment, AAIntersection
from .general import GeneralAdjacency, GeneralContainment, GeneralIntersection
from .rectangle import Point, Rectangle
from .strategies import (
    AdjacencyStrategy,
    AdjacencyType,
    ContainmentStrategy,
    IntersectionStrategy,
    StrategyType,
)


class RectangleAnalyzer:
    """Analyze the relationship between two rectangles.

    Automatically selects axis-aligned or general strategies based on
    the ``is_axis_aligned`` flag of the input rectangles, unless a
    specific ``strategy`` is provided.

    Args:
        a: First rectangle.
        b: Second rectangle.
        strategy: Which strategy family to use (default: AUTO).
    """

    def __init__(
        self,
        a: Rectangle,
        b: Rectangle,
        *,
        strategy: StrategyType = StrategyType.AUTO,
    ) -> None:
        """Initialize the analyzer with two rectangles.

        Args:
            a: First rectangle.
            b: Second rectangle.
            strategy: Override strategy selection.
        """
        self.a = a
        self.b = b

        (
            self._intersection,
            self._containment,
            self._adjacency,
        ) = _make_strategies(strategy, a, b)

    def intersection(self) -> list[Point]:
        """Return sorted intersection points between the two rectangles."""
        return self._intersection.find_points(self.a, self.b)

    def containment(self) -> str:
        """Return a containment descriptor string."""
        return self._containment.check(self.a, self.b)

    def adjacency(self) -> AdjacencyType:
        """Return the adjacency classification."""
        return self._adjacency.check(self.a, self.b)


def _make_strategies(
    strategy: StrategyType,
    a: Rectangle,
    b: Rectangle,
) -> tuple[IntersectionStrategy, ContainmentStrategy, AdjacencyStrategy]:
    """Instantiate the concrete strategy triple.

    Args:
        strategy: Which family to use.
        a: First rectangle (used for AUTO detection).
        b: Second rectangle (used for AUTO detection).

    Returns:
        A tuple of (intersection, containment, adjacency) strategies.
    """
    use_aa = strategy == StrategyType.AXIS_ALIGNED or (
        strategy == StrategyType.AUTO and a.is_axis_aligned and b.is_axis_aligned
    )
    if use_aa:
        return AAIntersection(), AAContainment(), AAAdjacency()
    return GeneralIntersection(), GeneralContainment(), GeneralAdjacency()
