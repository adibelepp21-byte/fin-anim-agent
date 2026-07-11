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
        "whiteboard_explainer_image.json",
        "whiteboard_explainer_svg.json",
    ],
)
def test_bundled_examples_are_valid(filename, monkeypatch):
    # whiteboard_explainer_image.json/whiteboard_explainer_svg.json's paths are
    # repo-root-relative (matching how --data/--output are already documented as
    # repo-root-relative in README/SKILL.md) — chdir so the examples are valid
    # regardless of the invoking cwd.
    monkeypatch.chdir(EXAMPLES_DIR.parent)
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


def test_whiteboard_image_missing_path_raises():
    data = SceneData(
        kind="whiteboard_explainer",
        title="Image Beat",
        beats=[WhiteboardBeat(narration="...", visual="image", label="Caption", image_path="")],
    )
    with pytest.raises(ValueError, match="visual 'image' requires a non-empty 'image_path'"):
        validate_scene_data(data)


def test_whiteboard_image_nonexistent_path_raises():
    data = SceneData(
        kind="whiteboard_explainer",
        title="Image Beat",
        beats=[
            WhiteboardBeat(
                narration="...", visual="image", label="Caption", image_path="/no/such/file.png"
            )
        ],
    )
    with pytest.raises(ValueError, match="does not exist"):
        validate_scene_data(data)


def test_whiteboard_image_existing_path_is_allowed(tmp_path):
    icon_path = tmp_path / "icon.png"
    icon_path.write_bytes(b"not a real png, existence is all validate_scene_data checks")
    data = SceneData(
        kind="whiteboard_explainer",
        title="Image Beat",
        beats=[
            WhiteboardBeat(narration="...", visual="image", label="Caption", image_path=str(icon_path))
        ],
    )
    validate_scene_data(data)  # should not raise


def test_whiteboard_svg_missing_path_raises():
    data = SceneData(
        kind="whiteboard_explainer",
        title="SVG Beat",
        beats=[WhiteboardBeat(narration="...", visual="svg", label="Caption", svg_path="")],
    )
    with pytest.raises(ValueError, match="visual 'svg' requires a non-empty 'svg_path'"):
        validate_scene_data(data)


def test_whiteboard_svg_nonexistent_path_raises():
    data = SceneData(
        kind="whiteboard_explainer",
        title="SVG Beat",
        beats=[
            WhiteboardBeat(narration="...", visual="svg", label="Caption", svg_path="/no/such/file.svg")
        ],
    )
    with pytest.raises(ValueError, match="does not exist"):
        validate_scene_data(data)


def test_whiteboard_svg_existing_path_is_allowed(tmp_path):
    svg_path = tmp_path / "scene.svg"
    svg_path.write_text("<svg></svg>")
    data = SceneData(
        kind="whiteboard_explainer",
        title="SVG Beat",
        beats=[WhiteboardBeat(narration="...", visual="svg", label="Caption", svg_path=str(svg_path))],
    )
    validate_scene_data(data)  # should not raise
