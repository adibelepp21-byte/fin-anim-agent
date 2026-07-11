#!/usr/bin/env python3
"""CLI entry point: render a fin-anim-agent scene from a JSON data file.

Usage:
    python3 build.py --data data.json --output out.mp4 [--quality l|m|h]

Always invoke with the full path to this file (e.g.
`python3 skills/fin-anim/scripts/build.py ...`) rather than `cd`-ing into
scripts/ first — Python adds this file's own directory to sys.path, which
is what lets `schema` and `scenes.*` resolve regardless of the caller's cwd.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from manim import tempconfig

from data_loader import load_scene_data
from scenes.bar_comparison import BarComparisonScene
from scenes.candlestick import CandlestickScene
from scenes.kpi_counter import KPICounterScene
from scenes.price_line import PriceLineScene
from scenes.whiteboard_explainer import WhiteboardExplainerScene

SCENE_CLASSES = {
    "price_line": PriceLineScene,
    "candlestick": CandlestickScene,
    "bar_comparison": BarComparisonScene,
    "kpi_counter": KPICounterScene,
    "whiteboard_explainer": WhiteboardExplainerScene,
}

QUALITY_FLAGS = {
    "l": {"pixel_width": 854, "pixel_height": 480, "frame_rate": 30},
    "m": {"pixel_width": 1280, "pixel_height": 720, "frame_rate": 30},
    "h": {"pixel_width": 1920, "pixel_height": 1080, "frame_rate": 60},
}


def build(data_path: str, output_path: str, quality: str = "m") -> Path:
    data = load_scene_data(data_path)
    scene_cls = SCENE_CLASSES[data.kind]

    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as media_dir:
        with tempconfig({**QUALITY_FLAGS[quality], "media_dir": media_dir, "disable_caching": True}):
            scene = scene_cls()
            scene.data = data
            scene.render()

        rendered = list(Path(media_dir).rglob("*.mp4"))
        if not rendered:
            raise RuntimeError("manim did not produce an output video — check the scene for errors above")
        shutil.move(str(rendered[0]), output)

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a fin-anim-agent Manim scene from JSON data.")
    parser.add_argument("--data", required=True, help="Path to scene data JSON file (see schema.py)")
    parser.add_argument("--output", required=True, help="Output video path, e.g. out/scene.mp4")
    parser.add_argument(
        "--quality", choices=["l", "m", "h"], default="m", help="Render quality: l=480p m=720p h=1080p60"
    )
    args = parser.parse_args()

    try:
        result = build(args.data, args.output, args.quality)
    except Exception as exc:  # surfaced to the calling agent, never swallowed
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"rendered: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
