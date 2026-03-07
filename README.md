# Rectangles

Analyze spatial relationships between two rectangles: **intersection**, **containment**, and **adjacency**.

Supports both **axis-aligned** (4 coordinates) and **general** rectangles (4 corner points).

## Requirements

- Python ≥ 3.14
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

```bash
git clone git@github.com:sixturtle/rectangles.git && cd rectangles
uv sync
```

## Usage

### CLI

Two subcommands are available:
- **`analyze`** — Run intersection, containment, and adjacency analysis
- **`visualize`** — Draw the two rectangles for manual verification

Rectangles can be specified in two formats:
- **Axis-aligned:** `x1,y1,x2,y2` (bottom-left and top-right)
- **General:** `x1,y1,x2,y2,x3,y3,x4,y4` (four corners, counter-clockwise)

```bash
# Basic analysis
uv run rectangles analyze --a 0,0,5,5 --b 3,3,8,8

# Force a specific strategy (auto, aa, or general)
uv run rectangles analyze --a 0,0,5,5 --b 3,3,8,8 --strategy general

# Analyze and open a visualization with results in the title
uv run rectangles analyze --a 0,0,5,5 --b 3,3,8,8 --show

# Draw rectangles only (no analysis)
uv run rectangles visualize --a 0,0,5,5 --b 3,3,8,8

# Save visualization to a file
uv run rectangles visualize --a 0,0,5,5 --b 3,3,8,8 --save output.png
```

Run `uv run rectangles --help` to see all curated examples.

### Python API

```python
from rectangles import Rectangle, RectangleAnalyzer, StrategyType

# Auto-detect strategy (uses axis-aligned for AA rects)
a = Rectangle.from_coords(0, 0, 5, 5)
b = Rectangle.from_coords(3, 3, 8, 8)
analyzer = RectangleAnalyzer(a, b)

analyzer.intersection()  # [(3, 3), (3, 5), (5, 3), (5, 5)]
analyzer.containment()   # "No containment"
analyzer.adjacency()     # AdjacencyType.NONE

# Force a specific strategy
analyzer = RectangleAnalyzer(a, b, strategy=StrategyType.GENERAL)

# General rectangles (specify 4 corners directly)
from rectangles import Point
a = Rectangle.from_points(
    Point(x=1, y=0), Point(x=3, y=1),
    Point(x=2, y=3), Point(x=0, y=2),
)
```

### Using strategies directly

```python
from rectangles.axis_aligned import AAIntersection, AAContainment, AAAdjacency

AAIntersection().find_points(a, b)
AAContainment().check(a, b)
AAAdjacency().check(a, b)
```

## Curated Examples

Ready-to-paste commands with expected output:

### Intersection — overlapping boxes

```bash
uv run rectangles analyze --a 0,0,5,5 --b 3,3,8,8
```
```
Intersection:  [(3.0, 3.0), (3.0, 5.0), (5.0, 3.0), (5.0, 5.0)]
Containment:   No containment
Adjacency:     none
```

### Containment — small box inside big box

```bash
uv run rectangles analyze --a 0,0,10,10 --b 2,2,5,5
```
```
Intersection:  [(2.0, 2.0), (2.0, 5.0), (5.0, 2.0), (5.0, 5.0)]
Containment:   A contains B
Adjacency:     none
```

### Adjacency — proper (full shared edge)

```bash
uv run rectangles analyze --a 0,0,3,4 --b 3,0,6,4
```
```
Intersection:  []
Containment:   No containment
Adjacency:     proper
```

### Adjacency — sub-line (one edge inside the other)

```bash
uv run rectangles analyze --a 0,0,3,6 --b 3,1,6,5
```
```
Intersection:  []
Containment:   No containment
Adjacency:     sub-line
```

### Adjacency — partial (edges partially overlap)

```bash
uv run rectangles analyze --a 0,0,3,4 --b 3,2,6,6
```
```
Intersection:  []
Containment:   No containment
Adjacency:     partial
```

### General rectangle — 8-coordinate input

```bash
uv run rectangles analyze --a 1,0,3,1,2,3,0,2 --b 0,0,4,0,4,4,0,4
```
```
Intersection:  [(0.0, 2.0), (1.0, 0.0), (2.0, 3.0), (3.0, 1.0)]
Containment:   B contains A
Adjacency:     none
```

### Visualize — draw rectangles

```bash
# Open a matplotlib window
uv run rectangles visualize --a 0,0,5,5 --b 3,3,8,8

# Save to a file
uv run rectangles visualize --a 0,0,5,5 --b 3,3,8,8 --save output.png

# Analyze + show visualization with summary in title
uv run rectangles analyze --a 0,0,5,5 --b 3,3,8,8 --show
```

## Testing

```bash
uv run pytest tests/ -v      # Run all tests
uv run mypy src/             # Type-check
uv run ruff check src/       # Lint
```

## Project Structure

```
src/rectangles/
├── rectangle.py          # Point, Segment, Rectangle models
├── strategies.py         # AdjacencyType, StrategyType enums + abstract strategy ABCs
├── analyzer.py           # RectangleAnalyzer facade
├── axis_aligned/         # Axis-aligned implementations
│   ├── intersection.py   # Coordinate overlap
│   ├── containment.py    # Interval comparison
│   └── adjacency.py      # Side coordinate + overlap
├── general/              # General rectangle implementations
│   ├── intersection.py   # Point-in-polygon + edge crossing
│   ├── containment.py    # Point-in-polygon containment
│   └── adjacency.py      # Collinear edge-segment overlap
├── util/                 # Shared math primitives
│   └── util.py           # Cross product, Cramer's rule, etc.
├── visualizer.py         # Matplotlib drawing
└── cli.py                # CLI entry point (analyze / visualize)
```

## Documentation

- [Design](docs/DESIGN.md) — architecture, strategy pattern, test case summary
- [Problem Description](docs/problem_description.md) — original requirements
- [Math Concepts](docs/math_concepts.md) — algorithms and formulas used
