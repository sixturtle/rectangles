"""Rectangles package."""

from .analyzer import RectangleAnalyzer
from .rectangle import Point, Rectangle, Segment
from .strategies import (
    AdjacencyStrategy,
    AdjacencyType,
    ContainmentStrategy,
    IntersectionStrategy,
    StrategyType,
)

__all__ = [
    "AdjacencyStrategy",
    "AdjacencyType",
    "ContainmentStrategy",
    "IntersectionStrategy",
    "Point",
    "Rectangle",
    "RectangleAnalyzer",
    "Segment",
    "StrategyType",
]
