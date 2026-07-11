"""Load and validate scene data from a JSON file on disk."""
from __future__ import annotations

import json
from pathlib import Path

from schema import WHITEBOARD_ICONS, SceneData

# Maps each scene kind to the one field that must be non-empty for it.
REQUIRED_FIELDS = {
    "price_line": "points",
    "candlestick": "candles",
    "bar_comparison": "bars",
    "kpi_counter": "kpi_label",
    "whiteboard_explainer": "beats",
}


def load_scene_data(path: str | Path) -> SceneData:
    raw = json.loads(Path(path).read_text())
    data = SceneData.from_dict(raw)
    validate_scene_data(data)
    return data


def validate_scene_data(data: SceneData) -> None:
    if data.kind not in REQUIRED_FIELDS:
        raise ValueError(
            f"Unknown scene kind: {data.kind!r}. Expected one of {sorted(REQUIRED_FIELDS)}"
        )
    if not data.title:
        raise ValueError("Scene data requires a non-empty 'title'")

    field_name = REQUIRED_FIELDS[data.kind]
    if not getattr(data, field_name):
        raise ValueError(f"Scene kind {data.kind!r} requires non-empty '{field_name}'")

    if data.kind == "whiteboard_explainer":
        _validate_whiteboard_beats(data.beats)


def _validate_whiteboard_beats(beats) -> None:
    for i, beat in enumerate(beats):
        if beat.visual == "image":
            if not beat.image_path:
                raise ValueError(f"beats[{i}]: visual 'image' requires a non-empty 'image_path'")
            if not Path(beat.image_path).exists():
                raise ValueError(
                    f"beats[{i}]: image_path {beat.image_path!r} does not exist — generate it "
                    "first (see tools/colab_generate_icons.ipynb) and use its real saved path"
                )
        elif beat.visual == "svg":
            if not beat.svg_path:
                raise ValueError(f"beats[{i}]: visual 'svg' requires a non-empty 'svg_path'")
            if not Path(beat.svg_path).exists():
                raise ValueError(
                    f"beats[{i}]: svg_path {beat.svg_path!r} does not exist — download/save it "
                    "first (e.g. a free CC0 illustration from undraw.co) and use its real saved path"
                )
        elif beat.visual != "text" and beat.visual not in WHITEBOARD_ICONS:
            raise ValueError(
                f"beats[{i}]: unknown visual {beat.visual!r}. "
                f"Expected 'text', 'image', 'svg', or one of {sorted(WHITEBOARD_ICONS)}"
            )
        if not beat.label:
            raise ValueError(
                f"beats[{i}]: requires a non-empty 'label' (short on-screen caption, "
                "not the full narration)"
            )
