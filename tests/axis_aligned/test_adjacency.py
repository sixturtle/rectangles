"""Tests for adjacency detection on axis-aligned rectangles."""

from __future__ import annotations

import pytest

from rectangles.axis_aligned import AAAdjacency
from rectangles.rectangle import Rectangle
from rectangles.strategies import AdjacencyType


def _r(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


@pytest.fixture()
def strategy() -> AAAdjacency:
    """Reusable adjacency strategy instance."""
    return AAAdjacency()


# ── Proper adjacency (entire side coincides) ──────────────────────────


class TestProperAdjacency:
    """Both rectangles share an entire, identical side."""

    def test_proper_right_left(self, strategy: AAAdjacency) -> None:
        """A's right side is exactly B's left side."""
        a = _r(0, 0, 3, 4)
        b = _r(3, 0, 6, 4)
        assert strategy.check(a, b) == AdjacencyType.PROPER

    def test_proper_left_right(self, strategy: AAAdjacency) -> None:
        """B's right side is exactly A's left side (reversed order)."""
        a = _r(3, 0, 6, 4)
        b = _r(0, 0, 3, 4)
        assert strategy.check(a, b) == AdjacencyType.PROPER

    def test_proper_top_bottom(self, strategy: AAAdjacency) -> None:
        """A's top side is exactly B's bottom side."""
        a = _r(0, 0, 4, 3)
        b = _r(0, 3, 4, 6)
        assert strategy.check(a, b) == AdjacencyType.PROPER

    def test_proper_bottom_top(self, strategy: AAAdjacency) -> None:
        """B's top side is exactly A's bottom side (reversed order)."""
        a = _r(0, 3, 4, 6)
        b = _r(0, 0, 4, 3)
        assert strategy.check(a, b) == AdjacencyType.PROPER


# ── Sub-line adjacency (one side fully contained in the other) ────────


class TestSubLineAdjacency:
    """One rectangle's full side lies within the other's side."""

    def test_subline_right_left_b_smaller(self, strategy: AAAdjacency) -> None:
        """B's left side is a sub-line of A's right side (B shorter)."""
        a = _r(0, 0, 3, 6)
        b = _r(3, 1, 6, 5)
        assert strategy.check(a, b) == AdjacencyType.SUB_LINE

    def test_subline_right_left_a_smaller(self, strategy: AAAdjacency) -> None:
        """A's right side is a sub-line of B's left side (A shorter)."""
        a = _r(0, 1, 3, 5)
        b = _r(3, 0, 6, 6)
        assert strategy.check(a, b) == AdjacencyType.SUB_LINE

    def test_subline_top_bottom_b_smaller(self, strategy: AAAdjacency) -> None:
        """B's bottom side is a sub-line of A's top side (B narrower)."""
        a = _r(0, 0, 6, 3)
        b = _r(1, 3, 5, 6)
        assert strategy.check(a, b) == AdjacencyType.SUB_LINE

    def test_subline_top_bottom_a_smaller(self, strategy: AAAdjacency) -> None:
        """A's top side is a sub-line of B's bottom side (A narrower)."""
        a = _r(1, 0, 5, 3)
        b = _r(0, 3, 6, 6)
        assert strategy.check(a, b) == AdjacencyType.SUB_LINE


# ── Partial adjacency (sides partially overlap) ──────────────────────


class TestPartialAdjacency:
    """Sides share some segment but neither fully contains the other."""

    def test_partial_right_left(self, strategy: AAAdjacency) -> None:
        """A's right side partially overlaps B's left side vertically."""
        a = _r(0, 0, 3, 4)
        b = _r(3, 2, 6, 6)
        assert strategy.check(a, b) == AdjacencyType.PARTIAL

    def test_partial_left_right(self, strategy: AAAdjacency) -> None:
        """Reversed: B's right side partially overlaps A's left side."""
        a = _r(3, 2, 6, 6)
        b = _r(0, 0, 3, 4)
        assert strategy.check(a, b) == AdjacencyType.PARTIAL

    def test_partial_top_bottom(self, strategy: AAAdjacency) -> None:
        """A's top side partially overlaps B's bottom side horizontally."""
        a = _r(0, 0, 4, 3)
        b = _r(2, 3, 6, 6)
        assert strategy.check(a, b) == AdjacencyType.PARTIAL

    def test_partial_bottom_top(self, strategy: AAAdjacency) -> None:
        """Reversed: B's top side partially overlaps A's bottom side."""
        a = _r(2, 3, 6, 6)
        b = _r(0, 0, 4, 3)
        assert strategy.check(a, b) == AdjacencyType.PARTIAL


# ── No adjacency ─────────────────────────────────────────────────────


class TestNoAdjacency:
    """Rectangles do not share any side."""

    def test_separated_horizontally(self, strategy: AAAdjacency) -> None:
        """Rectangles are separated with a gap horizontally."""
        a = _r(0, 0, 2, 2)
        b = _r(5, 0, 7, 2)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_separated_vertically(self, strategy: AAAdjacency) -> None:
        """Rectangles are separated with a gap vertically."""
        a = _r(0, 0, 2, 2)
        b = _r(0, 5, 2, 7)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_overlapping(self, strategy: AAAdjacency) -> None:
        """Rectangles overlap (not merely adjacent)."""
        a = _r(0, 0, 4, 4)
        b = _r(2, 2, 6, 6)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_corner_touching_only(self, strategy: AAAdjacency) -> None:
        """Only a single corner point is shared — not a side."""
        a = _r(0, 0, 3, 3)
        b = _r(3, 3, 6, 6)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_contained(self, strategy: AAAdjacency) -> None:
        """One rectangle fully inside the other (no shared sides)."""
        a = _r(0, 0, 10, 10)
        b = _r(2, 2, 5, 5)
        assert strategy.check(a, b) == AdjacencyType.NONE


# ── Symmetry ─────────────────────────────────────────────────────────


class TestSymmetry:
    """check(a, b) should equal check(b, a)."""

    @pytest.mark.parametrize(
        ("a", "b"),
        [
            (_r(0, 0, 3, 4), _r(3, 0, 6, 4)),  # proper
            (_r(0, 0, 3, 6), _r(3, 1, 6, 5)),  # sub-line
            (_r(0, 0, 3, 4), _r(3, 2, 6, 6)),  # partial
            (_r(0, 0, 2, 2), _r(5, 0, 7, 2)),  # none
        ],
        ids=["proper", "subline", "partial", "none"],
    )
    def test_commutative(
        self, strategy: AAAdjacency, a: Rectangle, b: Rectangle
    ) -> None:
        """Test swapping a and b."""
        assert strategy.check(a, b) == strategy.check(b, a)
