"""Tests for schema parsing and data validation. No Manim import here —
these must stay fast and runnable without the heavy manim/ffmpeg stack."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "fin-anim" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from data_loader import load_scene_data, validate_scene_data  # noqa: E402
from schema import SceneData, WhiteboardBeat  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

ALL_KINDS = {"price_line", "candlestick", "bar_comparison", "kpi_counter", "whiteboard_explainer"}


@pytest.mark.parametrize(
    "filename",
    [
        "price_line.json",
        "candlestick.json",
        "kpi_counter.json",
        "bar_comparison.json",
        "whiteboard_explainer.json",
    ],
)
def test_bundled_examples_are_valid(filename):
    data = load_scene_data(EXAMPLES_DIR / filename)
    assert data.title
    assert data.kind in ALL_KINDS


def test_price_line_round_trip():
    raw = json.loads((EXAMPLES_DIR / "price_line.json").read_text())
    data = SceneData.from_dict(raw)
    assert len(data.points) == 5
    assert data.points[0].date == "Mon"
    assert data.points[-1].value == 129.6


def test_missing_required_field_raises():
    data = SceneData(kind="price_line", title="Empty series")
    with pytest.raises(ValueError, match="requires non-empty 'points'"):
        validate_scene_data(data)


def test_missing_title_raises():
    data = SceneData(kind="kpi_counter", title="", kpi_label="Revenue")
    with pytest.raises(ValueError, match="non-empty 'title'"):
        validate_scene_data(data)


def test_unknown_kind_raises():
    data = SceneData(kind="pie_chart", title="Unsupported")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unknown scene kind"):
        validate_scene_data(data)


def test_whiteboard_beats_round_trip():
    raw = json.loads((EXAMPLES_DIR / "whiteboard_explainer.json").read_text())
    data = SceneData.from_dict(raw)
    assert len(data.beats) == 3
    assert data.beats[0].visual == "piggy_bank"
    assert data.beats[0].label == "Save $100"
    assert data.beats[-1].duration == 4.0


def test_whiteboard_unknown_icon_raises():
    data = SceneData(
        kind="whiteboard_explainer",
        title="Bad Icon",
        beats=[WhiteboardBeat(narration="...", visual="pie_chart", label="Nope")],
    )
    with pytest.raises(ValueError, match="unknown visual 'pie_chart'"):
        validate_scene_data(data)


def test_whiteboard_missing_label_raises():
    data = SceneData(
        kind="whiteboard_explainer",
        title="Missing Label",
        beats=[WhiteboardBeat(narration="...", visual="clock", label="")],
    )
    with pytest.raises(ValueError, match="requires a non-empty 'label'"):
        validate_scene_data(data)


def test_whiteboard_text_visual_is_allowed():
    data = SceneData(
        kind="whiteboard_explainer",
        title="Text Beat",
        beats=[WhiteboardBeat(narration="...", visual="text", label="Just a caption")],
    )
    validate_scene_data(data)  # should not raise
