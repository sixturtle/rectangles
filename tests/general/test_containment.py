"""Tests for general containment using point-in-polygon.

Focus: rotated/general rectangles. Only a couple of AA tests for parity.
"""

from __future__ import annotations

import pytest

from rectangles.general.containment import GeneralContainment
from rectangles.rectangle import Rectangle


def _aa(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


def _rotated(cx: float, cy: float, hw: float, hh: float, angle: float) -> Rectangle:
    """Rectangle centered at (cx, cy) with half-width/height, rotated *angle*°."""
    return Rectangle.from_coords(cx - hw, cy - hh, cx + hw, cy + hh).rotated(angle)


@pytest.fixture()
def strategy() -> GeneralContainment:
    """Reusable containment strategy instance."""
    return GeneralContainment()


# ── AA parity (minimal) ─────────────────────────────────────────────


class TestAxisAlignedParity:
    """Smoke tests: general algorithm agrees with AA on simple cases."""

    def test_aa_containment(self, strategy: GeneralContainment) -> None:
        """A contains B for axis-aligned rectangles."""
        assert strategy.check(_aa(0, 0, 10, 10), _aa(2, 2, 5, 5)) == "A contains B"

    def test_aa_no_containment(self, strategy: GeneralContainment) -> None:
        """No containment for overlapping AA rectangles."""
        assert strategy.check(_aa(0, 0, 5, 5), _aa(3, 3, 8, 8)) == "No containment"


# ── Rotated inside AA ────────────────────────────────────────────────


class TestRotatedInsideAA:
    """Rotated rectangle contained within an axis-aligned rectangle."""

    def test_small_45_inside_large(self, strategy: GeneralContainment) -> None:
        """Small 45° rotated rect fits inside large AA rect."""
        assert (
            strategy.check(_aa(0, 0, 10, 10), _rotated(5, 5, 1, 1, 45))
            == "A contains B"
        )

    def test_small_30_inside_large(self, strategy: GeneralContainment) -> None:
        """Small 30° rotated rect fits inside large AA rect."""
        assert (
            strategy.check(_aa(0, 0, 10, 10), _rotated(5, 5, 1, 1, 30))
            == "A contains B"
        )

    def test_small_60_inside_large(self, strategy: GeneralContainment) -> None:
        """Small 60° rotated rect fits inside large AA rect."""
        assert (
            strategy.check(_aa(0, 0, 10, 10), _rotated(5, 5, 1, 1, 60))
            == "A contains B"
        )

    def test_rotated_exceeds_boundary(self, strategy: GeneralContainment) -> None:
        """Rotated rect's corners poke outside the AA rect."""
        # 2×2 rect at center (2,2) rotated 45°: corners reach ≈ 4.83
        assert (
            strategy.check(_aa(0, 0, 4, 4), _rotated(2, 2, 2, 2, 45))
            == "No containment"
        )


# ── AA inside rotated ────────────────────────────────────────────────


class TestAAInsideRotated:
    """AA rectangle contained within a rotated rectangle."""

    def test_small_aa_inside_large_diamond(self, strategy: GeneralContainment) -> None:
        """Small AA rect inside a large 45° diamond."""
        diamond = _rotated(5, 5, 5, 5, 45)  # tips ~7.07 from center
        small = _aa(4, 4, 6, 6)  # 2×2 box at center
        assert strategy.check(diamond, small) == "A contains B"

    def test_aa_exceeds_diamond(self, strategy: GeneralContainment) -> None:
        """AA rect corners extend beyond the diamond."""
        diamond = _rotated(5, 5, 3, 3, 45)  # tips ~4.24 from center
        big_box = _aa(1, 1, 9, 9)
        assert strategy.check(diamond, big_box) == "No containment"


# ── Both rotated ─────────────────────────────────────────────────────


class TestBothRotated:
    """Both rectangles are rotated."""

    def test_same_angle_containment(self, strategy: GeneralContainment) -> None:
        """Small and large rect at the same angle — containment."""
        outer = _rotated(5, 5, 4, 3, 30)
        inner = _rotated(5, 5, 1, 1, 30)
        assert strategy.check(outer, inner) == "A contains B"

    def test_same_angle_no_containment(self, strategy: GeneralContainment) -> None:
        """Same angle but inner is too big."""
        a = _rotated(5, 5, 2, 2, 30)
        b = _rotated(5, 5, 3, 3, 30)
        assert strategy.check(a, b) == "B contains A"

    def test_different_angles_no_containment(
        self, strategy: GeneralContainment
    ) -> None:
        """Different angles, similar sizes — no containment."""
        a = _rotated(5, 5, 3, 1, 20)
        b = _rotated(5, 5, 3, 1, -20)
        assert strategy.check(a, b) == "No containment"

    def test_different_angles_containment(self, strategy: GeneralContainment) -> None:
        """Large outer at 15° containing small inner at 75°."""
        outer = _rotated(5, 5, 5, 5, 15)
        inner = _rotated(5, 5, 1, 1, 75)
        assert strategy.check(outer, inner) == "A contains B"

    def test_identical_rotated(self, strategy: GeneralContainment) -> None:
        """Identical rotated rectangles — A wins."""
        a = _rotated(5, 5, 3, 2, 45)
        assert strategy.check(a, a) == "A contains B"


# ── Disjoint rotated ─────────────────────────────────────────────────


class TestRotatedDisjoint:
    """Rotated rectangles with no overlap — no containment."""

    def test_separated_same_angle(self, strategy: GeneralContainment) -> None:
        """Two 45° rectangles far apart."""
        a = _rotated(0, 0, 2, 1, 45)
        b = _rotated(10, 10, 2, 1, 45)
        assert strategy.check(a, b) == "No containment"

    def test_separated_different_angles(self, strategy: GeneralContainment) -> None:
        """Different angles, far apart."""
        a = _rotated(0, 0, 2, 1, 30)
        b = _rotated(20, 20, 2, 1, 60)
        assert strategy.check(a, b) == "No containment"


# ── Symmetry ─────────────────────────────────────────────────────────


class TestSymmetry:
    """Swapping a and b should swap the containment label."""

    @pytest.mark.parametrize(
        ("a", "b", "expected_ab", "expected_ba"),
        [
            (
                _aa(0, 0, 10, 10),
                _rotated(5, 5, 1, 1, 45),
                "A contains B",
                "B contains A",
            ),
            (
                _rotated(5, 5, 3, 1, 20),
                _rotated(5, 5, 3, 1, -20),
                "No containment",
                "No containment",
            ),
            (
                _rotated(5, 5, 4, 3, 30),
                _rotated(5, 5, 1, 1, 30),
                "A contains B",
                "B contains A",
            ),
        ],
        ids=["aa_contains_rotated", "no_containment_x_pattern", "both_rotated"],
    )
    def test_swap(
        self,
        strategy: GeneralContainment,
        a: Rectangle,
        b: Rectangle,
        expected_ab: str,
        expected_ba: str,
    ) -> None:
        """Test swapping a and b."""
        assert strategy.check(a, b) == expected_ab
        assert strategy.check(b, a) == expected_ba
