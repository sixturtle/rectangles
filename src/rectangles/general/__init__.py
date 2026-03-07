"""General rectangle analysis strategies."""

from .adjacency import GeneralAdjacency
from .containment import GeneralContainment
from .intersection import GeneralIntersection

__all__ = ["GeneralIntersection", "GeneralContainment", "GeneralAdjacency"]
