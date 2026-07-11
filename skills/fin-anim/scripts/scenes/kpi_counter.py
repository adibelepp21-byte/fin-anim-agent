"""Animated single-metric KPI counter with a count-up effect and a delta badge."""
from manim import DOWN, GREEN, GREY, RED, UP, FadeIn, Scene, Text, ValueTracker, Write, always_redraw

from schema import SceneData


class KPICounterScene(Scene):
    """Good for one-number moments: 'Q3 revenue: $4.2B (+12.4%)'."""

    data: SceneData = None

    def construct(self):
        data = self.data
        if data is None:
            raise RuntimeError("KPICounterScene.data must be set before rendering")

        title = Text(data.title, font_size=40, weight="BOLD").to_edge(UP, buff=0.8)
        label = Text(data.kpi_label, font_size=28, color=GREY).next_to(title, DOWN, buff=0.5)

        tracker = ValueTracker(0.0)
        counter = always_redraw(
            lambda: Text(f"{tracker.get_value():,.2f}", font_size=72).next_to(label, DOWN, buff=0.6)
        )

        delta_color = GREEN if data.kpi_delta_pct >= 0 else RED
        delta_text = Text(
            f"{'+' if data.kpi_delta_pct >= 0 else ''}{data.kpi_delta_pct:.2f}%",
            font_size=32,
            color=delta_color,
        )

        self.play(Write(title))
        self.play(FadeIn(label))
        self.add(counter)
        self.play(tracker.animate.set_value(data.kpi_value), run_time=1.5)
        delta_text.next_to(counter, DOWN, buff=0.5)
        self.play(FadeIn(delta_text))
        self.wait(1)
