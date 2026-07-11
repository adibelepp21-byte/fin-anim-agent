# fin-anim-agent

A Claude Code skill that turns financial data — live market data or numbers you give
it — into short 2D animated explainer videos, rendered with [Manim](https://www.manim.community/).

Ask it things like:

- "Animate NVDA's price move this week"
- "Make a KPI reveal video: Q3 revenue $4.2B, up 12.4%"
- "Animate a candlestick chart for AAPL's last 5 sessions"
- "Compare revenue by segment as an animated bar chart"

## How it works

```
financial data (MCP fetch or manual input)
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

Four scene kinds today: `price_line`, `candlestick`, `bar_comparison`, `kpi_counter`.
See `skills/fin-anim/SKILL.md` for the full spec the agent follows, and `examples/`
for a sample data file per kind.

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
- `skills/fin-anim/scripts/build.py` — CLI: JSON in, MP4 out
- `examples/` — one sample data file per scene kind
- `tests/` — schema/validation tests (fast, no Manim import)

## Adding a new scene kind

1. Extend `SceneKind` and `SceneData` in `schema.py`.
2. Add its required-field entry to `REQUIRED_FIELDS` in `data_loader.py`.
3. Add a `scripts/scenes/<kind>.py` with a `Scene` subclass following the existing
   pattern (`data: SceneData = None`, read `self.data` in `construct()`).
4. Register it in `SCENE_CLASSES` in `build.py`.
5. Add an example file under `examples/` and a test in `tests/`.

## License

MIT
