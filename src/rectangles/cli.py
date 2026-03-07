"""CLI for rectangle analysis.

Subcommands:
    analyze   — Run intersection, containment, and adjacency analysis
    visualize — Draw the two rectangles (for manual verification)

Usage:
    rectangles analyze --a x1,y1,x2,y2 --b x1,y1,x2,y2
    rectangles visualize --a x1,y1,x2,y2 --b x1,y1,x2,y2 [--save out.png]
"""

from __future__ import annotations

import argparse
import textwrap

from .rectangle import Point, Rectangle

_EPILOG = textwrap.dedent("""\
    examples:
      # Intersection — two overlapping boxes
      rectangles analyze --a 0,0,5,5 --b 3,3,8,8

      # Containment — small box inside big box
      rectangles analyze --a 0,0,10,10 --b 2,2,5,5

      # Adjacency (proper) — full shared edge
      rectangles analyze --a 0,0,3,4 --b 3,0,6,4

      # Adjacency (sub-line) — partial edge contained
      rectangles analyze --a 0,0,3,6 --b 3,1,6,5

      # Adjacency (partial) — edges partially overlap
      rectangles analyze --a 0,0,3,4 --b 3,2,6,6

      # General rectangle (4 corners, counter-clockwise)
      rectangles analyze --a 1,0,3,1,2,3,0,2 --b 0,0,4,0,4,4,0,4

      # Visualize rectangles (opens matplotlib window)
      rectangles visualize --a 0,0,5,5 --b 3,3,8,8

      # Visualize and save to file
      rectangles visualize --a 0,0,5,5 --b 3,3,8,8 --save output.png
""")


def _parse_rect(value: str) -> Rectangle:
    """Parse 'x1,y1,x2,y2' or 'x1,y1,x2,y2,x3,y3,x4,y4' into a Rectangle.

    Args:
        value: Comma-separated coordinates (4 or 8 values).

    Returns:
        A validated Rectangle.

    Raises:
        argparse.ArgumentTypeError: If format is invalid.
    """
    parts = value.split(",")
    try:
        coords = [float(p.strip()) for p in parts]
    except ValueError as e:
        msg = f"Non-numeric coordinate in: {value}"
        raise argparse.ArgumentTypeError(msg) from e

    if len(coords) == 4:
        x1, y1, x2, y2 = coords
        try:
            return Rectangle.from_coords(x1, y1, x2, y2)
        except Exception as e:
            msg = f"Invalid rectangle {value}: {e}"
            raise argparse.ArgumentTypeError(msg) from e
    elif len(coords) == 8:
        points = [Point(x=coords[i], y=coords[i + 1]) for i in range(0, 8, 2)]
        return Rectangle.from_points(*points)
    else:
        msg = (
            f"Expected 4 coords (axis-aligned) or "
            f"8 coords (general), got {len(coords)}: {value}"
        )
        raise argparse.ArgumentTypeError(msg)


def _add_rect_args(parser: argparse.ArgumentParser) -> None:
    """Add --a and --b rectangle arguments to a parser."""
    parser.add_argument(
        "--a",
        required=True,
        type=_parse_rect,
        metavar="COORDS",
        help=(
            "First rectangle. 4 values (x1,y1,x2,y2) for "
            "axis-aligned, or 8 values "
            "(x1,y1,x2,y2,x3,y3,x4,y4) for general."
        ),
    )
    parser.add_argument(
        "--b",
        required=True,
        type=_parse_rect,
        metavar="COORDS",
        help="Second rectangle (same format as --a).",
    )


def _cmd_analyze(args: argparse.Namespace) -> None:
    """Run intersection, containment, and adjacency analysis."""
    from .analyzer import RectangleAnalyzer
    from .strategies import StrategyType

    strategy = StrategyType(getattr(args, "strategy", "auto"))
    analyzer = RectangleAnalyzer(args.a, args.b, strategy=strategy)

    intersection = analyzer.intersection()
    containment = analyzer.containment()
    adjacency = analyzer.adjacency().value

    print(f"Intersection:  {intersection}")
    print(f"Containment:   {containment}")
    print(f"Adjacency:     {adjacency}")

    if getattr(args, "show", False):
        from .visualizer import Visualizer

        n = len(intersection)
        title = (
            f"Intersection: {n} pt{'s' if n != 1 else ''} | "
            f"Containment: {containment} | "
            f"Adjacency: {adjacency}"
        )
        viz = Visualizer(title=title)
        viz.draw_rectangles([args.a, args.b], labels=["A", "B"], fill=True)
        viz.show()


def _cmd_visualize(args: argparse.Namespace) -> None:
    """Draw the two rectangles using matplotlib."""
    from .visualizer import Visualizer

    viz = Visualizer(title="Rectangle Visualization")
    viz.draw_rectangles([args.a, args.b], labels=["A", "B"], fill=True)

    if args.save:
        viz.save(args.save)
    else:
        viz.show()


def main() -> None:
    """CLI entry point for rectangle analysis."""
    parser = argparse.ArgumentParser(
        prog="rectangles",
        description="Analyze and visualize relationships between two rectangles.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    # ── analyze ──────────────────────────────────────────────────────
    analyze_p = subparsers.add_parser(
        "analyze",
        help="Run intersection, containment, and adjacency analysis.",
    )
    _add_rect_args(analyze_p)
    analyze_p.add_argument(
        "--strategy",
        choices=["auto", "aa", "general"],
        default="auto",
        help="Strategy: auto (default), aa (axis-aligned), general.",
    )
    analyze_p.add_argument(
        "--show",
        action="store_true",
        default=False,
        help="Open a matplotlib visualization after analysis.",
    )

    # ── visualize ────────────────────────────────────────────────────
    visualize_p = subparsers.add_parser(
        "visualize",
        help="Draw the two rectangles (for manual verification).",
    )
    _add_rect_args(visualize_p)
    visualize_p.add_argument(
        "--save",
        metavar="FILE",
        default=None,
        help="Save the plot to a file instead of displaying it.",
    )

    args = parser.parse_args()

    if args.command == "analyze":
        _cmd_analyze(args)
    elif args.command == "visualize":
        _cmd_visualize(args)
    else:
        parser.print_help()
