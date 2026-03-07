"""Tests for general rectangle utility functions."""

from __future__ import annotations

import pytest

from rectangles.rectangle import Point
from rectangles.util import Util


def _p(x: float, y: float) -> Point:
    """Shortcut to create a point."""
    return Point(x=x, y=y)


# Unit square with CCW vertices: (0,0) → (1,0) → (1,1) → (0,1)
UNIT_SQUARE = [_p(0, 0), _p(1, 0), _p(1, 1), _p(0, 1)]

# Larger rectangle (0,0)→(4,0)→(4,3)→(0,3)
WIDE_RECT = [_p(0, 0), _p(4, 0), _p(4, 3), _p(0, 3)]


class TestPointInPolygonInside:
    """Points strictly inside the polygon."""

    def test_center_of_unit_square(self) -> None:
        """Center point is inside."""
        assert Util.point_in_polygon(_p(0.5, 0.5), UNIT_SQUARE) is True

    def test_off_center(self) -> None:
        """Arbitrary interior point."""
        assert Util.point_in_polygon(_p(0.2, 0.8), UNIT_SQUARE) is True

    def test_inside_wide_rect(self) -> None:
        """Interior point of a non-square rectangle."""
        assert Util.point_in_polygon(_p(2, 1.5), WIDE_RECT) is True


class TestPointInPolygonBoundary:
    """Points exactly on edges or vertices (should return True)."""

    def test_on_vertex(self) -> None:
        """Point coincides with a vertex."""
        assert Util.point_in_polygon(_p(0, 0), UNIT_SQUARE) is True

    def test_on_bottom_edge(self) -> None:
        """Point on the bottom edge midpoint."""
        assert Util.point_in_polygon(_p(0.5, 0), UNIT_SQUARE) is True

    def test_on_right_edge(self) -> None:
        """Point on the right edge midpoint."""
        assert Util.point_in_polygon(_p(1, 0.5), UNIT_SQUARE) is True

    def test_on_top_edge(self) -> None:
        """Point on the top edge midpoint."""
        assert Util.point_in_polygon(_p(0.5, 1), UNIT_SQUARE) is True

    def test_on_left_edge(self) -> None:
        """Point on the left edge midpoint."""
        assert Util.point_in_polygon(_p(0, 0.5), UNIT_SQUARE) is True


class TestPointInPolygonOutside:
    """Points outside the polygon."""

    def test_right_of_square(self) -> None:
        """Point to the right."""
        assert Util.point_in_polygon(_p(2, 0.5), UNIT_SQUARE) is False

    def test_above_square(self) -> None:
        """Point above."""
        assert Util.point_in_polygon(_p(0.5, 2), UNIT_SQUARE) is False

    def test_below_square(self) -> None:
        """Point below."""
        assert Util.point_in_polygon(_p(0.5, -1), UNIT_SQUARE) is False

    def test_left_of_square(self) -> None:
        """Point to the left."""
        assert Util.point_in_polygon(_p(-1, 0.5), UNIT_SQUARE) is False

    def test_diagonal_outside(self) -> None:
        """Point diagonally outside."""
        assert Util.point_in_polygon(_p(1.5, 1.5), UNIT_SQUARE) is False


class TestPointInPolygonTriangle:
    """Verify with a non-rectangular convex polygon (triangle)."""

    @pytest.fixture()
    def triangle(self) -> list[Point]:
        """CCW triangle: (0,0) → (4,0) → (2,3)."""
        return [_p(0, 0), _p(4, 0), _p(2, 3)]

    def test_inside_triangle(self, triangle: list[Point]) -> None:
        """Centroid is inside."""
        assert Util.point_in_polygon(_p(2, 1), triangle) is True

    def test_outside_triangle(self, triangle: list[Point]) -> None:
        """Point outside the triangle."""
        assert Util.point_in_polygon(_p(0, 3), triangle) is False

    def test_on_triangle_vertex(self, triangle: list[Point]) -> None:
        """Point on a vertex."""
        assert Util.point_in_polygon(_p(2, 3), triangle) is True
