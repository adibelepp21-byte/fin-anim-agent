"""Data contract for fin-anim-agent scenes.

This is the single schema every scene renderer and every data source
(live MCP fetch or manual user input) must agree on. Keeping it in one
place means adding a new scene kind only requires a new dataclass +
a new REQUIRED_FIELDS entry in data_loader.py, not a new format.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SceneKind = Literal[
    "price_line", "candlestick", "bar_comparison", "kpi_counter", "whiteboard_explainer"
]

# Icon names the whiteboard_explainer scene knows how to draw. Kept here (not in
# scenes/whiteboard_assets.py, which imports manim) so data_loader.py can validate
# a beat's `visual` field without needing manim installed just to run fast tests.
WHITEBOARD_ICONS = frozenset(
    {
        "dollar",
        "arrow_up",
        "arrow_down",
        "clock",
        "house",
        "piggy_bank",
        "coin_stack",
        "calculator",
        "chart_bar",
        "lightbulb",
        "scale",
    }
)


@dataclass
class PricePoint:
    date: str
    value: float


@dataclass
class Candle:
    date: str
    open: float
    high: float
    low: float
    close: float


@dataclass
class BarItem:
    label: str
    value: float


@dataclass
class WhiteboardBeat:
    """One narrated beat of a whiteboard_explainer scene: draw `visual` (an icon
    name from WHITEBOARD_ICONS, or "text"), speak `narration`, hold for `duration`
    seconds, then erase before the next beat.

    `label` is the short on-screen caption (a few words) — not the narration
    itself, which is meant to be heard, not read.

    `audio_path` and `duration` are normally filled in by the agent after
    generating narration audio (e.g. via the elevenlabs skill) and measuring its
    real length with scripts/audio_duration.py — not typed by the user.
    """

    narration: str = ""
    visual: str = "text"
    label: str = ""
    audio_path: str = ""
    duration: float = 3.0


@dataclass
class SceneData:
    kind: SceneKind
    title: str
    subtitle: str = ""
    ticker: str = ""
    currency: str = "USD"
    source: str = ""

    points: list[PricePoint] = field(default_factory=list)
    candles: list[Candle] = field(default_factory=list)
    bars: list[BarItem] = field(default_factory=list)
    beats: list[WhiteboardBeat] = field(default_factory=list)

    kpi_label: str = ""
    kpi_value: float = 0.0
    kpi_delta_pct: float = 0.0

    @staticmethod
    def from_dict(raw: dict) -> "SceneData":
        data = SceneData(
            kind=raw["kind"],
            title=raw["title"],
            subtitle=raw.get("subtitle", ""),
            ticker=raw.get("ticker", ""),
            currency=raw.get("currency", "USD"),
            source=raw.get("source", ""),
            kpi_label=raw.get("kpi_label", ""),
            kpi_value=raw.get("kpi_value", 0.0),
            kpi_delta_pct=raw.get("kpi_delta_pct", 0.0),
        )
        data.points = [PricePoint(**p) for p in raw.get("points", [])]
        data.candles = [Candle(**c) for c in raw.get("candles", [])]
        data.bars = [BarItem(**b) for b in raw.get("bars", [])]
        data.beats = [WhiteboardBeat(**b) for b in raw.get("beats", [])]
        return data
