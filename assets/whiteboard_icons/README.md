# assets/whiteboard_icons/

PNG doodle icons for `whiteboard_explainer`'s `"image"` visual mode, generated for
free with `tools/colab_generate_icons.ipynb` (local Stable Diffusion on Colab's free
GPU — no paid API/MCP credits).

Generate the set (or add new icon names to `ICON_CONCEPTS` in the notebook first),
download `whiteboard_icons.zip` from the last cell, unzip it, and drop the PNGs in
here. Reference one from a beat:

```json
{"visual": "image", "image_path": "assets/whiteboard_icons/piggy_bank.png", "label": "Save $100", ...}
```

These PNGs are revealed with a left-to-right wipe (`reveal_image_with_hand` in
`skills/fin-anim/scripts/scenes/whiteboard_assets.py`), not vector path-traced like the
built-in primitive icons — see that file's module docstring for why.
