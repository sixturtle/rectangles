"""Tests for Util.segments_intersect."""

from __future__ import annotations

from rectangles.rectangle import Point, Segment
from rectangles.util import Util


def _seg(x1: float, y1: float, x2: float, y2: float) -> Segment:
    """Shortcut to create a segment."""
    return Segment(p1=Point(x=x1, y=y1), p2=Point(x=x2, y=y2))


def _p(x: float, y: float) -> Point:
    """Shortcut to create a point."""
    return Point(x=x, y=y)


# ── Crossing segments ────────────────────────────────────────────────


class TestCrossing:
    """Segments that cross at a single point."""

    def test_x_cross_at_origin(self) -> None:
        """Two segments forming an X through the origin."""
        a = _seg(-1, -1, 1, 1)
        b = _seg(-1, 1, 1, -1)
        result = Util.segments_intersect(a, b)
        assert result is not None
        assert abs(result.x) < 1e-9
        assert abs(result.y) < 1e-9

    def test_perpendicular_cross(self) -> None:
        """Horizontal and vertical segments crossing."""
        a = _seg(0, 2, 6, 2)  # horizontal at y=2
        b = _seg(3, 0, 3, 4)  # vertical at x=3
        result = Util.segments_intersect(a, b)
        assert result is not None
        assert abs(result.x - 3) < 1e-9
        assert abs(result.y - 2) < 1e-9

    def test_diagonal_cross(self) -> None:
        """Two diagonal segments crossing off-center."""
        a = _seg(0, 0, 4, 4)
        b = _seg(0, 4, 4, 0)
        result = Util.segments_intersect(a, b)
        assert result is not None
        assert abs(result.x - 2) < 1e-9
        assert abs(result.y - 2) < 1e-9

    def test_cross_at_endpoint(self) -> None:
        """Segments meeting at one endpoint (T-junction)."""
        a = _seg(0, 0, 4, 0)
        b = _seg(2, 0, 2, 4)
        result = Util.segments_intersect(a, b)
        assert result is not None
        assert abs(result.x - 2) < 1e-9
        assert abs(result.y) < 1e-9


# ── Non-crossing segments ────────────────────────────────────────────


class TestNoCrossing:
    """Segments that do not intersect."""

    def test_parallel_horizontal(self) -> None:
        """Two parallel horizontal segments."""
        a = _seg(0, 0, 5, 0)
        b = _seg(0, 1, 5, 1)
        assert Util.segments_intersect(a, b) is None

    def test_collinear_overlapping(self) -> None:
        """Collinear overlapping segments (parallel, det ≈ 0)."""
        a = _seg(0, 0, 5, 0)
        b = _seg(3, 0, 8, 0)
        assert Util.segments_intersect(a, b) is None

    def test_collinear_disjoint(self) -> None:
        """Collinear but separated segments."""
        a = _seg(0, 0, 3, 0)
        b = _seg(5, 0, 8, 0)
        assert Util.segments_intersect(a, b) is None

    def test_lines_cross_but_segments_dont(self) -> None:
        """Lines would cross, but the segments are too short."""
        a = _seg(0, 0, 1, 1)
        b = _seg(5, 0, 6, -1)
        assert Util.segments_intersect(a, b) is None

    def test_perpendicular_miss(self) -> None:
        """Perpendicular but not overlapping."""
        a = _seg(0, 0, 2, 0)
        b = _seg(5, -1, 5, 1)
        assert Util.segments_intersect(a, b) is None


# ── Commutativity ────────────────────────────────────────────────────


class TestCommutativity:
    """segments_intersect(a, b) should equal segments_intersect(b, a)."""

    def test_crossing_commutative(self) -> None:
        """Crossing result is the same regardless of order."""
        a = _seg(0, 0, 4, 4)
        b = _seg(0, 4, 4, 0)
        r1 = Util.segments_intersect(a, b)
        r2 = Util.segments_intersect(b, a)
        assert r1 is not None and r2 is not None
        assert abs(r1.x - r2.x) < 1e-9
        assert abs(r1.y - r2.y) < 1e-9

    def test_no_crossing_commutative(self) -> None:
        """Non-crossing returns None both ways."""
        a = _seg(0, 0, 1, 1)
        b = _seg(5, 0, 6, -1)
        assert Util.segments_intersect(a, b) is None
        assert Util.segments_intersect(b, a) is None
