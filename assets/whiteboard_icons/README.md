# assets/whiteboard_icons/

Assets for `whiteboard_explainer`, all free (no paid API/MCP credits).

## SVG scenes (`"svg"` visual mode) — preferred for multi-element scenes

Multi-element vector illustrations (a person + an object + their interaction),
traced shape-by-shape by the hand exactly like a built-in icon — real vector paths,
no generation step, no environment dependency. [undraw.co](https://undraw.co) is a
free CC0 source (no attribution required): download an SVG, save it here, reference
it:

```json
{"visual": "svg", "svg_path": "assets/whiteboard_icons/handshake.svg", "label": "A Deal Made", ...}
```

`example_scene.svg` is a small hand-authored placeholder (not from unDraw) proving
the multi-element tracing mechanism — swap in a real illustration when ready.

For a single concept, check the 19-icon built-in vector library in
`skills/fin-anim/scripts/scenes/whiteboard_assets.py` first — it's free and
instant, with no file to source or generate.

## Doodle icons (`"image"` visual mode) — optional/experimental

PNGs from `tools/colab_generate_icons.ipynb` (local Stable Diffusion on Colab's free
GPU). **De-prioritized as of the notebook breaking three different ways across
sessions** (a model repo pulled from Hugging Face, then a numpy/scipy ABI conflict,
then a Pillow one) — the built-in vector icons and SVG scenes above are the default
now. Still here for anyone who wants to keep trying it: generate the set (or add new
icon names to `ICON_CONCEPTS` in the notebook first), download
`whiteboard_icons.zip` from the last cell, unzip it, and drop the PNGs in here.
Reference one from a beat:

```json
{"visual": "image", "image_path": "assets/whiteboard_icons/piggy_bank.png", "label": "Save $100", ...}
```

These PNGs are revealed with a left-to-right wipe (`reveal_image_with_hand` in
`skills/fin-anim/scripts/scenes/whiteboard_assets.py`), not vector path-traced like the
built-in primitive icons — see that file's module docstring for why.

`example_placeholder.png` is a plain PIL-drawn stand-in (not AI-generated), committed
so the `"image"` mode has a runnable example without requiring the Colab step first.

## Realistic hand (`hand.png`) — optional/experimental

Same status as doodle icons above. Also from `tools/colab_generate_icons.ipynb` (its
hand section, near the end). If `hand.png` exists here, every beat's render uses it
automatically in place of the default stylized vector hand — no per-beat setting. See
the notebook's calibration cell if the pencil tip doesn't track quite right
(`DEFAULT_PHOTO_HAND_TIP_FRACTION` in `whiteboard_assets.py`).
