"""Tests for general intersection (polygon vertex enumeration).

Focus: rotated/general rectangles. Only a couple of AA tests for parity.
"""

from __future__ import annotations

import pytest

from rectangles.general.intersection import GeneralIntersection
from rectangles.rectangle import Point, Rectangle


def _aa(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


def _p(x: float, y: float) -> Point:
    """Shortcut to create a point."""
    return Point(x=x, y=y)


def _rotated(cx: float, cy: float, hw: float, hh: float, angle: float) -> Rectangle:
    """Rectangle centered at (cx, cy) with half-width/height, rotated *angle*°."""
    return Rectangle.from_coords(cx - hw, cy - hh, cx + hw, cy + hh).rotated(angle)


@pytest.fixture()
def strategy() -> GeneralIntersection:
    """Reusable intersection strategy instance."""
    return GeneralIntersection()


# ── AA parity (minimal) ─────────────────────────────────────────────


class TestAxisAlignedParity:
    """Smoke tests: general algorithm agrees with AA on simple cases."""

    def test_aa_overlap(self, strategy: GeneralIntersection) -> None:
        """Partial overlap includes edge crossings + inner corners."""
        result = strategy.find_points(_aa(0, 0, 5, 5), _aa(3, 3, 8, 8))
        assert _p(3, 5) in result  # crossing
        assert _p(5, 3) in result  # crossing
        assert _p(3, 3) in result  # corner of B inside A
        assert _p(5, 5) in result  # corner of A inside B

    def test_aa_disjoint(self, strategy: GeneralIntersection) -> None:
        """Separated AA rectangles produce no points."""
        assert strategy.find_points(_aa(0, 0, 2, 2), _aa(5, 5, 8, 8)) == []


# ── Rotated containment ──────────────────────────────────────────────


class TestRotatedContainment:
    """Rotated rectangle fully inside another — only corner points returned."""

    def test_small_45_inside_large_aa(self, strategy: GeneralIntersection) -> None:
        """Small 45° rotated rect centered inside large AA rect."""
        outer = _aa(0, 0, 10, 10)
        inner = _rotated(5, 5, 1, 1, 45)
        result = strategy.find_points(outer, inner)
        assert len(result) == 4
        # All 4 corners of inner should be present
        for corner in [inner.p1, inner.p2, inner.p3, inner.p4]:
            assert corner in result

    def test_large_aa_inside_large_rotated(self, strategy: GeneralIntersection) -> None:
        """AA rectangle contained inside a larger 45° diamond."""
        outer = _rotated(5, 5, 5, 5, 45)  # diamond ~7.07 half-diagonal
        inner = _aa(3, 3, 7, 7)  # 4×4 box centered at (5,5)
        result = strategy.find_points(outer, inner)
        # All 4 corners of inner are inside the diamond
        assert len(result) == 4

    def test_both_rotated_containment(self, strategy: GeneralIntersection) -> None:
        """Small 30° rect inside a larger 30° rect (same rotation)."""
        outer = _rotated(5, 5, 4, 4, 30)
        inner = _rotated(5, 5, 1, 1, 30)
        result = strategy.find_points(outer, inner)
        assert len(result) == 4


# ── Rotated overlap (edge crossings + corners) ──────────────────────


class TestRotatedOverlap:
    """Rotated rectangles partially overlapping."""

    def test_45_diamond_overlaps_aa(self, strategy: GeneralIntersection) -> None:
        """45° diamond partially overlapping an AA rectangle."""
        diamond = _rotated(0, 0, 2, 2, 45)  # tips at ±2√2 ≈ ±2.83
        box = _aa(0, 0, 5, 5)
        result = strategy.find_points(diamond, box)
        # Should have both crossing points and corners inside
        assert len(result) > 0
        # Diamond's right tip (≈2.83, 0) is inside the box
        # At least some corners of the diamond are inside the box
        corners_inside = [
            c
            for c in [diamond.p1, diamond.p2, diamond.p3, diamond.p4]
            if 0 <= c.x <= 5 and 0 <= c.y <= 5
        ]
        for c in corners_inside:
            assert c in result

    def test_two_45_diamonds_overlap(self, strategy: GeneralIntersection) -> None:
        """Two identical 45° diamonds shifted horizontally — partial overlap."""
        a = _rotated(0, 0, 2, 2, 45)
        b = _rotated(3, 0, 2, 2, 45)
        result = strategy.find_points(a, b)
        # They overlap in the middle; should have crossing points
        assert len(result) > 0

    def test_rotated_30_overlaps_aa(self, strategy: GeneralIntersection) -> None:
        """30° rotated rectangle partially overlapping an AA rectangle."""
        rotated = _rotated(3, 3, 3, 2, 30)
        box = _aa(0, 0, 4, 4)
        result = strategy.find_points(rotated, box)
        assert len(result) > 0  # some overlap exists

    def test_different_angles_overlap(self, strategy: GeneralIntersection) -> None:
        """Two rectangles at different angles overlapping."""
        a = _rotated(3, 3, 3, 1, 20)
        b = _rotated(3, 3, 3, 1, -20)
        result = strategy.find_points(a, b)
        # Same center, different angles — they form an X pattern
        assert len(result) > 0


# ── Rotated disjoint ─────────────────────────────────────────────────


class TestRotatedDisjoint:
    """Rotated rectangles with no overlap."""

    def test_separated_same_angle(self, strategy: GeneralIntersection) -> None:
        """Two 30° rectangles far apart."""
        a = _rotated(0, 0, 2, 1, 30)
        b = _rotated(10, 10, 2, 1, 30)
        assert strategy.find_points(a, b) == []

    def test_separated_different_angles(self, strategy: GeneralIntersection) -> None:
        """Two rectangles at different angles, far apart."""
        a = _rotated(0, 0, 2, 1, 45)
        b = _rotated(20, 20, 2, 1, 60)
        assert strategy.find_points(a, b) == []

    def test_nearby_but_no_overlap(self, strategy: GeneralIntersection) -> None:
        """Rotated rectangles close together but not touching."""
        a = _rotated(0, 0, 1, 1, 45)  # diamond with tips at ≈±1.41
        b = _rotated(4, 0, 1, 1, 45)
        assert strategy.find_points(a, b) == []


# ── Result properties ────────────────────────────────────────────────


class TestResultProperties:
    """Output should be sorted and deduplicated."""

    def test_sorted_output(self, strategy: GeneralIntersection) -> None:
        """Points from rotated intersection are in (x, y) order."""
        a = _rotated(3, 3, 3, 2, 30)
        b = _aa(0, 0, 4, 4)
        result = strategy.find_points(a, b)
        assert result == sorted(result)

    def test_no_duplicates(self, strategy: GeneralIntersection) -> None:
        """No duplicate points in output."""
        a = _rotated(5, 5, 1, 1, 45)
        b = _aa(0, 0, 10, 10)
        result = strategy.find_points(a, b)
        assert len(result) == len(set(result))


# ── Commutativity ────────────────────────────────────────────────────


class TestCommutativity:
    """find_points(a, b) == find_points(b, a)."""

    @pytest.mark.parametrize(
        ("a", "b"),
        [
            (_rotated(5, 5, 1, 1, 45), _aa(0, 0, 10, 10)),  # containment
            (_rotated(0, 0, 2, 2, 45), _aa(0, 0, 5, 5)),  # overlap
            (_rotated(0, 0, 1, 1, 30), _rotated(10, 10, 1, 1, 60)),  # disjoint
            (_rotated(3, 3, 3, 1, 20), _rotated(3, 3, 3, 1, -20)),  # X pattern
        ],
        ids=["containment", "overlap", "disjoint", "x_pattern"],
    )
    def test_commutative(
        self, strategy: GeneralIntersection, a: Rectangle, b: Rectangle
    ) -> None:
        """Test swapping a and b."""
        assert strategy.find_points(a, b) == strategy.find_points(b, a)
