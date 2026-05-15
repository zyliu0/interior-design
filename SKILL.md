---
name: interior-design
description: |
  Turn a raw interior image (sketch, photograph, or 3D screenshot) into a
  photorealistic professional interior rendering, restyled to match
  reference images. Three default styles included (European Contemporary,
  Modern Wabi-Sabi, Warm Minimalism); user can also upload their own
  reference. Use when the user wants to redesign, restyle, or re-render
  an interior space. Triggers: "redesign this room", "restyle this
  interior", "make this look [style]", "interior render", "interior
  design from this photo", "wabi-sabi this room", "warm minimal this".
---

# Interior Design Skill

Generate a photorealistic interior rendering from a raw image + style references. Host-agnostic: runs natively when the host can generate images, falls back to a Gemini / OpenAI API call otherwise.

## Step 0 — Mode detection (do this first, before asking anything)

Scan your own tool list. Do you have a tool **right now** that accepts text + one or more input images and returns a generated image? (Tool names vary by host — `image_generation`, `generate_image`, a built-in image tool, etc.)

- **Yes, or you're not sure** → **Mode A (native)**. You will use your own image-gen tool. Skip the API-key sections below.
- **Confirmed no** (you scanned your tool list and there is nothing for image generation) → **Mode B (API fallback)**. You will shell out to `scripts/render.py`.

**Mode A is preferred. Try it first.** If the native call errors with "tool not available" or similar, fall through to Mode B.

## Step 1 — Collect inputs (identical in both modes)

Use the host's question UI (e.g. `AskUserQuestion`) to gather:

1. **Raw image path** — required. The image of the space to be restyled (sketch, photo, or 3D screenshot).
2. **Style choice** — present these options, reading the current list from `references/styles.json`:
   - European Contemporary (`euro-contemporary`)
   - Modern Wabi-Sabi (`modern-wabi-sabi`)
   - Warm Minimalism (`warm-minimalism`)
   - "Upload my own" — if chosen, ask for a file path to a custom reference image.
3. **Optional second reference path** — leave blank to skip.
4. **Optional user prompt** — any additional direction (e.g. "warm evening lighting", "add a leather sofa"). Leave blank to skip.

Validate each path exists and points to a readable image file before proceeding. If invalid, surface a clear error and ask again.

## Step 2 — Load the system prompt

Read `prompts/system.md` in this skill directory **verbatim**. This is the inviolable master prompt — never modify or summarize it.

## Step 3 — Compose the final prompt

```
<contents of prompts/system.md, verbatim>

---
ADDITIONAL USER DIRECTION (secondary to all rules above):
<user prompt>
```

If the user didn't provide a secondary prompt, omit the `---` block entirely.

## Step 4 — Resolve reference image paths

- If a **default style** was chosen: look up its `folder` in `references/styles.json` and glob `references/styles/<folder>/*.{jpg,jpeg,png,webp}` to gather all style reference images (typically 2–3).
- If **"Upload my own"** was chosen: use the single user-provided path as the style reference.
- Append the optional **slot-2** user reference (if provided) to the end of the list.

Final image list for the call, in this exact order:

1. Raw image (spatial source) — always first.
2. Style reference(s) — 1–3 images from the chosen style folder, or the user's slot-1 upload.
3. Optional slot-2 user reference (if provided).

## Step 5a — Render (Mode A: native)

Invoke your native image-generation tool with:

- The composed prompt from Step 3 (as the text prompt).
- The image list from Step 4, in that exact order.

Save the returned image to `<raw_dir>/output/<raw_basename>-<ISO_timestamp>.png`. Create the `output/` directory if it doesn't exist. Strip filesystem-unsafe characters from the timestamp (use `YYYYMMDD-HHMMSS`).

If the tool returns image bytes, write them directly. If it returns inline-only, ask the host to also save to the path.

## Step 5b — Render (Mode B: API fallback)

1. Look for `.env` in this skill directory. Load `GEMINI_API_KEY`, `OPENAI_API_KEY`, `DEFAULT_PROVIDER`.
2. If **neither** key is set, explain to the user:
   > "This host doesn't have native image generation, so the skill needs an API key. Get one from https://aistudio.google.com/apikey (Gemini, recommended — cheaper) or https://platform.openai.com/api-keys (OpenAI). The key will be saved to `.env` so you only enter it once."

   Then ask which provider they want, prompt for the key, and write it to `.env`.
3. Pick the provider:
   - Only one key set → use that.
   - Both keys set → use `DEFAULT_PROVIDER` if set; otherwise ask once and save the choice to `.env`.
4. Ensure Python deps are installed: `pip install -r requirements.txt` (only first time).
5. Run:

   ```bash
   python scripts/render.py \
     --raw <raw_path> \
     --ref <ref_path_1> [--ref <ref_path_2> ...] \
     --provider <gemini|openai> \
     --user-prompt "<secondary text, or omit>" \
     --out-dir <raw_dir>/output
   ```

   Pass each reference image as its own `--ref` flag.
6. The script prints the absolute output path on its last stdout line. Capture it.

## Step 6 — Report

Print the absolute output path to the user. On macOS, offer:

```
open <path>
```

If `--provider both` would be useful (user wants side-by-side from Gemini and gpt-image-2), invoke Step 5b twice with different providers and report both paths.

---

## File map

- `prompts/system.md` — inviolable master system prompt.
- `references/styles.json` — list of default styles and their folders.
- `references/styles/<id>/` — 2–3 reference images per style.
- `scripts/render.py` — Mode B CLI entry (Phase 3 deliverable).
- `.env` — API keys (gitignored, never commit).
- `PLAN.md` — development plan.
- `README.md` — human-facing usage doc.
