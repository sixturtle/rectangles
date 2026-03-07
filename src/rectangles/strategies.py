"""Abstract strategy interfaces for rectangle analysis.

These ABCs define the contract for intersection, containment, and adjacency
analysis. Concrete implementations live in the `axis_aligned` and `general`
subpackages.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from .rectangle import Point, Rectangle


class AdjacencyType(Enum):
    """Classification of how two rectangle sides are shared.

    Attributes:
        PROPER: An entire side of A coincides with an entire side of B.
        SUB_LINE: One full side of one rectangle is contained within a
            side of the other.
        PARTIAL: Sides partially overlap but neither fully contains
            the other.
        NONE: No shared side.
    """

    PROPER = "proper"
    SUB_LINE = "sub-line"
    PARTIAL = "partial"
    NONE = "none"


class StrategyType(Enum):
    """Which family of analysis strategies to use.

    Attributes:
        AUTO: Choose based on rectangle properties.
        AXIS_ALIGNED: Force axis-aligned strategies.
        GENERAL: Force general (rotated) strategies.
    """

    AUTO = "auto"
    AXIS_ALIGNED = "aa"
    GENERAL = "general"


class IntersectionStrategy(ABC):
    """Strategy for finding intersection points between two rectangles."""

    @abstractmethod
    def find_points(self, a: Rectangle, b: Rectangle) -> list[Point]:
        """Find all edge-crossing points between rectangles *a* and *b*.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            Sorted list of intersection points.
        """


class ContainmentStrategy(ABC):
    """Strategy for checking containment between two rectangles."""

    @abstractmethod
    def check(self, a: Rectangle, b: Rectangle) -> str:
        """Describe the containment relationship.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            One of "A contains B", "B contains A", or "No containment".
        """


class AdjacencyStrategy(ABC):
    """Strategy for checking adjacency between two rectangles."""

    @abstractmethod
    def check(self, a: Rectangle, b: Rectangle) -> AdjacencyType:
        """Classify the adjacency between rectangles *a* and *b*.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            The adjacency classification.
        """
