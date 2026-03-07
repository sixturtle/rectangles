"""Axis-aligned rectangle analysis strategies."""

from .adjacency import AAAdjacency
from .containment import AAContainment
from .intersection import AAIntersection

__all__ = ["AAIntersection", "AAContainment", "AAAdjacency"]
