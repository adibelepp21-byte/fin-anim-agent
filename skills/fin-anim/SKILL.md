---
name: fin-anim
description: Generates short 2D animated videos that explain financial data — price trend lines, OHLC candlestick charts, single-metric KPI reveals ("Q3 revenue +12%"), and category comparisons (revenue by segment) — rendered with Manim. Use when the user asks to animate, visualize, or explain stock/market/earnings data as a video, or asks for a "financial explainer animation", "animated stock chart", "earnings recap video", or similar.
user-invocable: true
argument-hint: <ticker-or-topic> [--kind price_line|candlestick|bar_comparison|kpi_counter]
---

# fin-anim

Turns financial data — live market data or a figure the user hands you — into a short
2D Manim animation. This skill is the glue between data and video: it does not fetch
data itself (that's whatever MCP tools or user input are available in the session) and
it does not do voiceover/compositing (hand off to `elevenlabs` / `remotion` for that).

## Scope

Four scene kinds, one per shape of financial story:

| Kind | Use for | Required data |
|---|---|---|
| `price_line` | A ticker/index/metric moving over time | `points`: list of `{date, value}` |
| `candlestick` | OHLC price action | `candles`: list of `{date, open, high, low, close}` |
| `bar_comparison` | Comparing labeled values (segments, regions, peers) | `bars`: list of `{label, value}` |
| `kpi_counter` | One number landing with a delta (revenue, EPS, growth %) | `kpi_label`, `kpi_value`, `kpi_delta_pct` |

If the request doesn't clearly map to one of these, ask the user which shape fits
rather than guessing — a wrong scene kind wastes a full render cycle.

## Step 0 — check Manim is installed

```bash
python3 -c "import manim" 2>&1 || echo "NOT INSTALLED"
```

If not installed: `pip install -r requirements.txt` from the repo root (needs
`manim` + its system dependency, `ffmpeg` — Manim's docs cover per-OS setup if
`pip install manim` alone fails on missing Cairo/Pango).

## Step 1 — get the data

Prefer live data when the session has it connected; fall back to whatever the user
gives you directly. Do not fabricate numbers — if neither source has real data, say so
and ask, rather than inventing a plausible-looking series.

- **Live market data via MCP**: if an Alpha Vantage, Bigdata.com, or similar financial
  MCP server is connected this session, call its tools directly (e.g. a daily time
  series function for `price_line`/`candlestick`, a quote/overview function for
  `kpi_counter`). Map the returned series into the schema below yourself — these
  tools return their own JSON shapes, not this skill's schema.
- **Manual input**: the user pastes numbers, a table, or describes the story in prose
  ("Q3 revenue was $4.2B, up 12% from Q2"). Extract the numbers into the schema
  yourself; ask a clarifying question only if a required field is genuinely missing
  or ambiguous (e.g. they gave a % change but no base value for `kpi_counter`).

## Step 2 — write the data file

Write a JSON file matching `scripts/schema.py`'s `SceneData` shape to a scratch path
(e.g. `/tmp/fin-anim-data.json` or this session's scratchpad dir). Examples for each
kind are in `examples/`. Minimal `price_line` example:

```json
{
  "kind": "price_line",
  "title": "NVDA — Last 6 Sessions",
  "subtitle": "Daily close, USD",
  "ticker": "NVDA",
  "source": "Alpha Vantage TIME_SERIES_DAILY",
  "points": [
    {"date": "Mon", "value": 118.2},
    {"date": "Tue", "value": 121.4},
    {"date": "Wed", "value": 119.8},
    {"date": "Thu", "value": 124.1},
    {"date": "Fri", "value": 129.6}
  ]
}
```

`data_loader.py` validates the file before rendering starts and fails fast with a
clear error if a required field for the chosen `kind` is missing — read that error
back to the user rather than retrying blindly.

## Step 3 — render

```bash
python3 skills/fin-anim/scripts/build.py --data /tmp/fin-anim-data.json --output out/fin-anim.mp4 --quality m
```

- `--quality l|m|h` trades render time for resolution (480p/720p/1080p60). Default
  to `m` unless the user asks for a quick draft (`l`) or a final deliverable (`h`).
- On success it prints `rendered: <path>` — report that path back to the user.
- On failure it prints `error: ...` to stderr and exits non-zero — read the message,
  fix the data file or scene choice, and retry once. If it fails twice, stop and show
  the user the actual error instead of guessing at a third fix.

## Step 4 — offer next steps

After a successful render, offer (don't force) natural follow-ups:
- Narration/voiceover via the `elevenlabs` skill, synced to the animation's beats.
- Compositing multiple scenes, transitions, or branding into one video via `remotion`
  or the `claude-code-video-toolkit`, if the user wants more than a single clip.
- A different scene `kind` on the same data (e.g. also render the `kpi_counter` view
  of a stock move alongside its `price_line`).

## Design notes for future scene kinds

Each scene is a self-contained `manim.Scene` subclass in `scripts/scenes/` with a
class-level `data: SceneData = None` slot — `build.py` sets `.data` on the instance
before calling `.render()`, since Manim's own CLI-style construction doesn't take
constructor arguments. Adding a fifth kind means: extend `SceneKind` and `SceneData`
in `schema.py`, add its required-field entry in `data_loader.py`, add the scene class,
and register it in `SCENE_CLASSES` in `build.py`. Don't invent a second data format —
every scene reads from the same `SceneData`.
