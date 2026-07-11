"""Shared whiteboard-style building blocks: colors, the hand-and-pen mobject,
doodle icon library, and the draw-while-tracing-path helper.

The hand is a stylized sketch (fist + fingers + thumb + pen), not an
anatomically detailed illustration — that's a deliberate simplification, not a
missing feature; a rougher-but-legible hand is what most real whiteboard-video
tools use too, and it's what reads clearly at the small size a hand-plus-doodle
composition renders at.

Path tracing is per-leaf-shape, not per-icon: `build_icon()` returns a VGroup
whose children are plain primitives (Circle, Line, Ellipse, Rectangle,
Triangle, Arc) or nested VGroups of those (e.g. piggy_bank's two legs). Each
*leaf* primitive is a single continuous VMobject path, so `draw_icon_with_hand`
flattens the tree and draws one leaf at a time, moving the hand's pen tip along
that leaf's own `point_from_proportion(alpha)` — real per-stroke tracing, not a
bounding-box sweep. The same function draws "text" beats too, since Manim's
Text is itself a VGroup of one-path-per-glyph submobjects — for a short label
this looks like the hand actually handwriting it letter by letter.
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
    Create,
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
SKIN_COLOR = "#E8B48C"

# Small nudge so the pen-tip circle sits just past the ink rather than
# dead-centered on top of it (which would visually hide the stroke's leading edge).
TIP_NUDGE = UP * 0.03 + RIGHT * 0.02


def make_hand_cursor() -> VGroup:
    """Builds a stylized hand-holding-a-pen. The pen tip sits at local (0, 0, 0)
    at construction time — `draw_icon_with_hand` tracks that point via the
    `tip_position` attribute set here, updating it (and shifting the whole
    group rigidly) every time the hand moves, so the fist/fingers/pen shaft
    always carry along together instead of only the tip snapping to place.
    """
    pen_tip = Circle(radius=0.06, color=ACCENT_COLOR, fill_color=ACCENT_COLOR, fill_opacity=1)
    pen_shaft = Line(ORIGIN, UP * 0.55 + RIGHT * 0.22, color="#3A3A3A", stroke_width=14)

    fist = Ellipse(
        width=0.5, height=0.36, color=MARKER_COLOR, fill_color=SKIN_COLOR, fill_opacity=1, stroke_width=2
    )
    fist.move_to(UP * 0.62 + RIGHT * 0.22)

    thumb = Ellipse(
        width=0.22, height=0.14, color=MARKER_COLOR, fill_color=SKIN_COLOR, fill_opacity=1, stroke_width=2
    )
    thumb.move_to(fist.get_center() + LEFT * 0.18 + DOWN * 0.06)
    thumb.rotate(0.4)

    fingers = VGroup(
        *[
            Ellipse(
                width=0.16, height=0.3, color=MARKER_COLOR, fill_color=SKIN_COLOR, fill_opacity=1, stroke_width=2
            )
            .move_to(fist.get_center() + UP * 0.2 + RIGHT * (i * 0.14 - 0.14))
            .rotate(0.18 * (i - 1))
            for i in range(3)
        ]
    )

    hand = VGroup(pen_shaft, fist, thumb, fingers, pen_tip)
    hand.tip_position = ORIGIN
    return hand


def _flatten_vmobjects(mobject) -> list:
    """Returns the leaf drawable shapes inside a (possibly nested) VGroup, in
    the order they were added. Each leaf is a single continuous path that
    `point_from_proportion` can trace exactly."""
    if not mobject.submobjects:
        return [mobject]
    leaves: list = []
    for sub in mobject.submobjects:
        leaves.extend(_flatten_vmobjects(sub))
    return leaves


def draw_icon_with_hand(scene, icon, hand: VGroup, total_run_time: float) -> None:
    """Draws each leaf shape inside `icon` in sequence, moving `hand` so its pen
    tip traces the point currently being drawn — real per-stroke tracing, one
    shape at a time, rather than one Create() for the whole icon at once."""
    leaves = _flatten_vmobjects(icon)
    if not leaves:
        return

    per_leaf_time = max(total_run_time / len(leaves), 0.06)

    for leaf in leaves:
        start_point = leaf.point_from_proportion(0) + TIP_NUDGE
        hand.shift(start_point - hand.tip_position)
        hand.tip_position = start_point

        def update_hand(mob, alpha, leaf=leaf):
            target = leaf.point_from_proportion(alpha) + TIP_NUDGE
            mob.shift(target - mob.tip_position)
            mob.tip_position = target

        scene.play(Create(leaf), UpdateFromAlphaFunc(hand, update_hand), run_time=per_leaf_time)


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
