"""Tests for rectangle input validation (is_rectangle, is_ccw, from_points)."""

from __future__ import annotations

import math

import pytest

from rectangles.rectangle import Point, Rectangle


def _p(x: float, y: float) -> Point:
    """Shortcut to create a point."""
    return Point(x=x, y=y)


# -- Valid rectangles (CCW order) ------------------------------------------

UNIT_SQUARE = [_p(0, 0), _p(1, 0), _p(1, 1), _p(0, 1)]
WIDE_RECT = [_p(0, 0), _p(4, 0), _p(4, 3), _p(0, 3)]

# 45-degree rotated unit square (center at origin)
_s = math.sqrt(2) / 2
ROTATED_SQUARE = [_p(0, -_s), _p(_s, 0), _p(0, _s), _p(-_s, 0)]


class TestIsRectangle:
    """Rectangle.is_rectangle validation."""

    def test_unit_square(self) -> None:
        """Unit square is a valid rectangle."""
        assert Rectangle.is_rectangle(UNIT_SQUARE) is True

    def test_wide_rectangle(self) -> None:
        """Non-square axis-aligned rectangle is valid."""
        assert Rectangle.is_rectangle(WIDE_RECT) is True

    def test_rotated_square(self) -> None:
        """45-degree rotated square is a valid rectangle."""
        assert Rectangle.is_rectangle(ROTATED_SQUARE) is True

    def test_parallelogram_not_rectangle(self) -> None:
        """A parallelogram that is NOT a rectangle (unequal diagonals)."""
        pts = [_p(0, 0), _p(2, 0), _p(3, 1), _p(1, 1)]
        assert Rectangle.is_rectangle(pts) is False

    def test_arbitrary_quadrilateral(self) -> None:
        """Four random points — not a rectangle."""
        pts = [_p(0, 0), _p(3, 0), _p(4, 2), _p(0, 3)]
        assert Rectangle.is_rectangle(pts) is False

    def test_three_points_rejected(self) -> None:
        """Only three points — not enough for a rectangle."""
        assert Rectangle.is_rectangle([_p(0, 0), _p(1, 0), _p(1, 1)]) is False

    def test_five_points_rejected(self) -> None:
        """Five points — too many."""
        pts = [_p(0, 0), _p(1, 0), _p(1, 1), _p(0, 1), _p(0.5, 0.5)]
        assert Rectangle.is_rectangle(pts) is False

    def test_degenerate_line_segment(self) -> None:
        """Four collinear points — not a rectangle."""
        pts = [_p(0, 0), _p(1, 0), _p(2, 0), _p(3, 0)]
        assert Rectangle.is_rectangle(pts) is False


class TestIsCCW:
    """Rectangle.is_ccw winding-order check."""

    def test_ccw_unit_square(self) -> None:
        """Standard CCW unit square is detected."""
        assert Rectangle.is_ccw(UNIT_SQUARE) is True

    def test_cw_unit_square(self) -> None:
        """Reversed (clockwise) order → not CCW."""
        assert Rectangle.is_ccw(list(reversed(UNIT_SQUARE))) is False

    def test_ccw_rotated_square(self) -> None:
        """Rotated square in CCW order is detected."""
        assert Rectangle.is_ccw(ROTATED_SQUARE) is True


class TestFromCoordsValidation:
    """Rectangle.from_coords should reject degenerate inputs."""

    def test_valid_rectangle_accepted(self) -> None:
        """Standard axis-aligned rectangle is accepted."""
        r = Rectangle.from_coords(0, 0, 3, 4)
        assert r.p1 == _p(0, 0)
        assert r.p3 == _p(3, 4)

    def test_single_point_raises(self) -> None:
        """All four coords equal (zero-area point) → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle coordinates"):
            Rectangle.from_coords(1, 1, 1, 1)

    def test_zero_width_raises(self) -> None:
        """x1 == x2 (zero-width line) → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle coordinates"):
            Rectangle.from_coords(2, 0, 2, 5)

    def test_zero_height_raises(self) -> None:
        """y1 == y2 (zero-height line) → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle coordinates"):
            Rectangle.from_coords(0, 3, 5, 3)

    def test_swapped_x_raises(self) -> None:
        """x1 > x2 → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle coordinates"):
            Rectangle.from_coords(5, 0, 2, 4)

    def test_swapped_y_raises(self) -> None:
        """y1 > y2 → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle coordinates"):
            Rectangle.from_coords(0, 5, 3, 2)

    def test_negative_coords_accepted(self) -> None:
        """Negative coordinates are fine if x1 < x2 and y1 < y2."""
        r = Rectangle.from_coords(-3, -4, -1, -1)
        assert r.p1 == _p(-3, -4)


class TestFromPointsValidation:
    """Rectangle.from_points should reject invalid inputs."""

    def test_valid_rectangle_accepted(self) -> None:
        """Valid CCW rectangle is accepted."""
        r = Rectangle.from_points(_p(0, 0), _p(1, 0), _p(1, 1), _p(0, 1))
        assert r.p1 == _p(0, 0)

    def test_non_rectangle_raises(self) -> None:
        """Parallelogram → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle points"):
            Rectangle.from_points(_p(0, 0), _p(2, 0), _p(3, 1), _p(1, 1))

    def test_clockwise_order_raises(self) -> None:
        """Valid rectangle but CW winding → ValueError."""
        with pytest.raises(ValueError, match="not in counter-clockwise order"):
            Rectangle.from_points(_p(0, 1), _p(1, 1), _p(1, 0), _p(0, 0))

    def test_rotated_rectangle_accepted(self) -> None:
        """Non-axis-aligned rectangle in CCW order is accepted."""
        r = Rectangle.from_points(
            ROTATED_SQUARE[0],
            ROTATED_SQUARE[1],
            ROTATED_SQUARE[2],
            ROTATED_SQUARE[3],
        )
        assert r.p1 == ROTATED_SQUARE[0]

    def test_collapsed_single_point_raises(self) -> None:
        """All four points identical (degenerate point) → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle points"):
            Rectangle.from_points(_p(1, 1), _p(1, 1), _p(1, 1), _p(1, 1))

    def test_collinear_points_raises(self) -> None:
        """Four collinear points (degenerate line) → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle points"):
            Rectangle.from_points(_p(0, 0), _p(1, 0), _p(2, 0), _p(3, 0))

    def test_duplicate_adjacent_vertices_raises(self) -> None:
        """Two adjacent vertices coincide → ValueError."""
        with pytest.raises(ValueError, match="Invalid rectangle points"):
            Rectangle.from_points(_p(0, 0), _p(0, 0), _p(1, 1), _p(0, 1))
