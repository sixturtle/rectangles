"""Rectangle, Point, and Segment models."""

from __future__ import annotations

import math

from pydantic import BaseModel, Field

EPS = 1e-9


class Point(BaseModel):
    """Point in 2D space."""

    x: float = Field(..., description="X-coordinate of the point")
    y: float = Field(..., description="Y-coordinate of the point")

    def __repr__(self) -> str:
        """Return a string representation of the point."""
        return f"({self.x}, {self.y})"

    def __str__(self) -> str:
        """Return a string representation of the point."""
        return f"({self.x}, {self.y})"

    def __hash__(self) -> int:
        """Hash based on coordinates so Point can be used in sets."""
        return hash((self.x, self.y))

    def __lt__(self, other: object) -> bool:
        """Lexicographic ordering (x, then y) so Points can be sorted."""
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) < (other.x, other.y)

    def rounded(self, ndigits: int = 9) -> Point:
        """Return a new Point with coordinates rounded to *ndigits* decimals."""
        return Point(x=round(self.x, ndigits), y=round(self.y, ndigits))

    def distance_to(self, other: Point) -> float:
        """Return the Euclidean distance to *other*."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Segment(BaseModel):
    """Segment in 2D space."""

    p1: Point = Field(..., description="Start point of the segment")
    p2: Point = Field(..., description="End point of the segment")


class Rectangle(BaseModel):
    """Rectangle defined by its four corner points."""

    p1: Point = Field(..., description="Point 1 of the rectangle")
    p2: Point = Field(..., description="Point 2 of the rectangle")
    p3: Point = Field(..., description="Point 3 of the rectangle")
    p4: Point = Field(..., description="Point 4 of the rectangle")

    @classmethod
    def from_coords(cls, x1: float, y1: float, x2: float, y2: float) -> Rectangle:
        """Create an axis-aligned rectangle from bottom-left and top-right coords."""
        if x1 >= x2 or y1 >= y2:
            raise ValueError("Invalid rectangle coordinates.")
        return cls(
            p1=Point(x=x1, y=y1),
            p2=Point(x=x2, y=y1),
            p3=Point(x=x2, y=y2),
            p4=Point(x=x1, y=y2),
        )

    @classmethod
    def from_points(cls, p1: Point, p2: Point, p3: Point, p4: Point) -> Rectangle:
        """Create a general rectangle from four corner points."""
        if not cls.is_rectangle([p1, p2, p3, p4]):
            raise ValueError("Invalid rectangle points.")
        if not cls.is_ccw([p1, p2, p3, p4]):
            raise ValueError("Rectangle points are not in counter-clockwise order.")
        return cls(p1=p1, p2=p2, p3=p3, p4=p4)

    @property
    def is_axis_aligned(self) -> bool:
        """True if every edge is horizontal or vertical."""
        for seg in self.segments:
            dx = abs(seg.p1.x - seg.p2.x)
            dy = abs(seg.p1.y - seg.p2.y)
            if dx > EPS and dy > EPS:
                return False
        return True

    @staticmethod
    def signed_area(vertices: list[Point]) -> float:
        """Compute the signed area of a polygon (shoelace formula)."""
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i].x * vertices[j].y
            area -= vertices[j].x * vertices[i].y
        return area / 2.0

    @staticmethod
    def is_ccw(vertices: list[Point]) -> bool:
        """Check if polygon vertices are in counter-clockwise order."""
        return Rectangle.signed_area(vertices) > 0

    @staticmethod
    def is_rectangle(vertices: list[Point]) -> bool:
        """Check if four vertices form a rectangle.

        Uses equal-length bisecting diagonals.
        """
        if len(vertices) != 4:
            return False

        p1, p2, p3, p4 = vertices

        # Diagonals must bisect each other
        mid1 = Point(x=(p1.x + p3.x) / 2, y=(p1.y + p3.y) / 2)
        mid2 = Point(x=(p2.x + p4.x) / 2, y=(p2.y + p4.y) / 2)
        if abs(mid1.x - mid2.x) > EPS or abs(mid1.y - mid2.y) > EPS:
            return False

        # Diagonals must be non-zero and equal length
        d1 = p1.distance_to(p3)
        d2 = p2.distance_to(p4)
        if d1 < EPS or d2 < EPS:
            return False
        if abs(d1 - d2) > EPS:
            return False

        return True

    def rotated(
        self,
        angle: float,
        center: tuple[float, float] | None = None,
    ) -> Rectangle:
        """Return a NEW rectangle rotated by *angle* degrees.

        Args:
            angle: Rotation angle in degrees (counter-clockwise).
            center: Optional (cx, cy) to rotate around. Defaults to
                the rectangle's own center.
        """
        if center is not None:
            cx, cy = center
        else:
            cx = (self.p1.x + self.p3.x) / 2
            cy = (self.p1.y + self.p3.y) / 2
        theta = math.radians(angle % 360)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        corners = [
            Point(
                x=cx + (p.x - cx) * cos_t - (p.y - cy) * sin_t,
                y=cy + (p.x - cx) * sin_t + (p.y - cy) * cos_t,
            ).rounded()
            for p in [self.p1, self.p2, self.p3, self.p4]
        ]
        return Rectangle(
            p1=corners[0],
            p2=corners[1],
            p3=corners[2],
            p4=corners[3],
        )

    @property
    def segments(self) -> list[Segment]:
        """Return the four segments of the rectangle."""
        return [
            Segment(p1=self.p1, p2=self.p2),
            Segment(p1=self.p2, p2=self.p3),
            Segment(p1=self.p3, p2=self.p4),
            Segment(p1=self.p4, p2=self.p1),
        ]

    def __repr__(self) -> str:
        """Return a string representation of the rectangle."""
        return f"""Rectangle[
        {self.p1}, {self.p2}, {self.p3}, {self.p4}]"""

    def __str__(self) -> str:
        """Return a string representation of the rectangle."""
        return f"""Rectangle[
        {self.p1}, {self.p2}, {self.p3}, {self.p4}]"""
