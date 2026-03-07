"""Tests for general adjacency using collinear edge-segment overlap.

Focus: rotated/general rectangles. Only a couple of AA tests for parity.
"""

from __future__ import annotations

import math

import pytest

from rectangles.general.adjacency import GeneralAdjacency
from rectangles.rectangle import Rectangle
from rectangles.strategies import AdjacencyType


def _aa(x1: float, y1: float, x2: float, y2: float) -> Rectangle:
    """Shortcut to create an axis-aligned rectangle."""
    return Rectangle.from_coords(x1, y1, x2, y2)


def _rotated(cx: float, cy: float, hw: float, hh: float, angle: float) -> Rectangle:
    """Rectangle centered at (cx, cy) with half-width/height, rotated *angle*°."""
    return Rectangle.from_coords(cx - hw, cy - hh, cx + hw, cy + hh).rotated(angle)


@pytest.fixture()
def strategy() -> GeneralAdjacency:
    """Reusable adjacency strategy instance."""
    return GeneralAdjacency()


# ── AA parity (minimal) ─────────────────────────────────────────────


class TestAxisAlignedParity:
    """Smoke tests: general algorithm agrees with AA on simple cases."""

    def test_aa_proper(self, strategy: GeneralAdjacency) -> None:
        """Proper adjacency for AA rectangles."""
        assert strategy.check(_aa(0, 0, 3, 4), _aa(3, 0, 6, 4)) == AdjacencyType.PROPER

    def test_aa_none(self, strategy: GeneralAdjacency) -> None:
        """No adjacency for separated AA rectangles."""
        assert strategy.check(_aa(0, 0, 2, 2), _aa(5, 0, 7, 2)) == AdjacencyType.NONE


# ── Rotated proper adjacency ────────────────────────────────────────


class TestRotatedProper:
    """Two rotated rectangles sharing a full edge."""

    def test_same_angle_proper(self, strategy: GeneralAdjacency) -> None:
        """Two rectangles at 30°, sharing a full edge.

        Adjacent AA rects (0,0,3,4)-(3,0,6,4) rotated together by 30°
        should still share a full edge.
        """
        center = (3.0, 2.0)
        a = _aa(0, 0, 3, 4).rotated(30, center=center)
        b = _aa(3, 0, 6, 4).rotated(30, center=center)
        assert strategy.check(a, b) == AdjacencyType.PROPER

    def test_same_angle_proper_vertical(self, strategy: GeneralAdjacency) -> None:
        """Vertical adjacency rotated together stays proper."""
        center = (2.0, 3.0)
        a = _aa(0, 0, 4, 3).rotated(45, center=center)
        b = _aa(0, 3, 4, 6).rotated(45, center=center)
        assert strategy.check(a, b) == AdjacencyType.PROPER


# ── Rotated sub-line adjacency ───────────────────────────────────────


class TestRotatedSubLine:
    """One shared edge is a sub-line of the other."""

    def test_same_angle_sub_line(self, strategy: GeneralAdjacency) -> None:
        """Sub-line adjacency at 30°: short side inside long side."""
        center = (3.0, 3.0)
        a = _aa(0, 0, 3, 6).rotated(30, center=center)
        b = _aa(3, 1, 6, 5).rotated(30, center=center)
        assert strategy.check(a, b) == AdjacencyType.SUB_LINE

    def test_same_angle_sub_line_reversed(self, strategy: GeneralAdjacency) -> None:
        """Sub-line adjacency at 45°, shorter rect has the shorter edge."""
        center = (3.0, 3.0)
        a = _aa(0, 1, 3, 5).rotated(45, center=center)
        b = _aa(3, 0, 6, 6).rotated(45, center=center)
        assert strategy.check(a, b) == AdjacencyType.SUB_LINE


# ── Rotated partial adjacency ───────────────────────────────────────


class TestRotatedPartial:
    """Edges partially overlap."""

    def test_same_angle_partial(self, strategy: GeneralAdjacency) -> None:
        """Partial adjacency at 30°."""
        center = (3.0, 3.0)
        a = _aa(0, 0, 3, 4).rotated(30, center=center)
        b = _aa(3, 2, 6, 6).rotated(30, center=center)
        assert strategy.check(a, b) == AdjacencyType.PARTIAL

    def test_same_angle_partial_45(self, strategy: GeneralAdjacency) -> None:
        """Partial adjacency at 45°."""
        center = (3.0, 3.0)
        a = _aa(0, 0, 4, 3).rotated(45, center=center)
        b = _aa(2, 3, 6, 6).rotated(45, center=center)
        assert strategy.check(a, b) == AdjacencyType.PARTIAL


# ── Rotated no adjacency ────────────────────────────────────────────


class TestRotatedNone:
    """Rotated rectangles with no shared collinear edges."""

    def test_separated_same_angle(self, strategy: GeneralAdjacency) -> None:
        """Two 30° rectangles far apart."""
        a = _rotated(0, 0, 2, 1, 30)
        b = _rotated(10, 10, 2, 1, 30)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_overlapping_same_angle(self, strategy: GeneralAdjacency) -> None:
        """Overlapping (not just touching) rotated rectangles."""
        a = _rotated(0, 0, 3, 3, 30)
        b = _rotated(2, 2, 3, 3, 30)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_different_angles(self, strategy: GeneralAdjacency) -> None:
        """Different rotation angles — edges can't be collinear."""
        a = _rotated(5, 5, 3, 1, 20)
        b = _rotated(5, 5, 3, 1, -20)
        assert strategy.check(a, b) == AdjacencyType.NONE

    def test_contained_rotated(self, strategy: GeneralAdjacency) -> None:
        """Small rotated rect inside a larger one — no shared edge."""
        outer = _rotated(5, 5, 4, 4, 30)
        inner = _rotated(5, 5, 1, 1, 30)
        assert strategy.check(outer, inner) == AdjacencyType.NONE

    def test_corner_touching_rotated(self, strategy: GeneralAdjacency) -> None:
        """Two 45° diamonds touching at a single corner (not a shared edge)."""
        # Diamond A centered at origin with tips at ±2√2
        a = _rotated(0, 0, 2, 2, 45)
        # Diamond B centered so its left tip touches A's right tip
        s2 = 2 * math.sqrt(2)
        b = _rotated(2 * s2, 0, 2, 2, 45)
        assert strategy.check(a, b) == AdjacencyType.NONE


# ── Symmetry ─────────────────────────────────────────────────────────


class TestSymmetry:
    """check(a, b) == check(b, a) for rotated cases."""

    @pytest.mark.parametrize(
        ("a", "b"),
        [
            (  # proper
                _aa(0, 0, 3, 4).rotated(30, center=(3.0, 2.0)),
                _aa(3, 0, 6, 4).rotated(30, center=(3.0, 2.0)),
            ),
            (  # sub-line
                _aa(0, 0, 3, 6).rotated(30, center=(3.0, 3.0)),
                _aa(3, 1, 6, 5).rotated(30, center=(3.0, 3.0)),
            ),
            (  # partial
                _aa(0, 0, 3, 4).rotated(30, center=(3.0, 3.0)),
                _aa(3, 2, 6, 6).rotated(30, center=(3.0, 3.0)),
            ),
            (_rotated(0, 0, 2, 1, 30), _rotated(10, 10, 2, 1, 30)),  # none
        ],
        ids=["proper", "subline", "partial", "none"],
    )
    def test_commutative(
        self, strategy: GeneralAdjacency, a: Rectangle, b: Rectangle
    ) -> None:
        """Test swapping a and b."""
        assert strategy.check(a, b) == strategy.check(b, a)
