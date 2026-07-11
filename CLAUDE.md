# CLAUDE.md

## Project

fin-anim-agent — a Claude Code skill (`/fin-anim`) that turns financial data into
short 2D animated explainer videos using Manim. Repo: adibelepp21-byte/fin-anim-agent.

## Structure

- `skills/fin-anim/SKILL.md` — canonical skill spec; the agent reads this when the
  skill fires. This is the single source of truth for behavior — keep code and this
  file in sync.
- `skills/fin-anim/scripts/schema.py` — `SceneData` dataclass, the one data contract
  every scene kind and every data source must produce.
- `skills/fin-anim/scripts/data_loader.py` — loads a JSON file, validates it against
  `REQUIRED_FIELDS` for its `kind` before any rendering starts.
- `skills/fin-anim/scripts/scenes/` — one `manim.Scene` subclass per scene kind
  (`price_line`, `candlestick`, `bar_comparison`, `kpi_counter`). Each takes its data
  via a class-level `data: SceneData = None` slot set by `build.py`, not via
  `__init__`, since Manim's own scene construction doesn't accept constructor args.
- `skills/fin-anim/scripts/build.py` — CLI orchestrator: JSON data in, MP4 out.
- `examples/` — one valid data file per scene kind, used by both manual testing and
  `tests/test_schema_and_loader.py`.
- `tests/` — schema/validation tests only. Deliberately excludes Manim rendering (no
  `manim` import) so the suite stays fast and doesn't need ffmpeg/Cairo/Pango in CI.

## Commands

- `pip install -r requirements.txt` — install manim + pytest
- `pytest tests/ -v` — run the schema/validation test suite
- `python3 skills/fin-anim/scripts/build.py --data <file>.json --output out/<name>.mp4 --quality m` — render

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

- Never fabricate financial data — if live data isn't available and the user hasn't
  supplied numbers, ask; don't render a plausible-looking series.
- Keep `tests/` free of a `manim` import — rendering correctness is verified manually
  (`build.py` against `examples/`), not in the fast test suite. If manim rendering
  tests are added later, put them in a separate opt-in suite, not `tests/`.
- This skill only does data → animation. Voiceover and multi-scene compositing are
  explicitly out of scope — hand off to the `elevenlabs` / `remotion` skills instead
  of reimplementing that here.
