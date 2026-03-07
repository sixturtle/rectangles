"""General utility functions for rectangle analysis.

Shared math primitives used by the general (non-axis-aligned) intersection,
containment, and adjacency strategies.
"""

from __future__ import annotations

from ..rectangle import Point, Segment
from ..strategies import AdjacencyType

EPS = 1e-9
COL_EPS = 1e-7  # wider tolerance for collinearity cross-products


class Util:
    """Shared math primitives for general rectangle analysis."""

    @staticmethod
    def point_in_polygon(p: Point, vertices: list[Point]) -> bool:
        """Check whether a point lies inside or on the boundary of a convex polygon.

        Uses the cross-product same-side test: for every directed edge
        (V_i → V_{i+1}), compute the cross product of the edge vector
        **u** = V_{i+1} − V_i with the point vector **v** = P − V_i.

        If all cross products are ≥ 0 (within tolerance), the point is
        on the left side of every edge and therefore inside the polygon.

        A negative cross product (< −EPS) means P is to the right of
        that edge, i.e. outside.

        Note:
            Requires vertices in counter-clockwise (CCW) order.
            Only valid for convex polygons.

        Args:
            p: The point to test.
            vertices: Polygon vertices in CCW order.

        Returns:
            True if *p* is inside or on the boundary of the polygon.
        """
        n = len(vertices)

        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % n]

            # Edge vector u = P2 - P1, point vector v = P - P1
            u = Point(x=p2.x - p1.x, y=p2.y - p1.y)
            v = Point(x=p.x - p1.x, y=p.y - p1.y)

            # 2D cross product: positive ⇒ left of edge, negative ⇒ right
            uv = (u.x * v.y) - (u.y * v.x)
            if uv < -EPS:
                return False

        return True

    @staticmethod
    def collinear_segments(
        a: Segment, b: Segment
    ) -> tuple[Segment, AdjacencyType] | None:
        """Return shared segment and adjacency type if collinear.

        Returns the overlap if *a* and *b* are collinear and overlap.

        Algorithm (see math_concepts.md § 1, 3, 5):
            1. Express edge A parametrically: P(t) = A.p1 + t·**u**, t ∈ [0, 1].
            2. Check collinearity by verifying B's endpoints have zero
               cross product against **u**.
            3. Project B's endpoints onto A's parametric space via dot
               product to get t₁, t₂.
            4. Compute the overlap of [0, 1] ∩ [t₁, t₂].
            5. Classify the overlap length against both full edges.

        Args:
            a: First segment.
            b: Second segment.

        Returns:
            A ``(shared_segment, adjacency_type)`` tuple if the segments
            are collinear and share a non-degenerate overlap, or ``None``
            if they are not collinear or do not overlap.
        """
        # Edge A direction
        u = Point(x=a.p2.x - a.p1.x, y=a.p2.y - a.p1.y)

        # Offset between start of A and start of B
        v = Point(x=b.p1.x - a.p1.x, y=b.p1.y - a.p1.y)

        # Offset between start of A and end of B
        w = Point(x=b.p2.x - a.p1.x, y=b.p2.y - a.p1.y)

        # Check collinearity: cross product of edge A × (point − A.p1)
        # If both B.p1 and B.p2 lie on the line through A.p1→A.p2, cross ≈ 0
        uv = (u.x * v.y) - (u.y * v.x)
        uw = (u.x * w.y) - (u.y * w.x)
        if abs(uv) > COL_EPS or abs(uw) > COL_EPS:
            return None  # not collinear

        # Dot product of edge A with itself = |edge A|²
        denom = u.x * u.x + u.y * u.y
        if denom < EPS:
            return None  # degenerate (zero-length) edge

        # Parametric t along edge A for each endpoint of edge B
        # t = dot(offset, edge_direction) / |edge|²
        t1 = (v.x * u.x + v.y * u.y) / denom
        t2 = (w.x * u.x + w.y * u.y) / denom
        t_blo, t_bhi = min(t1, t2), max(t1, t2)

        # Overlap of [0, 1] (edge A in t-space) and [t_blo, t_bhi] (edge B)
        t_lo = max(t_blo, 0.0)
        t_hi = min(t_bhi, 1.0)

        if t_hi - t_lo < EPS:
            return None  # no overlap

        # Reconstruct the shared segment from parametric coordinates
        sp1 = Point(x=a.p1.x + t_lo * u.x, y=a.p1.y + t_lo * u.y)
        sp2 = Point(x=a.p1.x + t_hi * u.x, y=a.p1.y + t_hi * u.y)
        shared = Segment(p1=sp1, p2=sp2)

        # Classify: compare overlap [t_lo, t_hi] against both full edges
        a_is_overlap = abs(t_lo) < EPS and abs(t_hi - 1.0) < EPS
        b_is_overlap = abs(t_lo - t_blo) < EPS and abs(t_hi - t_bhi) < EPS

        if a_is_overlap and b_is_overlap:
            return shared, AdjacencyType.PROPER
        elif a_is_overlap or b_is_overlap:
            return shared, AdjacencyType.SUB_LINE
        else:
            return shared, AdjacencyType.PARTIAL

    @staticmethod
    def segments_intersect(a: Segment, b: Segment) -> Point | None:
        """Find the intersection point of two non-collinear segments.

        Algorithm (see math_concepts.md § 1, 4):
            Express both segments parametrically:
                P(t) = A.p1 + t·**u**,  t ∈ [0, 1]
                Q(s) = B.p1 + s·**v**,  s ∈ [0, 1]

            Setting P(t) = Q(s) gives: t·**u** − s·**v** = **w**
            where **u** = A.p2 − A.p1, **v** = B.p2 − B.p1, **w** = B.p1 − A.p1.

            Matrix form (Cramer's Rule):
                | u.x  −v.x |   | t |   | w.x |
                | u.y  −v.y | · | s | = | w.y |

                det = u.x·v.y − u.y·v.x  (2D cross product)
                t = (w.x·v.y − w.y·v.x) / det
                s = (w.x·u.y − w.y·u.x) / det

            If det ≈ 0 the segments are parallel/collinear (use
            ``collinear_segments`` instead). Otherwise, if 0 ≤ t ≤ 1
            and 0 ≤ s ≤ 1, the crossing lies within both segments.

        Args:
            a: First segment.
            b: Second segment.

        Returns:
            The intersection ``Point``, or ``None`` if the segments are
            parallel, collinear, or do not cross within their bounds.
        """
        u = Point(x=a.p2.x - a.p1.x, y=a.p2.y - a.p1.y)
        v = Point(x=b.p2.x - b.p1.x, y=b.p2.y - b.p1.y)
        w = Point(x=b.p1.x - a.p1.x, y=b.p1.y - a.p1.y)

        # 2D cross product u × v
        det = (u.x * v.y) - (u.y * v.x)
        if abs(det) < EPS:
            return None  # parallel or collinear

        # Cramer's rule
        t = (w.x * v.y - w.y * v.x) / det
        s = (w.x * u.y - w.y * u.x) / det

        if -EPS <= t <= 1 + EPS and -EPS <= s <= 1 + EPS:
            px = a.p1.x + t * u.x
            py = a.p1.y + t * u.y
            return Point(x=px, y=py).rounded()

        return None
