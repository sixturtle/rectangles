"""Tests for Util.collinear_segments."""

from __future__ import annotations

from rectangles.rectangle import Point, Segment
from rectangles.strategies import AdjacencyType
from rectangles.util import Util


def _seg(x1: float, y1: float, x2: float, y2: float) -> Segment:
    """Shortcut to create a segment."""
    return Segment(p1=Point(x=x1, y=y1), p2=Point(x=x2, y=y2))


# ── Proper (identical edges) ─────────────────────────────────────────


class TestProper:
    """Segments are collinear and cover exactly the same range."""

    def test_identical_horizontal(self) -> None:
        """Two identical horizontal segments."""
        a = _seg(0, 0, 4, 0)
        b = _seg(0, 0, 4, 0)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.PROPER

    def test_identical_vertical(self) -> None:
        """Two identical vertical segments."""
        a = _seg(0, 0, 0, 5)
        b = _seg(0, 0, 0, 5)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.PROPER

    def test_identical_diagonal(self) -> None:
        """Two identical diagonal segments."""
        a = _seg(0, 0, 3, 4)
        b = _seg(0, 0, 3, 4)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.PROPER

    def test_reversed_direction(self) -> None:
        """Same line but B goes in reverse direction."""
        a = _seg(0, 0, 4, 0)
        b = _seg(4, 0, 0, 0)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.PROPER


# ── Sub-line (one fully contained in the other) ──────────────────────


class TestSubLine:
    """One segment is entirely within the other."""

    def test_b_inside_a(self) -> None:
        """B is a sub-segment of A."""
        a = _seg(0, 0, 10, 0)
        b = _seg(2, 0, 7, 0)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.SUB_LINE

    def test_a_inside_b(self) -> None:
        """A is a sub-segment of B."""
        a = _seg(2, 0, 7, 0)
        b = _seg(0, 0, 10, 0)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.SUB_LINE

    def test_diagonal_sub_line(self) -> None:
        """Sub-line on a diagonal."""
        a = _seg(0, 0, 6, 6)
        b = _seg(1, 1, 4, 4)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.SUB_LINE


# ── Partial overlap ──────────────────────────────────────────────────


class TestPartial:
    """Segments overlap partially but neither contains the other."""

    def test_horizontal_partial(self) -> None:
        """Overlapping horizontal segments."""
        a = _seg(0, 0, 5, 0)
        b = _seg(3, 0, 8, 0)
        result = Util.collinear_segments(a, b)
        assert result is not None
        shared, adj = result
        assert adj == AdjacencyType.PARTIAL
        # Shared region should be [3, 5] on the x-axis
        assert abs(shared.p1.x - 3) < 1e-9
        assert abs(shared.p2.x - 5) < 1e-9

    def test_vertical_partial(self) -> None:
        """Overlapping vertical segments."""
        a = _seg(0, 0, 0, 5)
        b = _seg(0, 3, 0, 8)
        result = Util.collinear_segments(a, b)
        assert result is not None
        _, adj = result
        assert adj == AdjacencyType.PARTIAL


# ── No overlap (collinear but disjoint, or not collinear) ────────────


class TestNoOverlap:
    """Segments that don't produce a shared collinear segment."""

    def test_collinear_gap(self) -> None:
        """Collinear segments separated by a gap."""
        a = _seg(0, 0, 3, 0)
        b = _seg(5, 0, 8, 0)
        assert Util.collinear_segments(a, b) is None

    def test_collinear_touch_at_point(self) -> None:
        """Collinear segments sharing only an endpoint (zero-length overlap)."""
        a = _seg(0, 0, 3, 0)
        b = _seg(3, 0, 6, 0)
        assert Util.collinear_segments(a, b) is None

    def test_not_collinear_parallel(self) -> None:
        """Parallel but offset segments."""
        a = _seg(0, 0, 5, 0)
        b = _seg(0, 1, 5, 1)
        assert Util.collinear_segments(a, b) is None

    def test_not_collinear_crossing(self) -> None:
        """Perpendicular segments."""
        a = _seg(0, 0, 5, 0)
        b = _seg(2, -2, 2, 2)
        assert Util.collinear_segments(a, b) is None


# ── Commutativity ────────────────────────────────────────────────────


class TestCommutativity:
    """collinear_segments(a, b) and collinear_segments(b, a) should agree on type."""

    def test_partial_commutative(self) -> None:
        """Swapping a and b should give the same adjacency type."""
        a = _seg(0, 0, 5, 0)
        b = _seg(3, 0, 8, 0)
        r1 = Util.collinear_segments(a, b)
        r2 = Util.collinear_segments(b, a)
        assert r1 is not None and r2 is not None
        assert r1[1] == r2[1]

    def test_sub_line_commutative(self) -> None:
        """Sub-line classification is the same regardless of order."""
        a = _seg(0, 0, 10, 0)
        b = _seg(2, 0, 7, 0)
        r1 = Util.collinear_segments(a, b)
        r2 = Util.collinear_segments(b, a)
        assert r1 is not None and r2 is not None
        assert r1[1] == r2[1]
