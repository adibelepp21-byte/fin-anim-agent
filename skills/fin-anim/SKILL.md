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
   - `visual` — one of, **in this preference order**:
     - a built-in icon name (19 available): `dollar`, `arrow_up`, `arrow_down`, `clock`,
       `house`, `piggy_bank`, `coin_stack`, `calculator`, `chart_bar`, `lightbulb`,
       `scale`, `briefcase`, `credit_card`, `graduation_cap`, `handshake`, `umbrella`,
       `warning_triangle`, `bank`, `pie_chart` — drawn as vector shapes with the hand
       tracing each one's real path. Free, no generation step, no GPU, no environment
       to break — **this is the default and preferred path**. If none of these fit the
       concept, prefer adding a new one (see Design notes below) over reaching for
       `"image"`.
     - `"text"` — the `label` is handwritten by the same path-tracing hand.
     - `"svg"` — `svg_path` points to a vector illustration, loaded as an
       `SVGMobject` and path-traced shape-by-shape just like a built-in icon (no
       separate reveal technique needed — an SVG already carries real vector paths).
       **Second choice** for a richer **scene** with several composed elements (a
       person, an object, their interaction) in one beat:
       [undraw.co](https://undraw.co) is a free CC0 illustration library (no
       attribution required, no generation step, no credits, no environment
       dependency) with exactly this kind of multi-element scene as ready SVG
       files — download one, save it, and reference its path. `data_loader.py`
       fails fast if `svg_path` doesn't exist.
     - `"image"` — **optional/experimental, not the default.** `image_path` points to
       a PNG generated with `tools/colab_generate_icons.ipynb` (Stable Diffusion on
       Colab's free GPU). Only reach for this if the user explicitly wants to try
       AI-generated icons and accepts that Colab's environment has repeatedly broken
       across sessions (model repo takedowns, numpy/scipy/Pillow ABI conflicts — see
       the notebook's changelog for the specific fixes applied so far). Don't propose
       it as the solution for "I want a nicer icon" — propose a new built-in vector
       icon or an `"svg"` scene first. The image is revealed with a wipe, not
       path-traced (see `whiteboard_assets.py`'s docstring for why).
   - `label` — a short on-screen caption (a few words, NOT the full narration — the
     narration is heard, the label is a glance-able caption under the doodle). Required
     for every visual kind, including `"image"`/`"svg"`.

**The hand itself** defaults to the stylized vector sketch. `make_photo_hand_cursor()`
(a realistic hand-and-pencil PNG, also from `tools/colab_generate_icons.ipynb`) exists
and is auto-used if `assets/whiteboard_icons/hand.png` happens to be present, but per
the same decision above, don't proactively steer the user toward generating one —
it carries the same Colab-fragility tradeoff as `"image"` icons.
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
    },
    {
      "narration": "That's the real power of starting early.",
      "visual": "image",
      "image_path": "assets/whiteboard_icons/piggy_bank.png",
      "label": "Start Early",
      "audio_path": "/tmp/beat_03.mp3",
      "duration": 4.0
    },
    {
      "narration": "Two people shaking hands after a deal, for instance.",
      "visual": "svg",
      "svg_path": "assets/whiteboard_icons/handshake.svg",
      "label": "A Deal Made",
      "audio_path": "/tmp/beat_04.mp3",
      "duration": 4.5
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
- If a `whiteboard_explainer` beat's built-in icon doesn't quite fit the concept,
  the default move is adding a new vector icon (see Design notes below) or reaching
  for an `"svg"` scene from undraw.co — **not** the Colab notebook (see below).

## Generating custom icons via Colab — optional/experimental, not the default

`tools/colab_generate_icons.ipynb` runs Stable Diffusion on Colab's free GPU tier —
no paid API/MCP credits, which is why it exists at all. But after repeated,
different environment failures across sessions (the `runwayml/stable-diffusion-v1-5`
model repo being pulled from Hugging Face, a numpy/scipy ABI mismatch, then a Pillow
ABI mismatch from patching that fix), the user explicitly decided to de-prioritize
this path in favor of the always-reliable vector icons and `"svg"` scenes. Don't
proactively suggest the Colab route for "make this icon nicer" — only use it if the
user specifically asks to try AI-generated icons again, and set the expectation that
Colab's shared-environment dependency conflicts may need fresh debugging each time
(the notebook's changelog documents the fixes applied so far, but a new Colab base
image update could introduce another one). This session can prepare/edit the
notebook but cannot run it (no GPU here) — the user runs it themselves.

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
(colors, both hand mobjects — `make_hand_cursor()` vector and
`make_photo_hand_cursor()` photo — the vector doodle icon library (19 icons and
counting), the path-tracing helper used by vector icons/text/SVG scenes, and the
wipe-reveal helper for `"image"` PNGs) — adding a new built-in vector icon means
adding one `_icon_<name>()` builder there, registering it in `_ICON_BUILDERS`, and
adding the same name to `WHITEBOARD_ICONS` in `schema.py` (there's an assertion at
import time that these two lists match). **This is the preferred way to cover a new
concept** — free, instant, no environment risk. Adding a new *generated* icon (the
de-prioritized Colab path) doesn't touch any of that — just add its concept to
`ICON_CONCEPTS` in `tools/colab_generate_icons.ipynb`, generate it, and reference the
PNG via `visual: "image"`. A new `"svg"` scene needs
no code changes at all — just a saved `.svg` file and a beat referencing it.
