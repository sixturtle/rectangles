"""Matplotlib-based rectangle visualizer."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .rectangle import Rectangle

# Color palette for drawing multiple rectangles
COLORS: list[str] = [
    "#4A90D9",  # blue
    "#E74C3C",  # red
    "#2ECC71",  # green
    "#F39C12",  # orange
    "#9B59B6",  # purple
    "#1ABC9C",  # teal
    "#E67E22",  # dark orange
    "#3498DB",  # light blue
]


class Visualizer:
    """Draws rectangles and analysis results on a matplotlib figure."""

    fig: Figure
    ax: Axes

    def __init__(self, title: str = "Rectangle Analysis") -> None:
        """Initialize a new visualizer with a titled figure."""
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 8))
        self.ax.set_title(title, fontsize=14, fontweight="bold")
        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3, linestyle="--")
        self._color_index: int = 0

    def _next_color(self) -> str:
        color: str = COLORS[self._color_index % len(COLORS)]
        self._color_index += 1
        return color

    def draw_rectangle(
        self,
        rect: Rectangle,
        color: str | None = None,
        label: str | None = None,
        linewidth: float = 2.0,
        fill: bool = False,
        alpha: float = 0.15,
    ) -> None:
        """Draw a single rectangle on the plot.

        Args:
            rect: The rectangle to draw.
            color: Edge color. Auto-assigned if None.
            label: Optional label displayed at the rectangle's center.
            linewidth: Width of the rectangle border.
            fill: Whether to fill the rectangle with a translucent color.
            alpha: Fill opacity (only used when fill=True).
        """
        if color is None:
            color = self._next_color()

        patch: patches.Patch

        # Draw as a closed polygon.
        patch = patches.Polygon(
            [
                (rect.p1.x, rect.p1.y),
                (rect.p2.x, rect.p2.y),
                (rect.p3.x, rect.p3.y),
                (rect.p4.x, rect.p4.y),
            ],
            closed=True,
            linewidth=linewidth,
            edgecolor=color,
            facecolor=color if fill else "none",
            alpha=alpha if fill else 1.0,
            label=label,
        )

        self.ax.add_patch(patch)

        # Draw label at center
        if label:
            cx, cy = (rect.p1.x + rect.p3.x) / 2, (rect.p1.y + rect.p3.y) / 2
            self.ax.text(
                cx,
                cy,
                label,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=color,
            )

    def draw_rectangles(
        self,
        rects: Sequence[Rectangle],
        labels: Sequence[str] | None = None,
        fill: bool = False,
    ) -> None:
        """Draw multiple rectangles, auto-assigning colors and labels.

        Args:
            rects: Sequence of rectangles to draw.
            labels: Optional labels, one per rectangle. Defaults to "A", "B", "C", ...
            fill: Whether to fill rectangles.
        """
        if labels is None:
            labels = [chr(ord("A") + i) for i in range(len(rects))]

        for rect, lbl in zip(rects, labels):
            self.draw_rectangle(rect, label=lbl, fill=fill)

    def auto_fit(self, padding: float = 1.0) -> None:
        """Auto-scale axes to fit all drawn content with padding."""
        self.ax.autoscale_view()
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0] - padding, xlim[1] + padding)
        self.ax.set_ylim(ylim[0] - padding, ylim[1] + padding)

    def show(self) -> None:
        """Display the plot."""
        self.ax.legend(loc="upper right")
        self.auto_fit()
        plt.tight_layout()
        plt.show()

    def save(self, path: str, dpi: int = 150) -> None:
        """Save the plot to a file."""
        self.ax.legend(loc="upper right")
        self.auto_fit()
        plt.tight_layout()
        self.fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved to {path}")
