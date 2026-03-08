# Math Concepts

Six core math concepts are used to solve intersection, containment, adjacency, and input validation problems for axis-aligned and general rectangles.


## 1. Parametric Line

Any point on a line segment can be represented as a parametric function of the endpoints. Mathematically:

$$
P(t) = P_1 + t(P_2 - P_1)
$$

Where $P(t)$ is the point on the line segment, $P_1$ and $P_2$ are the endpoints, and $t$ is a parameter that ranges from $0$ to $1$.

| $t$ value | Position |
|-----------|----------|
| $t < 0$   | Before $P_1$ |
| $t = 0$   | $P_1$ |
| $t = 0.5$ | Midpoint |
| $t = 1$   | $P_2$ |
| $t > 1$   | After $P_2$ |

```
t=0     t=0.5     t=1
P1--------.--------P2
```


## 2. 2D Cross Product

The 2D cross product of two vectors is a scalar value equal to the signed area of the parallelogram spanned by the two vectors.

Given two vectors $\vec{u} = (u_x, u_y)$ and $\vec{v} = (v_x, v_y)$, the cross product is defined as:

$$
\vec{u} \times \vec{v} = \begin{vmatrix}
u_x & u_y \\
v_x & v_y
\end{vmatrix} = u_x v_y - u_y v_x
$$

| Value    | Orientation |
|----------|-------------|
| $> 0$    | Counterclockwise (left turn) — $\vec{v}$ is to the left of $\vec{u}$ |
| $< 0$    | Clockwise (right turn) — $\vec{v}$ is to the right of $\vec{u}$ |
| $= 0$    | Collinear — $\vec{v}$ is parallel to $\vec{u}$ |

**Usage**
- **Orientation test**: Determine which side of a directed line a point lies on.
- **Segment intersection**: Detect whether two segments straddle each other by checking if their endpoints have opposite orientations relative to the other segment.
- **Collinearity check**: If $\vec{u} \times \vec{v} = 0$, the points are collinear.


## 3. Dot Product Projection

Given a point $P$ and a line segment $P_1 \to P_2$, the parametric position $t$ of $P$'s projection onto the line is:

$$
t = \frac{(P - P_1) \cdot (P_2 - P_1)}{|P_2 - P_1|^2}
$$

Let:

$$
\vec{u} = P_2 - P_1 = (P_{2x} - P_{1x},\; P_{2y} - P_{1y}) \quad \text{(edge direction)}
$$

$$
\vec{v} = P - P_1 = (P_x - P_{1x},\; P_y - P_{1y}) \quad \text{(offset to point)}
$$

Then:

$$
t = \frac{\vec{v} \cdot \vec{u}}{\vec{u} \cdot \vec{u}} = \frac{v_x \cdot u_x + v_y \cdot u_y}{u_x^2 + u_y^2}
$$

**Usage**
- Project a point onto a line segment to find the closest point or parametric position.
- Used in collinear overlap detection to find where one segment's endpoints fall on another segment's parametric space.


## 4. Cramer's Rule (2×2 System)

When two non-parallel line segments $P_1 P_2$ and $P_3 P_4$ may cross, we solve for $t$ and $u$ simultaneously.

**System of equations:**

$$
P(t) = P_1 + t(P_2 - P_1), \quad t \in [0, 1]
$$

$$
Q(u) = P_3 + u(P_4 - P_3), \quad u \in [0, 1]
$$

Setting $P(t) = Q(u)$:

$$
P_1 + t(P_2 - P_1) = P_3 + u(P_4 - P_3)
$$

Rearranging:

$$
t \cdot \vec{a} - u \cdot \vec{b} = \vec{c}
$$

Where:
- $\vec{a} = P_2 - P_1$ (direction of segment A)
- $\vec{b} = P_4 - P_3$ (direction of segment B)
- $\vec{c} = P_3 - P_1$ (offset between segment origins)

Expanding into $x$ and $y$ components:

$$
t \cdot a_x - u \cdot b_x = c_x
$$

$$
t \cdot a_y - u \cdot b_y = c_y
$$

**Matrix form** $A\mathbf{x} = \mathbf{c}$:

$$
\begin{bmatrix}
a_x & -b_x \\
a_y & -b_y
\end{bmatrix}
\begin{bmatrix}
t \\
u
\end{bmatrix}
=
\begin{bmatrix}
c_x \\
c_y
\end{bmatrix}
$$

**Determinant:**

$$
\det(A) = a_x \cdot (-b_y) - (-b_x) \cdot a_y = -a_x b_y + a_y b_x
$$

**Solving via Cramer's Rule:**

$$
t = \frac{(-b_y) \cdot c_x - (-b_x) \cdot c_y}{\det(A)} = \frac{-b_y \cdot c_x + b_x \cdot c_y}{\det(A)}
$$

$$
u = \frac{a_x \cdot c_y - a_y \cdot c_x}{\det(A)}
$$

| Condition | Meaning |
|-----------|---------|
| $\det(A) = 0$ | Lines are parallel (or collinear) |
| $0 \le t \le 1$ and $0 \le u \le 1$ | Crossing is within both segments |
| $t$ or $u$ outside $[0,1]$ | Lines cross but segments don't reach |

**Usage**
- Segment intersection point detection for general (non-axis-aligned) rectangles.


## 5. 1D Interval Overlap

Given two intervals $[a_1, a_2]$ and $[b_1, b_2]$, their overlap is:

$$
\text{left} = \max(a_1, b_1)
$$

$$
\text{right} = \min(a_2, b_2)
$$

$$
\text{overlap exists} \iff \text{left} < \text{right}
$$

**Usage**
- **Axis-aligned rectangle intersection**: Check overlap of $[a_{x1}, a_{x2}]$ and $[b_{x1}, b_{x2}]$ on each axis.
- **Collinear edge overlap**: Overlap of $[0, 1]$ (edge A in $t$-space) and $[t_1, t_2]$ (edge B projected onto A).
- **Adjacency**: Comparing overlap interval against full edge intervals to classify as proper, sub-line, or partial.


## 6. Shoelace Formula (Signed Area)

The signed area of a simple polygon with vertices $(x_1, y_1), (x_2, y_2), \ldots, (x_n, y_n)$ is:

$$
A = \frac{1}{2} \sum_{i=1}^{n} (x_i \cdot y_{i+1} - x_{i+1} \cdot y_i)
$$

where indices wrap around, i.e. $(x_{n+1}, y_{n+1}) = (x_1, y_1)$.

| Sign of $A$ | Winding Order |
|-------------|---------------|
| $A > 0$     | Counter-clockwise (CCW) |
| $A < 0$     | Clockwise (CW) |
| $A = 0$     | Degenerate (collinear points) |

The absolute value $|A|$ gives the true area of the polygon.

**Usage**
- **Winding-order check**: Use `signed_area > 0` to verify that input points are in counter-clockwise order.
- **Rectangle validation**: A degenerate area ($A = 0$) indicates collinear points, which cannot form a valid rectangle.


## Axis-Aligned vs. Rotated: Which concepts are needed?

| Concept | Axis-Aligned | Rotated | Validation |
|---------|:------------:|:-------:|:----------:|
| 1. Parametric Line | — | ✓ | — |
| 2. 2D Cross Product | — | ✓ | — |
| 3. Dot Product Projection | — | ✓ | — |
| 4. Cramer's Rule | — | ✓ | — |
| 5. 1D Interval Overlap | ✓ | ✓ | — |
| 6. Shoelace Formula | — | — | ✓ |

Axis-aligned rectangles need only **Concept 5**. Rotated rectangles require **Concepts 1–5**. Input validation uses **Concept 6** for winding-order checks.


## Dot product vs. Cross Product of two vectors

* **Dot Product**: Measuring how much two vectors align. or How far along is a point P on line A when you project P onto A.
* **Cross Product**: Measuring orthogonality. 0 means same direction (parallel)