"""Shared whiteboard-style building blocks: colors, marker-cursor mobject,
doodle icon library, and the draw-while-tracking-cursor helper.

v1 simplification #1: the "hand" is a stylized marker-tip cursor (an angled
shaft + round tip), not an illustrated hand — a full hand-and-pen illustration
is a natural follow-up, not required for the whiteboard *feel* this scene is
after.

v1 simplification #2: the cursor sweeps linearly across each visual's
bounding box rather than tracing its exact stroke path. Point-for-point path
tracking across a VGroup made of several unrelated shapes (a clock's face +
hour hand + minute hand, say) isn't reliably exposed as one continuous path by
Manim's VMobject API — a diagonal sweep synced to the same Create() already
reads convincingly as "drawing this" without that complexity.
"""
from __future__ import annotations

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    Arc,
    Circle,
    Ellipse,
    Line,
    Rectangle,
    RoundedRectangle,
    Square,
    Text,
    Triangle,
    UpdateFromAlphaFunc,
    VGroup,
)

from schema import WHITEBOARD_ICONS

WHITEBOARD_COLOR = "#FAF7F0"
MARKER_COLOR = "#2B2B2B"
ACCENT_COLOR = "#1F5FBF"

CURSOR_OFFSET = UP * 0.15 + RIGHT * 0.15


def make_cursor() -> VGroup:
    """A simple marker-tip cursor: a short angled shaft with a round accent tip."""
    shaft = Line(DOWN * 0.5 + LEFT * 0.15, UP * 0.5 + RIGHT * 0.15, color=MARKER_COLOR, stroke_width=10)
    tip = Circle(radius=0.08, color=ACCENT_COLOR, fill_color=ACCENT_COLOR, fill_opacity=1)
    tip.move_to(DOWN * 0.5 + LEFT * 0.15)
    return VGroup(shaft, tip)


def draw_with_hand(scene, mobject, cursor: VGroup, run_time: float) -> None:
    """Plays Create(mobject) while cursor sweeps diagonally across its bounding box."""
    from manim import Create  # local import keeps the public import list above minimal

    start = mobject.get_corner(UP + LEFT) + CURSOR_OFFSET
    end = mobject.get_corner(DOWN + RIGHT) + CURSOR_OFFSET
    cursor.move_to(start)

    def update_cursor(mob, alpha):
        mob.move_to(start + (end - start) * alpha)

    scene.play(Create(mobject), UpdateFromAlphaFunc(cursor, update_cursor), run_time=run_time)


def build_icon(name: str) -> VGroup:
    builder = _ICON_BUILDERS.get(name)
    if builder is None:
        raise ValueError(f"Unknown whiteboard icon: {name!r}. Known icons: {sorted(_ICON_BUILDERS)}")
    return builder()


def _icon_dollar() -> VGroup:
    return VGroup(Text("$", font_size=160, color=MARKER_COLOR))


def _icon_arrow_up() -> VGroup:
    shaft = Line(DOWN * 1.1, UP * 0.9, color=MARKER_COLOR, stroke_width=10)
    head = Triangle(color=MARKER_COLOR, fill_color=MARKER_COLOR, fill_opacity=1).scale(0.35)
    head.move_to(UP * 1.15)
    return VGroup(shaft, head)


def _icon_arrow_down() -> VGroup:
    shaft = Line(UP * 1.1, DOWN * 0.9, color=MARKER_COLOR, stroke_width=10)
    head = Triangle(color=MARKER_COLOR, fill_color=MARKER_COLOR, fill_opacity=1).scale(0.35).rotate(PI)
    head.move_to(DOWN * 1.15)
    return VGroup(shaft, head)


def _icon_clock() -> VGroup:
    face = Circle(radius=1.1, color=MARKER_COLOR, stroke_width=8)
    hour = Line(ORIGIN, UP * 0.5, color=MARKER_COLOR, stroke_width=6)
    minute = Line(ORIGIN, RIGHT * 0.8, color=MARKER_COLOR, stroke_width=5)
    return VGroup(face, hour, minute)


def _icon_house() -> VGroup:
    base = Square(side_length=1.5, color=MARKER_COLOR, stroke_width=8)
    roof = Triangle(color=MARKER_COLOR, stroke_width=8).scale(1.15)
    roof.next_to(base, UP, buff=-0.15)
    door = Rectangle(width=0.4, height=0.7, color=MARKER_COLOR, stroke_width=6)
    door.move_to(base.get_bottom() + UP * 0.35)
    return VGroup(roof, base, door)


def _icon_piggy_bank() -> VGroup:
    body = Ellipse(width=2.2, height=1.5, color=MARKER_COLOR, stroke_width=8)
    slot = Line(DOWN * 0.1, UP * 0.15, color=MARKER_COLOR, stroke_width=6)
    slot.move_to(body.get_top())
    legs = VGroup(
        *[
            Line(UP * 0.15, DOWN * 0.15, color=MARKER_COLOR, stroke_width=6).move_to(
                body.get_bottom() + shift
            )
            for shift in (LEFT * 0.6, RIGHT * 0.6)
        ]
    )
    return VGroup(body, slot, legs)


def _icon_coin_stack() -> VGroup:
    coins = VGroup(
        *[
            Ellipse(width=1.4, height=0.4, color=MARKER_COLOR, stroke_width=6).shift(UP * 0.32 * i)
            for i in range(3)
        ]
    )
    return coins


def _icon_calculator() -> VGroup:
    body = RoundedRectangle(width=1.3, height=1.9, corner_radius=0.15, color=MARKER_COLOR, stroke_width=8)
    screen = Rectangle(width=0.9, height=0.4, color=MARKER_COLOR, stroke_width=5)
    screen.move_to(body.get_top() + DOWN * 0.45)
    buttons = VGroup(
        *[
            Rectangle(width=0.22, height=0.22, color=MARKER_COLOR, stroke_width=4).move_to(
                body.get_center() + RIGHT * col * 0.35 + DOWN * (0.15 + row * 0.35)
            )
            for row in range(3)
            for col in (-1, 0, 1)
        ]
    )
    return VGroup(body, screen, buttons)


def _icon_chart_bar() -> VGroup:
    heights = [0.6, 1.0, 1.5, 1.0]
    bars = VGroup(
        *[
            Rectangle(width=0.4, height=h, color=MARKER_COLOR, stroke_width=6).move_to(
                RIGHT * i * 0.55 + UP * h / 2
            )
            for i, h in enumerate(heights)
        ]
    )
    axis = Line(LEFT * 0.5, RIGHT * (0.55 * len(heights)), color=MARKER_COLOR, stroke_width=6)
    axis.move_to(bars.get_bottom() + DOWN * 0.02)
    return VGroup(axis, bars)


def _icon_lightbulb() -> VGroup:
    bulb = Circle(radius=0.7, color=MARKER_COLOR, stroke_width=8)
    base = Rectangle(width=0.5, height=0.3, color=MARKER_COLOR, stroke_width=6)
    base.next_to(bulb, DOWN, buff=0)
    rays = VGroup(
        *[
            Line(
                bulb.get_center() + direction * 0.9,
                bulb.get_center() + direction * 1.3,
                color=MARKER_COLOR,
                stroke_width=5,
            )
            for direction in (UP, LEFT, RIGHT, UP + LEFT, UP + RIGHT)
        ]
    )
    return VGroup(rays, bulb, base)


def _icon_scale() -> VGroup:
    pole = Line(DOWN * 1.1, UP * 1.1, color=MARKER_COLOR, stroke_width=8)
    beam = Line(LEFT * 1.1, RIGHT * 1.1, color=MARKER_COLOR, stroke_width=8).move_to(UP * 1.0)
    left_pan = Line(LEFT * 1.1 + UP * 1.0, LEFT * 1.1 + DOWN * 0.3, color=MARKER_COLOR, stroke_width=5)
    right_pan = Line(RIGHT * 1.1 + UP * 1.0, RIGHT * 1.1 + DOWN * 0.3, color=MARKER_COLOR, stroke_width=5)
    left_bowl = Arc(radius=0.35, start_angle=PI, angle=PI, color=MARKER_COLOR, stroke_width=6)
    left_bowl.move_to(LEFT * 1.1 + DOWN * 0.3)
    right_bowl = Arc(radius=0.35, start_angle=PI, angle=PI, color=MARKER_COLOR, stroke_width=6)
    right_bowl.move_to(RIGHT * 1.1 + DOWN * 0.3)
    return VGroup(pole, beam, left_pan, right_pan, left_bowl, right_bowl)


_ICON_BUILDERS = {
    "dollar": _icon_dollar,
    "arrow_up": _icon_arrow_up,
    "arrow_down": _icon_arrow_down,
    "clock": _icon_clock,
    "house": _icon_house,
    "piggy_bank": _icon_piggy_bank,
    "coin_stack": _icon_coin_stack,
    "calculator": _icon_calculator,
    "chart_bar": _icon_chart_bar,
    "lightbulb": _icon_lightbulb,
    "scale": _icon_scale,
}

assert set(_ICON_BUILDERS) == WHITEBOARD_ICONS, "icon builders and schema.WHITEBOARD_ICONS drifted apart"
