"""Tests for intersection detection on axis-aligned rectangles."""

from __future__ import annotations

import pytest

from rectangles.axis_aligned import AAIntersection
from rectangles.rectangle import Point, Rectangle


def _r(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


def _p(x: float, y: float) -> Point:
    """Shortcut to create a point."""
    return Point(x=x, y=y)


@pytest.fixture()
def strategy() -> AAIntersection:
    """Reusable intersection strategy instance."""
    return AAIntersection()


# ── Overlapping rectangles (produce intersection points) ─────────────


class TestOverlapping:
    """Two rectangles overlap — edges cross at specific points."""

    def test_overlap_two_points(self, strategy: AAIntersection) -> None:
        """Classic overlap producing two crossing points."""
        a = _r(0, 0, 5, 5)
        b = _r(3, 3, 8, 8)
        assert strategy.find_points(a, b) == [
            _p(3, 3),
            _p(3, 5),
            _p(5, 3),
            _p(5, 5),
        ]

    def test_overlap_narrow_rectangle(self, strategy: AAIntersection) -> None:
        """Narrow B overlaps A's right side only."""
        a = _r(0, 0, 5, 5)
        b = _r(3, 3, 8, 4)
        assert strategy.find_points(a, b) == [
            _p(3, 3),
            _p(3, 4),
            _p(5, 3),
            _p(5, 4),
        ]

    def test_overlap_bottom_left(self, strategy: AAIntersection) -> None:
        """B overlaps A from the bottom-left corner area."""
        a = _r(2, 2, 6, 6)
        b = _r(0, 0, 4, 4)
        assert strategy.find_points(a, b) == [
            _p(2, 2),
            _p(2, 4),
            _p(4, 2),
            _p(4, 4),
        ]

    def test_overlap_top_right(self, strategy: AAIntersection) -> None:
        """B overlaps A from the top-right corner area."""
        a = _r(0, 0, 4, 4)
        b = _r(2, 2, 6, 6)
        assert strategy.find_points(a, b) == [
            _p(2, 2),
            _p(2, 4),
            _p(4, 2),
            _p(4, 4),
        ]

    def test_cross_shaped_four_points(self, strategy: AAIntersection) -> None:
        """Cross-shaped overlap producing four intersection points."""
        a = _r(0, 2, 6, 4)
        b = _r(2, 0, 4, 6)
        assert strategy.find_points(a, b) == [_p(2, 2), _p(2, 4), _p(4, 2), _p(4, 4)]


# ── Containment (no edges cross) ────────────────────────────────────


class TestContainment:
    """One rectangle inside another — returns inner rectangle vertices."""

    def test_a_contains_b(self, strategy: AAIntersection) -> None:
        """B is fully inside A — returns B's corners."""
        a = _r(0, 0, 10, 10)
        b = _r(2, 2, 5, 5)
        assert strategy.find_points(a, b) == [
            _p(2, 2),
            _p(2, 5),
            _p(5, 2),
            _p(5, 5),
        ]

    def test_b_contains_a(self, strategy: AAIntersection) -> None:
        """A is fully inside B — returns A's corners."""
        a = _r(2, 2, 5, 5)
        b = _r(0, 0, 10, 10)
        assert strategy.find_points(a, b) == [
            _p(2, 2),
            _p(2, 5),
            _p(5, 2),
            _p(5, 5),
        ]

    def test_identical_rectangles(self, strategy: AAIntersection) -> None:
        """Identical rectangles — returns the shared rectangle's corners."""
        a = _r(0, 0, 5, 5)
        b = _r(0, 0, 5, 5)
        assert strategy.find_points(a, b) == [
            _p(0, 0),
            _p(0, 5),
            _p(5, 0),
            _p(5, 5),
        ]


# ── Adjacency (touching sides — no crossing) ────────────────────────


class TestAdjacent:
    """Rectangles share a side or partial side — strict inequality excludes these."""

    def test_adjacent_right_left(self, strategy: AAIntersection) -> None:
        """A's right side touches B's left side."""
        a = _r(0, 0, 5, 5)
        b = _r(5, 0, 8, 8)
        assert strategy.find_points(a, b) == []

    def test_adjacent_top_bottom(self, strategy: AAIntersection) -> None:
        """A's top side touches B's bottom side."""
        a = _r(0, 0, 5, 5)
        b = _r(0, 5, 5, 10)
        assert strategy.find_points(a, b) == []

    def test_corner_touching(self, strategy: AAIntersection) -> None:
        """Rectangles share only a single corner point."""
        a = _r(0, 0, 3, 3)
        b = _r(3, 3, 6, 6)
        assert strategy.find_points(a, b) == []


# ── Disjoint (no contact at all) ─────────────────────────────────────


class TestDisjoint:
    """Rectangles are completely separated."""

    def test_separated_horizontally(self, strategy: AAIntersection) -> None:
        """Gap between rectangles on the x-axis."""
        a = _r(0, 0, 3, 3)
        b = _r(6, 0, 9, 3)
        assert strategy.find_points(a, b) == []

    def test_separated_vertically(self, strategy: AAIntersection) -> None:
        """Gap between rectangles on the y-axis."""
        a = _r(0, 0, 3, 3)
        b = _r(0, 6, 3, 9)
        assert strategy.find_points(a, b) == []


# ── Result ordering and deduplication ────────────────────────────────


class TestResultProperties:
    """Verify the output list is sorted and deduplicated."""

    def test_sorted_by_x_then_y(self, strategy: AAIntersection) -> None:
        """Points should be returned in lexicographic (x, y) order."""
        a = _r(0, 2, 6, 4)
        b = _r(2, 0, 4, 6)
        result = strategy.find_points(a, b)
        assert result == sorted(result)

    def test_no_duplicates(self, strategy: AAIntersection) -> None:
        """Each intersection point appears exactly once."""
        a = _r(0, 0, 5, 5)
        b = _r(3, 3, 8, 8)
        result = strategy.find_points(a, b)
        assert len(result) == len(set(result))


# ── Commutativity ────────────────────────────────────────────────────


class TestCommutativity:
    """find_points(a, b) should equal find_points(b, a)."""

    @pytest.mark.parametrize(
        ("a", "b"),
        [
            (_r(0, 0, 5, 5), _r(3, 3, 8, 8)),  # overlapping
            (_r(0, 0, 10, 10), _r(2, 2, 5, 5)),  # containment
            (_r(0, 0, 5, 5), _r(5, 0, 8, 8)),  # adjacent
            (_r(0, 0, 3, 3), _r(6, 0, 9, 3)),  # disjoint
            (_r(0, 2, 6, 4), _r(2, 0, 4, 6)),  # cross-shaped
        ],
        ids=["overlapping", "containment", "adjacent", "disjoint", "cross"],
    )
    def test_commutative(
        self, strategy: AAIntersection, a: Rectangle, b: Rectangle
    ) -> None:
        """Test swapping a and b."""
        assert strategy.find_points(a, b) == strategy.find_points(b, a)
