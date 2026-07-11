"""Animated OHLC candlestick chart."""
from manim import DOWN, GREEN, GREY, RED, UP, Axes, Create, FadeIn, Line, Rectangle, Scene, Text, VGroup, Write

from schema import SceneData


class CandlestickScene(Scene):
    """Renders candles left-to-right, colored green (bullish) or red (bearish)."""

    data: SceneData = None

    def construct(self):
        data = self.data
        if data is None:
            raise RuntimeError("CandlestickScene.data must be set before rendering")

        title = Text(data.title, font_size=40, weight="BOLD").to_edge(UP, buff=0.6)

        candles = data.candles
        all_values = [v for c in candles for v in (c.open, c.high, c.low, c.close)]
        y_min, y_max = min(all_values), max(all_values)
        pad = (y_max - y_min) * 0.15 or max(abs(y_min), 1) * 0.1

        axes = Axes(
            x_range=[0, max(len(candles) - 1, 1), max(1, len(candles) // 6)],
            y_range=[y_min - pad, y_max + pad, (y_max - y_min + 2 * pad) / 5 or 1],
            x_length=10,
            y_length=5,
            axis_config={"include_numbers": False, "color": GREY},
        ).shift(DOWN * 0.3)

        width = min(0.4, 8.0 / max(len(candles), 1))
        candle_mobs = []
        for i, c in enumerate(candles):
            bullish = c.close >= c.open
            color = GREEN if bullish else RED
            wick = Line(axes.c2p(i, c.low), axes.c2p(i, c.high), color=color, stroke_width=2)
            body_top = max(c.open, c.close)
            body_bottom = min(c.open, c.close)
            top_y = axes.c2p(0, body_top)[1]
            bottom_y = axes.c2p(0, body_bottom)[1]
            body = Rectangle(
                width=width,
                height=max(top_y - bottom_y, 0.03),
                color=color,
                fill_color=color,
                fill_opacity=1,
            ).move_to(axes.c2p(i, (body_top + body_bottom) / 2))
            candle_mobs.append(VGroup(wick, body))

        self.play(Write(title))
        self.play(Create(axes))
        for mob in candle_mobs:
            self.play(FadeIn(mob), run_time=max(0.15, 2 / len(candle_mobs)))
        self.wait(1)
