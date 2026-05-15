# interior-design

A host-agnostic Claude / Codex / Gemini skill that turns a raw interior image (sketch, photograph, or 3D screenshot) into a photorealistic professional interior rendering, restyled to match reference images.

## Quick start

Invoke the skill from any compatible host:

```
/interior-design
```

The skill will ask you for:

1. **Raw image** — the space you want restyled (sketch, photo, or 3D screenshot).
2. **Style** — pick one of the built-in styles or upload your own reference.
3. **Optional second reference** — another image to influence the style.
4. **Optional prompt** — any extra direction ("evening light", "add a velvet chair", etc.).

The output lands in `./output/` next to your raw image, named `<basename>-<timestamp>.png`.

## Built-in styles

- **European Contemporary** — refined apartment style, stone + brass + dark woods.
- **Modern Wabi-Sabi** — limewashed plaster, undyed linen, aged wood, muted earth tones.
- **Warm Minimalism** — soft neutrals, layered textiles, warm woods, diffuse natural light.

Each style folder under `references/styles/` holds 2–3 reference images. Drop your own to add a style — add an entry to `references/styles.json` with the same `id` slug as the folder.

## How it routes

- **Mode A (native, preferred)** — if your host can generate images directly (Codex, Gemini app, any multi-modal agent with image-gen tools), the skill composes the prompt and uses the host's own tool. Zero config, no API keys.
- **Mode B (API fallback)** — for hosts that can't generate images (Claude Code, text-only Cursor sessions), the skill shells out to `scripts/render.py` which calls Gemini Image 3.0 or OpenAI's `gpt-image-2`. First run prompts for an API key and saves it to `.env`.

## Mode B setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add one or both keys:
#   https://aistudio.google.com/apikey   (Gemini)
#   https://platform.openai.com/api-keys (OpenAI)
```

Manual invocation of the renderer:

```bash
python scripts/render.py \
  --raw ~/photos/living-room.jpg \
  --ref references/styles/warm-minimalism/1.jpg \
  --ref references/styles/warm-minimalism/2.jpg \
  --ref references/styles/warm-minimalism/3.jpg \
  --provider gemini \
  --user-prompt "warm evening light, brass accents" \
  --out-dir ~/photos/output
```

## Inviolable rules

The master system prompt (`prompts/system.md`) tells the model to:

- Respect the raw image's spatial layout exactly — no walls/windows/doors moved.
- Respect the raw image's camera angle — same viewpoint and framing.
- Render in 2-point perspective.
- Use references for style only, never for layout.

Your optional prompt is appended as **secondary** direction below these rules — it can guide style choices but cannot override the spatial fidelity rules.

## Files

```
SKILL.md                    # routing logic + agent flow
PLAN.md                     # development plan
prompts/system.md           # inviolable master system prompt
references/styles.json      # default style catalog
references/styles/<id>/     # 2–3 reference images per style
scripts/render.py           # Mode B CLI (Phase 3)
```
