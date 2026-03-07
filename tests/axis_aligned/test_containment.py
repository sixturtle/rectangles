"""Tests for containment detection on axis-aligned rectangles."""

from __future__ import annotations

import pytest

from rectangles.axis_aligned import AAContainment
from rectangles.rectangle import Rectangle


def _r(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


@pytest.fixture()
def strategy() -> AAContainment:
    """Reusable containment strategy instance."""
    return AAContainment()


# ── _contains() low-level predicate ──────────────────────────────────


class TestContains:
    """Tests for the internal _contains(outer, inner) predicate."""

    def test_inner_fully_inside(self, strategy: AAContainment) -> None:
        """Inner rectangle is strictly inside outer."""
        outer = _r(0, 0, 10, 10)
        inner = _r(2, 2, 5, 5)
        assert strategy._contains(outer, inner) is True

    def test_inner_shares_boundary(self, strategy: AAContainment) -> None:
        """Inner rectangle touches outer boundary (still contained)."""
        outer = _r(0, 0, 10, 10)
        inner = _r(0, 0, 5, 5)
        assert strategy._contains(outer, inner) is True

    def test_inner_is_identical(self, strategy: AAContainment) -> None:
        """Inner rectangle is exactly the same as outer."""
        a = _r(0, 0, 5, 5)
        assert strategy._contains(a, a) is True

    def test_inner_exceeds_right(self, strategy: AAContainment) -> None:
        """Inner extends beyond outer's right edge."""
        outer = _r(0, 0, 5, 5)
        inner = _r(1, 1, 6, 4)
        assert strategy._contains(outer, inner) is False

    def test_inner_exceeds_top(self, strategy: AAContainment) -> None:
        """Inner extends beyond outer's top edge."""
        outer = _r(0, 0, 5, 5)
        inner = _r(1, 1, 4, 6)
        assert strategy._contains(outer, inner) is False

    def test_inner_exceeds_left(self, strategy: AAContainment) -> None:
        """Inner extends beyond outer's left edge."""
        outer = _r(2, 0, 8, 8)
        inner = _r(0, 1, 5, 5)
        assert strategy._contains(outer, inner) is False

    def test_inner_exceeds_bottom(self, strategy: AAContainment) -> None:
        """Inner extends beyond outer's bottom edge."""
        outer = _r(0, 2, 8, 8)
        inner = _r(1, 0, 5, 5)
        assert strategy._contains(outer, inner) is False

    def test_no_overlap(self, strategy: AAContainment) -> None:
        """Rectangles are completely separate."""
        outer = _r(0, 0, 3, 3)
        inner = _r(5, 5, 8, 8)
        assert strategy._contains(outer, inner) is False

    def test_outer_inside_inner(self, strategy: AAContainment) -> None:
        """Outer is actually smaller — reversed containment."""
        outer = _r(2, 2, 5, 5)
        inner = _r(0, 0, 10, 10)
        assert strategy._contains(outer, inner) is False


# ── check() high-level method ────────────────────────────────────────


class TestCheckContainment:
    """Tests for the check(a, b) descriptor."""

    def test_a_contains_b(self, strategy: AAContainment) -> None:
        """A contains B."""
        a = _r(0, 0, 10, 10)
        b = _r(2, 2, 5, 5)
        assert strategy.check(a, b) == "A contains B"

    def test_b_contains_a(self, strategy: AAContainment) -> None:
        """B contains A."""
        a = _r(2, 2, 5, 5)
        b = _r(0, 0, 10, 10)
        assert strategy.check(a, b) == "B contains A"

    def test_no_containment_overlapping(self, strategy: AAContainment) -> None:
        """Partial overlap — neither contains the other."""
        a = _r(0, 0, 5, 5)
        b = _r(3, 3, 8, 8)
        assert strategy.check(a, b) == "No containment"

    def test_no_containment_separated(self, strategy: AAContainment) -> None:
        """Completely separate rectangles."""
        a = _r(0, 0, 2, 2)
        b = _r(5, 5, 8, 8)
        assert strategy.check(a, b) == "No containment"

    def test_no_containment_adjacent(self, strategy: AAContainment) -> None:
        """Adjacent rectangles (touching sides) — no containment."""
        a = _r(0, 0, 3, 3)
        b = _r(3, 0, 6, 3)
        assert strategy.check(a, b) == "No containment"

    def test_identical_returns_a_contains_b(self, strategy: AAContainment) -> None:
        """Identical rectangles — _contains() is True both ways, A wins."""
        a = _r(0, 0, 5, 5)
        b = _r(0, 0, 5, 5)
        assert strategy.check(a, b) == "A contains B"

    def test_inner_on_boundary(self, strategy: AAContainment) -> None:
        """Inner shares one full edge with outer."""
        a = _r(0, 0, 10, 10)
        b = _r(0, 0, 10, 5)
        assert strategy.check(a, b) == "A contains B"


# ── Symmetry ─────────────────────────────────────────────────────────


class TestContainmentSymmetry:
    """Swapping a and b should swap the result label."""

    @pytest.mark.parametrize(
        ("a", "b", "expected_ab", "expected_ba"),
        [
            (_r(0, 0, 10, 10), _r(2, 2, 5, 5), "A contains B", "B contains A"),
            (_r(0, 0, 5, 5), _r(3, 3, 8, 8), "No containment", "No containment"),
        ],
        ids=["containment", "no_containment"],
    )
    def test_swap(
        self,
        strategy: AAContainment,
        a: Rectangle,
        b: Rectangle,
        expected_ab: str,
        expected_ba: str,
    ) -> None:
        """Test swapping a and b."""
        assert strategy.check(a, b) == expected_ab
        assert strategy.check(b, a) == expected_ba
