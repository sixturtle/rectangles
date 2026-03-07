"""Generate example images for the gallery."""

from rectangles import Rectangle, RectangleAnalyzer
from rectangles.rectangle import Point
from rectangles.visualizer import Visualizer

EXAMPLES = [
    {
        "name": "01_intersection_overlap",
        "title": "Overlapping Boxes",
        "a": Rectangle.from_coords(0, 0, 5, 5),
        "b": Rectangle.from_coords(3, 3, 8, 8),
    },
    {
        "name": "02_containment",
        "title": "Containment — Small Inside Big",
        "a": Rectangle.from_coords(0, 0, 10, 10),
        "b": Rectangle.from_coords(2, 2, 5, 5),
    },
    {
        "name": "03_adjacency_proper",
        "title": "Adjacency — Proper (Full Shared Edge)",
        "a": Rectangle.from_coords(0, 0, 3, 4),
        "b": Rectangle.from_coords(3, 0, 6, 4),
    },
    {
        "name": "04_adjacency_subline",
        "title": "Adjacency — Sub-line (Partial Containment)",
        "a": Rectangle.from_coords(0, 0, 3, 6),
        "b": Rectangle.from_coords(3, 1, 6, 5),
    },
    {
        "name": "05_adjacency_partial",
        "title": "Adjacency — Partial Overlap",
        "a": Rectangle.from_coords(0, 0, 3, 4),
        "b": Rectangle.from_coords(3, 2, 6, 6),
    },
    {
        "name": "06_disjoint",
        "title": "Disjoint — No Contact",
        "a": Rectangle.from_coords(0, 0, 3, 3),
        "b": Rectangle.from_coords(6, 0, 9, 3),
    },
    {
        "name": "07_cross_shaped",
        "title": "Cross-shaped Overlap (4 Points)",
        "a": Rectangle.from_coords(0, 2, 6, 4),
        "b": Rectangle.from_coords(2, 0, 4, 6),
    },
    {
        "name": "08_general_rotated",
        "title": "General — Rotated Inside Axis-Aligned",
        "a": Rectangle.from_points(
            Point(x=1, y=0),
            Point(x=3, y=1),
            Point(x=2, y=3),
            Point(x=0, y=2),
        ),
        "b": Rectangle.from_coords(0, 0, 4, 4),
    },
    {
        "name": "09_general_45_diamond",
        "title": "General — 45° Diamond Overlaps Box",
        "a": Rectangle.from_coords(0, 0, 4, 4).rotated(45),
        "b": Rectangle.from_coords(0, 0, 4, 4),
    },
]


def main() -> None:
    """Generate all example images."""
    for ex in EXAMPLES:
        analyzer = RectangleAnalyzer(ex["a"], ex["b"])
        n = len(analyzer.intersection())
        containment = analyzer.containment()
        adjacency = analyzer.adjacency().value

        subtitle = (
            f"Intersection: {n} pt{'s' if n != 1 else ''} | "
            f"Containment: {containment} | "
            f"Adjacency: {adjacency}"
        )
        full_title = f"{ex['title']}\n{subtitle}"

        viz = Visualizer(title=full_title)
        viz.draw_rectangles([ex["a"], ex["b"]], labels=["A", "B"], fill=True)

        path = f"examples/images/{ex['name']}.png"
        viz.save(path)
        print(f"  OK {path}")


if __name__ == "__main__":
    main()
