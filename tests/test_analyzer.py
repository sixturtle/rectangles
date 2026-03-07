"""Tests for the RectangleAnalyzer facade."""

from __future__ import annotations

from rectangles.analyzer import RectangleAnalyzer
from rectangles.rectangle import Point, Rectangle
from rectangles.strategies import AdjacencyType, StrategyType


def _r(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


def _p(x: float, y: float) -> Point:
    """Shortcut to create a point."""
    return Point(x=x, y=y)


# ── Axis-aligned auto-selection ──────────────────────────────────────


class TestAnalyzerAxisAligned:
    """Verify the analyzer delegates to axis-aligned strategies."""

    def test_intersection(self) -> None:
        """Overlapping rectangles produce intersection polygon vertices."""
        analyzer = RectangleAnalyzer(_r(0, 0, 5, 5), _r(3, 3, 8, 8))
        assert analyzer.intersection() == [
            _p(3, 3),
            _p(3, 5),
            _p(5, 3),
            _p(5, 5),
        ]

    def test_containment(self) -> None:
        """A contains B."""
        analyzer = RectangleAnalyzer(_r(0, 0, 10, 10), _r(2, 2, 5, 5))
        assert analyzer.containment() == "A contains B"

    def test_adjacency_proper(self) -> None:
        """Adjacent rectangles classified as proper."""
        analyzer = RectangleAnalyzer(_r(0, 0, 3, 4), _r(3, 0, 6, 4))
        assert analyzer.adjacency() == AdjacencyType.PROPER

    def test_intersection_when_contained(self) -> None:
        """B contained in A — returns B's corners as intersection polygon."""
        analyzer = RectangleAnalyzer(_r(0, 0, 10, 10), _r(2, 2, 5, 5))
        assert analyzer.intersection() == [
            _p(2, 2),
            _p(2, 5),
            _p(5, 2),
            _p(5, 5),
        ]

    def test_no_containment_when_disjoint(self) -> None:
        """No containment for separated rectangles."""
        analyzer = RectangleAnalyzer(_r(0, 0, 2, 2), _r(5, 5, 8, 8))
        assert analyzer.containment() == "No containment"

    def test_no_adjacency_when_disjoint(self) -> None:
        """No adjacency for separated rectangles."""
        analyzer = RectangleAnalyzer(_r(0, 0, 2, 2), _r(5, 5, 8, 8))
        assert analyzer.adjacency() == AdjacencyType.NONE


# ── General rectangle fallback ───────────────────────────────────────


class TestAnalyzerGeneral:
    """Verify the analyzer falls back to general strategies."""

    def test_general_intersection_works(self) -> None:
        """General intersection is implemented and returns correct result."""
        a = Rectangle.from_points(
            Point(x=0, y=0), Point(x=1, y=0), Point(x=1, y=1), Point(x=0, y=1)
        )
        b = _r(0, 0, 2, 2)
        analyzer = RectangleAnalyzer(a, b)
        result = analyzer.intersection()
        # a is fully inside b, so all 4 corners of a are returned
        assert len(result) == 4

    def test_general_containment_works(self) -> None:
        """General containment is implemented and returns correct result."""
        a = Rectangle.from_points(
            Point(x=0, y=0), Point(x=1, y=0), Point(x=1, y=1), Point(x=0, y=1)
        )
        b = _r(0, 0, 2, 2)
        analyzer = RectangleAnalyzer(a, b, strategy=StrategyType.GENERAL)
        assert analyzer.containment() == "B contains A"

    def test_general_adjacency_works(self) -> None:
        """General adjacency is implemented and returns correct result."""
        a = Rectangle.from_points(
            Point(x=0, y=0), Point(x=1, y=0), Point(x=1, y=1), Point(x=0, y=1)
        )
        b = _r(0, 0, 2, 2)
        analyzer = RectangleAnalyzer(a, b, strategy=StrategyType.GENERAL)
        assert analyzer.adjacency() == AdjacencyType.SUB_LINE
