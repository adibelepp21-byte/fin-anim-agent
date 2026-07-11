# CLAUDE.md

## Project

fin-anim-agent — a Claude Code skill (`/fin-anim`) that turns financial data and
concepts into short 2D animated videos using Manim. Repo:
adibelepp21-byte/fin-anim-agent.

## Structure

- `skills/fin-anim/SKILL.md` — canonical skill spec; the agent reads this when the
  skill fires. This is the single source of truth for behavior — keep code and this
  file in sync.
- `skills/fin-anim/scripts/schema.py` — `SceneData` dataclass, the one data contract
  every scene kind and every data source must produce. Also holds `WHITEBOARD_ICONS`
  (the canonical icon-name list) and `WhiteboardBeat`.
- `skills/fin-anim/scripts/data_loader.py` — loads a JSON file, validates it against
  `REQUIRED_FIELDS` for its `kind` before any rendering starts, plus kind-specific
  checks (e.g. `whiteboard_explainer` beats: known icon name or `"image"` with an
  `image_path` that actually exists on disk, non-empty `label`).
- `skills/fin-anim/scripts/scenes/` — one `manim.Scene` subclass per scene kind
  (`price_line`, `candlestick`, `bar_comparison`, `kpi_counter`,
  `whiteboard_explainer`). Each takes its data via a class-level
  `data: SceneData = None` slot set by `build.py`, not via `__init__`, since Manim's
  own scene construction doesn't accept constructor args.
- `skills/fin-anim/scripts/scenes/whiteboard_assets.py` — colors, `make_hand_cursor()`
  (the stylized hand-and-pen mobject), the vector doodle icon library (one
  `_icon_<name>()` builder per icon, all built from Manim primitives — no external
  SVG/image assets), `draw_icon_with_hand()` (flattens a vector/text beat's visual into
  its leaf shapes and draws them one at a time with the hand's pen tip tracing each
  leaf's own `point_from_proportion(alpha)` path), and `reveal_image_with_hand()` (wipes
  a raster `"image"` PNG into view instead, since it has no vector path to trace).
  Imports manim, so it stays out of `tests/` (see Rules).
- `skills/fin-anim/scripts/build.py` — CLI orchestrator: JSON data in, MP4 out.
- `skills/fin-anim/scripts/audio_duration.py` — thin `ffprobe` wrapper; measures a
  narration clip's real duration so `whiteboard_explainer` beats can be timed to their
  voiceover instead of guessed from word count.
- `tools/colab_generate_icons.ipynb` — generates `assets/whiteboard_icons/*.png` for
  free on Colab's GPU tier (local Stable Diffusion via `diffusers`, no paid API/MCP
  credits). This session can edit the notebook but cannot run it (no GPU in this
  environment) — the user runs it on Colab and downloads the PNGs themselves.
- `assets/whiteboard_icons/` — generated PNGs, referenced by beats with
  `visual: "image"` and `image_path` pointing here.
- `examples/` — one valid data file per scene kind, used by both manual testing and
  `tests/test_schema_and_loader.py`.
- `tests/` — schema/validation tests only. Deliberately excludes Manim rendering (no
  `manim` import) so the suite stays fast and doesn't need ffmpeg/Cairo/Pango in CI.

## Commands

- `pip install -r requirements.txt` — install manim + pytest
- `pytest tests/ -v` — run the schema/validation test suite
- `python3 skills/fin-anim/scripts/build.py --data <file>.json --output out/<name>.mp4 --quality m` — render
- `python3 skills/fin-anim/scripts/audio_duration.py <file>.mp3` — print a clip's duration in seconds

## Conventions

- Python 3.10+, type hints, dataclasses for data shapes (no pydantic dependency —
  keep this skill's own footprint light; heavier validation libs belong in whatever
  calls into it, not in the render pipeline itself).
- Every scene reads from the same `SceneData` shape. Do not invent a second data
  format for a new scene kind — extend the existing one.
- `build.py` and every module under `scripts/scenes/` use **absolute imports**
  (`from schema import SceneData`, not `from .schema import SceneData`). This only
  resolves correctly when `build.py` is invoked by its full/relative path (e.g.
  `python3 skills/fin-anim/scripts/build.py ...`) — Python adds that file's own
  directory to `sys.path`, which is what lets sibling modules resolve regardless of
  the caller's cwd. Don't switch to relative imports without also adding `__init__.py`
  package plumbing and a different invocation story (`python3 -m ...`).
- Commit format: `type(scope): message` (e.g. `feat(scenes): add pie_chart kind`)

## Rules

- Never fabricate financial data or narration — if live data isn't available and the
  user hasn't supplied numbers, ask; don't render a plausible-looking series. Same for
  `whiteboard_explainer` scripts: don't invent a "fact" about compound interest etc.
  that wasn't asked for or verified.
- Keep `tests/` free of a `manim` import — rendering correctness is verified manually
  (`build.py` against `examples/`), not in the fast test suite. If manim rendering
  tests are added later, put them in a separate opt-in suite, not `tests/`. This is
  why `WHITEBOARD_ICONS` lives in `schema.py` (manim-free) rather than being derived
  from `whiteboard_assets.py` (which imports manim) — `data_loader.py` needs to
  validate icon names without pulling manim into the test suite.
- For the four data-chart kinds, voiceover and multi-scene compositing stay out of
  scope — hand off to the `elevenlabs` / `remotion` skills. `whiteboard_explainer` is
  the one exception: it owns per-beat narration generation (via `elevenlabs`) and
  timing (via `audio_duration.py`) as part of its own workflow (SKILL.md Step 1b),
  because the animation's pacing is *derived from* the voiceover, not layered on
  after — that's not "reimplementing elevenlabs", it's using its output as timing
  input.
- The whiteboard hand traces each leaf shape's real path (`point_from_proportion`) —
  it is not a bounding-box sweep. What IS still a deliberate simplification: the hand
  itself is a stylized sketch (fist + 3 fingers + thumb + pen, all Manim primitives),
  not an anatomically detailed illustration, and the doodle icons are primitive shapes,
  not illustrated assets. Both are documented in `whiteboard_assets.py`'s module
  docstring — don't "fix" them reflexively as if they were bugs.
- `draw_icon_with_hand` divides `total_run_time` evenly across however many leaf shapes
  a beat's visual flattens into (an icon's shapes AND a Text label's individual glyph
  paths both count as leaves). A short caption on a multi-part icon reads as
  deliberate handwriting; a long caption can end up with a very small per-glyph
  `run_time` and look like a fast scribble — keep beat `label`s to a few words (already
  the rule per SKILL.md) rather than compensating for this in the renderer.
- Icon generation is local-and-free (`tools/colab_generate_icons.ipynb` on Colab's free
  GPU tier), by explicit user decision — not a paid MCP image-generation tool. Don't
  reintroduce an MCP/API generation path for whiteboard icons without asking first;
  this was chosen specifically to avoid recurring per-call credits for what's meant to
  be a repeatable YouTube content pipeline. `"image"` beats using a wipe reveal instead
  of path-tracing is the accepted tradeoff for this (a raster PNG has no vector path to
  trace) — not a bug to unify with the vector path either.
