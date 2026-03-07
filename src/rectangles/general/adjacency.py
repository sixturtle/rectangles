"""Adjacency analysis for general (possibly rotated) rectangles.

Determines whether two rectangles share a collinear edge segment and
classifies the adjacency sub-type (proper, sub-line, or partial).

Algorithm:
    For every pair of edges (one from each rectangle), test whether the
    two segments are collinear and overlapping using parametric projection.
    The first collinear overlap found determines the adjacency type.
    See math_concepts.md § 1, 3, 5 for the underlying math.
"""

from __future__ import annotations

from ..rectangle import Rectangle
from ..strategies import AdjacencyStrategy, AdjacencyType
from ..util import Util


class GeneralAdjacency(AdjacencyStrategy):
    """General adjacency using collinear edge-segment overlap."""

    def check(self, a: Rectangle, b: Rectangle) -> AdjacencyType:
        """Classify adjacency between two general rectangles.

        Iterates over all pairs of edges (one from *a*, one from *b*)
        and returns the adjacency type of the first collinear overlap
        found.  If no edges are collinear and overlapping, returns
        ``AdjacencyType.NONE``.

        Args:
            a: First rectangle.
            b: Second rectangle.

        Returns:
            The adjacency classification.
        """
        for seg_a in a.segments:
            for seg_b in b.segments:
                result = Util.collinear_segments(seg_a, seg_b)
                if result is not None:
                    return result[1]
        return AdjacencyType.NONE
