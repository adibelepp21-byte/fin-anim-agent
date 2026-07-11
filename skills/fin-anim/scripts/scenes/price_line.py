"""Animated line chart for a single price/metric series over time."""
from manim import (
    DOWN,
    GREEN,
    GREY,
    RED,
    RIGHT,
    UP,
    Axes,
    Create,
    Dot,
    FadeIn,
    Line,
    Scene,
    Text,
    Write,
)

from schema import SceneData


class PriceLineScene(Scene):
    """Renders a left-to-right animated draw of a price series with a % delta badge.

    `data` must be set on the instance before `.render()` is called
    (build.py does this) since Manim's CLI-style scene construction
    doesn't take constructor arguments.
    """

    data: SceneData = None

    def construct(self):
        data = self.data
        if data is None:
            raise RuntimeError("PriceLineScene.data must be set before rendering")

        title = Text(data.title, font_size=40, weight="BOLD").to_edge(UP, buff=0.6)
        subtitle = None
        if data.subtitle:
            subtitle = Text(data.subtitle, font_size=24, color=GREY).next_to(title, DOWN, buff=0.2)

        values = [p.value for p in data.points]
        labels = [p.date for p in data.points]
        y_min, y_max = min(values), max(values)
        pad = (y_max - y_min) * 0.15 or max(abs(y_min), 1) * 0.1

        axes = Axes(
            x_range=[0, max(len(values) - 1, 1), max(1, len(values) // 6)],
            y_range=[y_min - pad, y_max + pad, (y_max - y_min + 2 * pad) / 5 or 1],
            x_length=10,
            y_length=5,
            axis_config={"include_numbers": False, "color": GREY},
        ).shift(DOWN * 0.3)

        trend_up = values[-1] >= values[0]
        line_color = GREEN if trend_up else RED

        points = [axes.c2p(i, v) for i, v in enumerate(values)]
        dot = Dot(points[0], color=line_color, radius=0.08)

        first_label = Text(labels[0], font_size=18, color=GREY).next_to(
            axes.c2p(0, y_min - pad), DOWN, buff=0.2
        )
        last_label = Text(labels[-1], font_size=18, color=GREY).next_to(
            axes.c2p(len(values) - 1, y_min - pad), DOWN, buff=0.2
        )

        delta_pct = ((values[-1] - values[0]) / values[0] * 100) if values[0] else 0.0
        delta_text = Text(
            f"{'+' if delta_pct >= 0 else ''}{delta_pct:.2f}%",
            font_size=30,
            color=line_color,
        ).next_to(axes, UP, buff=0.15).align_to(axes, RIGHT)

        self.play(Write(title))
        if subtitle:
            self.play(FadeIn(subtitle))
        self.play(Create(axes), FadeIn(first_label), FadeIn(last_label))
        self.add(dot)

        for i in range(len(points) - 1):
            segment = Line(points[i], points[i + 1], color=line_color, stroke_width=4)
            self.play(Create(segment), dot.animate.move_to(points[i + 1]), run_time=max(0.5, 3 / len(points)))

        self.play(FadeIn(delta_text))
        self.wait(1)
