# fin-anim-agent

A Claude Code skill that turns financial data and concepts — live market data, numbers
you give it, or a concept to teach — into short 2D animated videos, rendered with
[Manim](https://www.manim.community/).

Ask it things like:

- "Animate NVDA's price move this week"
- "Make a KPI reveal video: Q3 revenue $4.2B, up 12.4%"
- "Animate a candlestick chart for AAPL's last 5 sessions"
- "Compare revenue by segment as an animated bar chart"
- "Make a whiteboard animation explaining compound interest"

## How it works

```
financial data or concept (MCP fetch, manual input, or a concept to teach)
        │
        ▼
  scripts/schema.py     ← one JSON shape for every scene kind
        │
        ▼
  scripts/data_loader.py ← validates before rendering starts
        │
        ▼
  scripts/scenes/*.py    ← one Manim Scene subclass per scene kind
        │
        ▼
  scripts/build.py       ← renders to MP4, quality l/m/h
```

Five scene kinds today: `price_line`, `candlestick`, `bar_comparison`, `kpi_counter`,
and `whiteboard_explainer` (a narrated, hand-drawn-doodle-style explainer for financial
concepts — compound interest, inflation, diversification, and the like — with
per-beat voiceover synced via the `elevenlabs` skill). See `skills/fin-anim/SKILL.md`
for the full spec the agent follows, and `examples/` for a sample data file per kind.

## Install

As a Claude Code plugin:

```
/plugin marketplace add adibelepp21-byte/fin-anim-agent
/plugin install fin-anim-agent@fin-anim-agent
```

Or install the skill directly with the [Agent Skills](https://agentskills.io) CLI:

```
npx skills add adibelepp21-byte/fin-anim-agent -g
```

## Local development

```bash
pip install -r requirements.txt

# render one of the bundled examples
python3 skills/fin-anim/scripts/build.py \
  --data examples/price_line.json \
  --output out/demo.mp4 \
  --quality m

# run tests (schema/validation only — no manim/ffmpeg needed)
pytest tests/ -v
```

## Project layout

- `skills/fin-anim/SKILL.md` — the skill spec Claude reads when `/fin-anim` fires
- `skills/fin-anim/scripts/schema.py` — the data contract (`SceneData`) every scene reads
- `skills/fin-anim/scripts/data_loader.py` — loads + validates a JSON data file
- `skills/fin-anim/scripts/scenes/` — one Manim `Scene` subclass per scene kind
- `skills/fin-anim/scripts/scenes/whiteboard_assets.py` — shared hand-and-pen mobject,
  the vector doodle icon library, the path-tracing draw helper (vector icons/text), and
  the wipe-reveal helper (for `"image"` PNGs) used by `whiteboard_explainer`
- `skills/fin-anim/scripts/build.py` — CLI: JSON in, MP4 out
- `skills/fin-anim/scripts/audio_duration.py` — measures a narration clip's real length
  via ffprobe, for timing `whiteboard_explainer` beats to their voiceover
- `tools/colab_generate_icons.ipynb` — generates whiteboard doodle PNGs for free on
  Colab's GPU tier (local Stable Diffusion, no paid API/MCP credits) — see
  `assets/whiteboard_icons/README.md`
- `assets/whiteboard_icons/` — generated PNGs referenced by `whiteboard_explainer`
  beats with `visual: "image"`
- `examples/` — one sample data file per scene kind
- `tests/` — schema/validation tests (fast, no Manim import)

## Adding a new scene kind

1. Extend `SceneKind` and `SceneData` in `schema.py`.
2. Add its required-field entry (and any kind-specific validation) to
   `data_loader.py`.
3. Add a `scripts/scenes/<kind>.py` with a `Scene` subclass following the existing
   pattern (`data: SceneData = None`, read `self.data` in `construct()`).
4. Register it in `SCENE_CLASSES` in `build.py`.
5. Add an example file under `examples/` and a test in `tests/`.

## Adding a new whiteboard doodle icon

**Built-in vector icon** (free, path-traced by the hand, no generation step):

1. Add an `_icon_<name>()` builder to `scripts/scenes/whiteboard_assets.py`, built from
   Manim primitives (`Circle`, `Rectangle`, `Line`, `Arc`, ...) — no external SVG/image
   assets, keeps the skill self-contained.
2. Register it in `_ICON_BUILDERS` in the same file.
3. Add the same name to `WHITEBOARD_ICONS` in `schema.py` — an assertion at import time
   checks these two lists stay in sync.

**Generated PNG icon** (for a concept the primitives don't cover well, or a more
polished look — wipe-revealed, not path-traced):

1. Add its concept to `ICON_CONCEPTS` in `tools/colab_generate_icons.ipynb`.
2. Run the notebook on Colab (free GPU tier), download `whiteboard_icons.zip`.
3. Drop the PNG into `assets/whiteboard_icons/` and reference it with
   `"visual": "image", "image_path": "assets/whiteboard_icons/<name>.png"`.

## License

MIT
