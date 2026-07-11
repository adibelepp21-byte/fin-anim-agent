"""Whiteboard-style explainer: hand-drawn icons/text, narrated beat by beat.

Classic whiteboard-video rhythm: draw something while it's being talked about,
hold it on screen for the rest of the narration, wipe it, draw the next thing.
"""
from manim import DOWN, UP, Create, FadeOut, Scene, Text, VGroup

from schema import SceneData
from scenes.whiteboard_assets import MARKER_COLOR, WHITEBOARD_COLOR, build_icon, draw_with_hand, make_cursor

HANDWRITING_FONT = "Kalam"  # a handwriting Google Font if installed; Pango silently
# substitutes a default font if it isn't, so this never crashes on a bare system.


class WhiteboardExplainerScene(Scene):
    """Good for teaching a financial concept in a few narrated beats, each
    paired with one hand-drawn icon or short caption."""

    data: SceneData = None

    def construct(self):
        data = self.data
        if data is None:
            raise RuntimeError("WhiteboardExplainerScene.data must be set before rendering")
        if not data.beats:
            raise RuntimeError("WhiteboardExplainerScene requires at least one beat")

        self.camera.background_color = WHITEBOARD_COLOR

        title = Text(data.title, font_size=44, color=MARKER_COLOR, weight="BOLD", font=HANDWRITING_FONT)
        if title.width > 11:
            title.scale_to_fit_width(11)
        self.play(Create(title), run_time=1.0)
        self.wait(0.5)
        self.play(FadeOut(title), run_time=0.5)

        cursor = make_cursor()

        for beat in data.beats:
            visual = self._build_visual(beat)
            draw_time = max(0.8, min(beat.duration * 0.5, 3.0))
            hold_time = max(0.0, beat.duration - draw_time)

            if beat.audio_path:
                self.add_sound(beat.audio_path, time_offset=0)

            self.add(cursor)
            draw_with_hand(self, visual, cursor, run_time=draw_time)
            self.remove(cursor)

            if hold_time > 0:
                self.wait(hold_time)

            self.play(FadeOut(visual), run_time=0.4)

    def _build_visual(self, beat) -> VGroup:
        if beat.visual == "text":
            body = Text(beat.label, font_size=36, color=MARKER_COLOR, font=HANDWRITING_FONT)
            if body.width > 10:
                body.scale_to_fit_width(10)
            return VGroup(body)

        icon = build_icon(beat.visual)
        icon.scale(1.4).shift(UP * 0.6)
        label = Text(beat.label, font_size=32, color=MARKER_COLOR, font=HANDWRITING_FONT)
        label.next_to(icon, DOWN, buff=0.5)
        return VGroup(icon, label)
