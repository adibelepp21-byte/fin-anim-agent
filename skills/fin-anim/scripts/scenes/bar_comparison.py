"""Animated bar chart comparing several labeled values (e.g. revenue by segment)."""
from manim import BLUE, DOWN, GREY, UP, Create, FadeIn, Rectangle, Scene, Text, VGroup, Write

from schema import SceneData


class BarComparisonScene(Scene):
    """Good for category comparisons: revenue by segment, YoY growth by region, etc."""

    data: SceneData = None

    def construct(self):
        data = self.data
        if data is None:
            raise RuntimeError("BarComparisonScene.data must be set before rendering")

        title = Text(data.title, font_size=40, weight="BOLD").to_edge(UP, buff=0.6)

        bars_data = data.bars
        max_val = max((b.value for b in bars_data), default=1) or 1
        bar_width = 1.0
        spacing = 1.6
        max_height = 4.0

        group = VGroup()
        for i, b in enumerate(bars_data):
            height = max(b.value / max_val * max_height, 0.05)
            rect = Rectangle(
                width=bar_width, height=height, color=BLUE, fill_color=BLUE, fill_opacity=0.85
            )
            rect.move_to([i * spacing, height / 2 - 2.0, 0])
            value_label = Text(f"{b.value:,.1f}", font_size=20).next_to(rect, UP, buff=0.1)
            name_label = Text(b.label, font_size=20, color=GREY).next_to(rect, DOWN, buff=0.2)
            group.add(VGroup(rect, value_label, name_label))

        group.move_to([0, 0, 0])

        self.play(Write(title))
        for bar_group in group:
            rect, value_label, name_label = bar_group
            self.play(Create(rect), FadeIn(value_label), FadeIn(name_label), run_time=max(0.3, 2 / len(group)))
        self.wait(1)
