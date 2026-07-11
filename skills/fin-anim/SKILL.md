---
name: fin-anim
description: Generates short 2D animated videos that explain financial data and concepts — price trend lines, OHLC candlestick charts, single-metric KPI reveals ("Q3 revenue +12%"), category comparisons (revenue by segment), and narrated whiteboard-style explainers of financial concepts (compound interest, inflation, diversification) — rendered with Manim. Use when the user asks to animate, visualize, or explain stock/market/earnings data or a financial concept as a video, or asks for a "financial explainer animation", "animated stock chart", "earnings recap video", "whiteboard animation about money/finance", or similar.
user-invocable: true
argument-hint: <ticker-or-topic> [--kind price_line|candlestick|bar_comparison|kpi_counter|whiteboard_explainer]
---

# fin-anim

Turns financial data or concepts — live market data, a figure the user hands you, or
a concept to teach — into a short 2D Manim animation. This skill is the glue between
content and video: it does not fetch market data itself (that's whatever MCP tools or
user input are available in the session), and multi-scene compositing beyond one clip
is out of scope (hand off to `remotion` / `claude-code-video-toolkit` for that). It
does own narration for `whiteboard_explainer` specifically — see Step 1b.

## Scope

Five scene kinds, one per shape of financial story:

| Kind | Use for | Required data |
|---|---|---|
| `price_line` | A ticker/index/metric moving over time | `points`: list of `{date, value}` |
| `candlestick` | OHLC price action | `candles`: list of `{date, open, high, low, close}` |
| `bar_comparison` | Comparing labeled values (segments, regions, peers) | `bars`: list of `{label, value}` |
| `kpi_counter` | One number landing with a delta (revenue, EPS, growth %) | `kpi_label`, `kpi_value`, `kpi_delta_pct` |
| `whiteboard_explainer` | Teaching a financial concept, narrated, whiteboard-doodle style | `beats`: list of narrated beats — see Step 1b |

The first four are data-driven charts; `whiteboard_explainer` is concept-driven and
narrated (compound interest, inflation, diversification, budgeting, risk vs. reward —
not a specific ticker's numbers). If the request doesn't clearly map to one of these,
ask the user which shape fits rather than guessing — a wrong scene kind wastes a full
render cycle, and for `whiteboard_explainer` also a voiceover generation cycle.

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

Skip this step entirely for `whiteboard_explainer` — it's concept-driven, not a data
fetch. Go to Step 1b.

## Step 1b — `whiteboard_explainer` only: script it, narrate it, time it

This kind is different from the other four: instead of one data series, it's a short
script of 2–5 narrated "beats", each pairing one on-screen doodle with one spoken line.

1. **Write the script.** Break the concept into 2–5 beats. Each beat needs:
   - `narration` — the spoken line (a sentence or two, natural spoken English/whatever
     language the user wants narrated in).
   - `visual` — either `"text"` or one of the built-in icon names: `dollar`, `arrow_up`,
     `arrow_down`, `clock`, `house`, `piggy_bank`, `coin_stack`, `calculator`,
     `chart_bar`, `lightbulb`, `scale`. Pick the icon that matches the beat's idea (e.g.
     `piggy_bank` for saving, `clock` for time/growth, `scale` for risk vs. reward).
   - `label` — a short on-screen caption (a few words, NOT the full narration — the
     narration is heard, the label is a glance-able caption under the doodle).
2. **Generate narration audio per beat** with the `elevenlabs` skill, one audio file per
   beat (not one file for the whole script — each beat needs its own file so its
   duration can drive that beat's on-screen timing).
3. **Measure each clip's real duration** — do not estimate from word count, TTS pacing
   varies by voice/provider:
   ```bash
   python3 skills/fin-anim/scripts/audio_duration.py /path/to/beat_01.mp3
   ```
   Put the printed number straight into that beat's `duration` field, and the file path
   into `audio_path`.
4. If the user explicitly says no voiceover, leave `audio_path` empty and `duration` at
   a reasonable default (~3–4s per beat) — the scene still renders, just silent.

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

`whiteboard_explainer` example (see Step 1b for how `audio_path`/`duration` get filled):

```json
{
  "kind": "whiteboard_explainer",
  "title": "What Is Compound Interest?",
  "beats": [
    {
      "narration": "Compound interest means your money earns interest, and then that interest earns interest too.",
      "visual": "piggy_bank",
      "label": "Save $100",
      "audio_path": "/tmp/beat_01.mp3",
      "duration": 4.5
    },
    {
      "narration": "Over time, even small amounts grow much faster than you'd expect.",
      "visual": "clock",
      "label": "Time + Growth",
      "audio_path": "/tmp/beat_02.mp3",
      "duration": 4.0
    }
  ]
}
```

`data_loader.py` validates the file before rendering starts and fails fast with a
clear error if a required field for the chosen `kind` is missing — for
`whiteboard_explainer` specifically, that includes an unrecognized `visual` icon name
or a missing `label`. Read that error back to the user rather than retrying blindly.

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
- For the four data-chart kinds: narration/voiceover via the `elevenlabs` skill, if the
  user wants the clip narrated (`whiteboard_explainer` already includes this).
- Compositing multiple scenes, transitions, or branding into one video via `remotion`
  or the `claude-code-video-toolkit`, if the user wants more than a single clip.
- A different scene `kind` on the same content (e.g. also render the `kpi_counter`
  view of a stock move alongside its `price_line`; or a `whiteboard_explainer` beat
  that sets up a concept before a `price_line` shows the real numbers).

## Design notes for future scene kinds

Each scene is a self-contained `manim.Scene` subclass in `scripts/scenes/` with a
class-level `data: SceneData = None` slot — `build.py` sets `.data` on the instance
before calling `.render()`, since Manim's own CLI-style construction doesn't take
constructor arguments. Adding a sixth kind means: extend `SceneKind` and `SceneData`
in `schema.py`, add its required-field entry (and any kind-specific validation, like
`whiteboard_explainer`'s beat checks) in `data_loader.py`, add the scene class, and
register it in `SCENE_CLASSES` in `build.py`. Don't invent a second data format —
every scene reads from the same `SceneData`.

`whiteboard_explainer` specifically also has `scripts/scenes/whiteboard_assets.py`
(colors, the marker-cursor mobject, the doodle icon library, and the
draw-while-tracking-cursor helper) — adding a new doodle icon means adding one
`_icon_<name>()` builder there, registering it in `_ICON_BUILDERS`, and adding the same
name to `WHITEBOARD_ICONS` in `schema.py` (there's an assertion at import time that
these two lists match).
