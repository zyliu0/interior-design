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

Generate a photorealistic interior rendering from a raw image plus style references. This skill is pure prompt + reference orchestration. Image generation is the host's job — the skill does not check capabilities, install dependencies, or run any code of its own.

## Step 1 — Collect inputs

Use the host's question UI (e.g. `AskUserQuestion`) to gather each input below. **Hard rule: never guess or auto-fill any input the user did not explicitly name.** If a value isn't in the user's original message, you ask. Always.

1. **Raw image path** — required. The image of the space to be restyled (sketch, photo, or 3D screenshot). Ask if not supplied.

2. **Style choice — REQUIRED. NEVER PICK A STYLE FOR THE USER.**

   You MUST present the question UI with the available styles UNLESS the user has *explicitly* named a specific style in their original message — by exact id (`euro-contemporary`, `modern-wabi-sabi`, `warm-minimalism`) or by exact name ("European Contemporary", "Modern Wabi-Sabi", "Warm Minimalism").

   The following are NOT explicit style choices and MUST trigger the question UI:
   - Vibe words: "cozy", "elegant", "modern", "warm", "minimal", "Japanese", "European".
   - Inferences from the raw image's content, lighting, or existing furniture.
   - Defaults of any kind (no "first style", no "most popular", no random pick).
   - The user saying "you choose" or "pick whatever" — even then, ask, then let them confirm.

   When you ask, present these options, reading the current list from `references/styles.json`:
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

## Step 5 — Generate the image

Invoke whatever image-generation capability your host provides (native tool, sub-skill, image-gen API call — whatever exists in your environment) with:

- The composed prompt from Step 3 as the text prompt.
- The image list from Step 4, in that exact order.

Save the returned image to `<raw_dir>/output/<raw_basename>-<YYYYMMDD-HHMMSS>.png`. Create the `output/` directory if it doesn't exist.

If your host has no image-generation capability, **tell the user honestly**: "This host doesn't have image generation available. Run this skill in a host with native multi-modal image gen (Codex, Gemini app, etc.)." Do not attempt fallbacks. Do not ask for API keys. Do not install anything.

## Step 6 — Report

Print the absolute output path to the user. On macOS, offer:

```
open <path>
```

---

## File map

- `prompts/system.md` — inviolable master system prompt.
- `references/styles.json` — list of default styles and their folders.
- `references/styles/<id>/` — 2–3 reference images per style.
- `README.md` — human-facing usage doc.
- `LICENSE` — MIT.
