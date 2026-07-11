# assets/whiteboard_icons/

Assets for `whiteboard_explainer`, all generated or sourced for free (no paid API/MCP
credits):

## Doodle icons (`"image"` visual mode)

PNGs from `tools/colab_generate_icons.ipynb` (local Stable Diffusion on Colab's free
GPU). Generate the set (or add new icon names to `ICON_CONCEPTS` in the notebook
first), download `whiteboard_icons.zip` from the last cell, unzip it, and drop the
PNGs in here. Reference one from a beat:

```json
{"visual": "image", "image_path": "assets/whiteboard_icons/piggy_bank.png", "label": "Save $100", ...}
```

These PNGs are revealed with a left-to-right wipe (`reveal_image_with_hand` in
`skills/fin-anim/scripts/scenes/whiteboard_assets.py`), not vector path-traced like the
built-in primitive icons — see that file's module docstring for why.

`example_placeholder.png` is a plain PIL-drawn stand-in (not AI-generated), committed
so the `"image"` mode has a runnable example without requiring the Colab step first.

## Realistic hand (`hand.png`)

Also from `tools/colab_generate_icons.ipynb` (its hand section, near the end). If
`hand.png` exists here, every beat's render uses it automatically in place of the
default stylized vector hand — no per-beat setting. See the notebook's calibration
cell if the pencil tip doesn't track quite right (`DEFAULT_PHOTO_HAND_TIP_FRACTION` in
`whiteboard_assets.py`).

## SVG scenes (`"svg"` visual mode)

Multi-element vector illustrations (a person + an object + their interaction),
traced shape-by-shape by the hand exactly like a built-in icon — real vector paths,
not a raster wipe. [undraw.co](https://undraw.co) is a free CC0 source (no
attribution required): download an SVG, save it here, reference it:

```json
{"visual": "svg", "svg_path": "assets/whiteboard_icons/handshake.svg", "label": "A Deal Made", ...}
```

`example_scene.svg` is a small hand-authored placeholder (not from unDraw) proving
the multi-element tracing mechanism — swap in a real illustration when ready.
