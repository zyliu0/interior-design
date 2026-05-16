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

## Step 0 — Mode detection (work the ladder top-to-bottom)

The goal is to use the host's native image generation whenever it exists, and only fall back to the API path when nothing else is wired up. **Do not stop at the first failed check.** Many hosts expose image generation through a *skill* rather than a directly-visible tool — our previous "scan your tool list and bail" logic missed those and incorrectly fell through to API mode. Walk this ladder:

### A. Delegate to a host `imagegen` skill (preferred)

Many hosts ship an `imagegen` skill that knows how to invoke their native image-generation primitive. Check these paths for an existing `SKILL.md`:

```
~/.codex/skills/.system/imagegen/SKILL.md
~/.codex/skills/imagegen/SKILL.md
~/.agents/skills/imagegen/SKILL.md
~/.claude/skills/imagegen/SKILL.md
./.agents/skills/imagegen/SKILL.md
```

A quick way to check:

```bash
for p in ~/.codex/skills/.system/imagegen ~/.codex/skills/imagegen ~/.agents/skills/imagegen ~/.claude/skills/imagegen ./.agents/skills/imagegen; do [ -f "$p/SKILL.md" ] && echo "FOUND: $p/SKILL.md"; done
```

If one is found, **read its `SKILL.md`** to learn its input format, then plan to use it in Step 5a. This path is the most robust because the `imagegen` skill handles tool-name plumbing, feature-flag detection, and host quirks for you.

### B. Direct image-gen tool in your tool list

Scan your currently visible tools for an image-generation primitive. Tool names vary by host — try at least: `image_gen`, `image_generation`, `generate_image`, `imagegen`, `create_image`. If you have a tool-search capability (e.g. `ToolSearch` in Claude Code), also query for those names — the tool may be deferred and load on demand.

If any callable tool surfaces, plan to use it directly in Step 5a.

### C. Host advertises image gen but tool is hidden

On Codex, run `codex features list`. If it shows `image_generation stable true` but rungs A and B both came up empty, **do not silently fall back to API mode** — that's the bug this section is fixing. Surface the contradiction to the user:

> "Your host advertises image generation as enabled, but no callable tool is exposed in this session and no `imagegen` skill is installed at the expected paths (`~/.codex/skills/.system/imagegen/`, etc.). Options: (1) install one with `npx skills add vercel-labs/skills --skill imagegen`, then re-run me; (2) fall back to API mode if you have a Gemini or OpenAI key in `.env`."

Wait for the user to choose. Do not auto-fall-through.

### D. Mode B (API fallback)

Only after A, B, and C are all confirmed unavailable: route to Mode B and shell out to `scripts/render.py`. This is the path that requires an API key.

**Bias:** if you're unsure whether you have native image gen, lean Mode A — try it. The previous version of this skill defaulted to Mode B on uncertainty, which caused users to be asked for unnecessary API keys when their host could already do the work.

## Step 1 — Collect inputs (identical in both modes)

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

## Step 5a — Render (Mode A: native)

Use whichever rung of Step 0 you landed on:

### If you chose A (delegate to a host `imagegen` skill)

1. Read the imagegen skill's `SKILL.md` if you haven't already, to learn its input contract.
2. Invoke it with:
   - The composed prompt from Step 3 as the text prompt.
   - The image list from Step 4, in that exact order (raw first, then style references, then any user-supplied slot-2 image).
3. Capture the resulting image. Save to `<raw_dir>/output/<raw_basename>-<ISO_timestamp>.png`.

### If you chose B (direct image-gen tool)

Invoke the tool directly with:

- The composed prompt from Step 3 (as the text prompt).
- The image list from Step 4, in that exact order.

Save the returned image to `<raw_dir>/output/<raw_basename>-<ISO_timestamp>.png`.

### Output handling (both A and B)

- Create the `output/` directory if it doesn't exist.
- Use the timestamp format `YYYYMMDD-HHMMSS` (filesystem-safe).
- If the tool returns image bytes, write them directly.
- If the tool returns inline-only (no path, no bytes), explicitly ask the host to also save the image to the output path before continuing.

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
