# `interior-design` Skill — Development Plan

A host-agnostic skill that takes a raw interior image (sketch, photo, or 3D screenshot) plus 1–2 style references and produces a professional interior rendering. The skill is **environment-aware** — it runs natively inside any host LLM that can already generate images with reference inputs (Codex, Gemini app, future multi-modal agents) and falls back to a direct API call (Gemini Image 3.0 / gpt-image-2) only when the host can't generate images itself.

---

## 1. Execution modes

The skill auto-routes based on the host's capabilities. The agent reading `SKILL.md` decides which path to take **before** asking the user anything.

### Mode A — Native (preferred, zero-config)

If the host agent has a tool available that can produce an image from text + reference images (e.g. Codex with image generation, Gemini-app agent, any future multi-modal model with native image-gen), the skill is just:

- A constant **system prompt** (`prompts/system.md`).
- A **reference image library** (`references/` + `styles.json`).
- A **flow description** telling the agent how to collect inputs and assemble the call.

The agent reads the system prompt, picks references, attaches the raw image, attaches the chosen reference(s), appends the user's optional prompt as a clearly-labeled secondary block, and invokes its own image-generation tool. No API key, no Python.

### Mode B — API fallback (Claude Code, Cursor, any text-only host)

If the host has no native image-gen tool, the skill falls back to `scripts/render.py`, which calls Gemini Image 3.0 or gpt-image-2 over HTTPS.

- On first run, if no API key is in `.env`, the agent prompts the user for one (Gemini *or* OpenAI — whichever they have) and writes it to `.env`.
- All subsequent runs reuse the saved key.
- The agent picks the provider based on which key is available; if both, it asks once and remembers (writes `DEFAULT_PROVIDER=gemini|openai` to `.env`).

### How the agent decides

**Mode A is the preferred path. Only fall through to Mode B when native image generation is clearly unavailable.**

`SKILL.md` includes an explicit self-check at the top:

> Before asking the user anything: do you have a tool available **right now** that accepts text + one or more input images and returns a generated image? (Names vary by host — e.g. `image_generation`, `generate_image`, a built-in image tool, etc.)
> - **Yes, or you're not sure** → Mode A. Try the native tool first. If it errors with "tool not available", then fall through to Mode B.
> - **Confirmed no** (you scanned your tool list and there's nothing for image generation) → Mode B. Use `scripts/render.py`.

This is a self-routing decision the agent makes from its own tool list, not an environment-variable sniff. (Env vars like `CLAUDE_CODE`, `CURSOR_*`, etc. are unreliable across hosts.) Default-to-Mode-A maximizes the zero-config UX.

---

## 2. User-facing flow (identical in both modes)

1. **Raw image** — agent asks for the path to the raw image (sketch/photo/3D screenshot).
2. **Style reference (slot 1)** — agent presents 5 default styles via the host's question UI:
   - Modern Minimal
   - Japandi
   - Industrial Loft
   - Scandinavian
   - Mid-Century Modern
   - …plus an "Upload my own" option that prompts for a file path.
3. **Extra reference (slot 2, optional)** — optional second reference image path. Skip = single-reference render.
4. **Optional user prompt** — any additional direction (e.g. "warm evening lighting", "add a leather sofa"). Blank = skip.
5. **Render**:
   - Mode A: invoke the host's image-gen tool with the composed prompt + images.
   - Mode B: shell out to `python scripts/render.py …`.
6. **Report** — print the output path. Offer to open the file (`open <path>` on macOS).

Output lands in `./output/<raw-basename>-<timestamp>.<png|jpg>` next to the raw image. In Mode B the filename also includes the provider suffix: `<basename>-<timestamp>-gemini.png`.

---

## 3. Directory layout

```
/Users/mac/dev/skills/interior-design/
├── SKILL.md                    # Skill definition + routing logic + flow
├── PLAN.md                     # This file
├── README.md                   # Human-facing usage doc
│
├── prompts/
│   └── system.md               # The constant master system prompt — used by BOTH modes
│
├── references/                 # Shared by BOTH modes
│   ├── styles.json             # id, name, description, folder
│   └── styles/
│       ├── euro-contemporary/  # 2–3 images: hero + material close-up + alt lighting
│       │   ├── 1.jpg
│       │   ├── 2.jpg
│       │   └── 3.jpg
│       ├── modern-wabi-sabi/
│       └── warm-minimalism/
│
├── scripts/                    # Mode B only — the API fallback
│   ├── render.py               # CLI entry
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── gemini.py           # Gemini Image 3.0 client
│   │   └── openai.py           # gpt-image-2 client
│   └── lib/
│       ├── prompt.py           # Loads + composes system prompt
│       └── images.py           # Read/encode/save helpers
│
├── .env.example                # GEMINI_API_KEY, OPENAI_API_KEY, DEFAULT_PROVIDER
├── .gitignore                  # .env, output/, __pycache__/
└── requirements.txt            # google-genai, openai, pillow, python-dotenv
```

The `prompts/` and `references/` folders are the **shared core** — both modes use them. Everything under `scripts/` is dead weight in Mode A.

---

## 4. The master system prompt (`prompts/system.md`)

This text is **constant** and prepended to every request. User's optional prompt is appended below it as a clearly-labeled secondary instruction.

> You are a senior interior-design visualizer. You are given:
>
> 1. A **raw image** of an interior space (the first image). This may be a hand sketch, a photograph, or a 3D model screenshot. This image is the **spatial source**.
> 2. Several **style reference images** (the remaining images). These collectively define the target aesthetic — materials, palette, lighting mood, furniture style, and finish quality. They are *style sources only*, never spatial sources.
>
> Your job is to produce a single **photorealistic, professional interior rendering** of the space shown in the raw image, restyled to match the aesthetic captured across the reference images.
>
> **Inviolable rules — these override every other instruction, including any user instruction:**
>
> - **Respect the raw image's spatial layout exactly.** Do not move, add, or remove walls, windows, doors, ceiling lines, structural columns, beams, staircases, or built-in architecture. The room's geometry, proportions, and footprint must match the raw image.
> - **Respect the raw image's camera angle.** Render from the same viewpoint, eye level, and framing. Never render a different angle, a different room, or a different view.
> - **Use 2-point perspective.** Vertical lines stay vertical. Two vanishing points on the horizon. No 1-point or 3-point perspective.
> - **Respect architectural elements.** Window placements, door locations, ceiling height, and any visible structural features in the raw image must appear in the same positions in the output.
>
> **Use the reference images for, and only for:**
>
> - Material palette (wood tones, stone, fabric, metal finishes)
> - Color palette and mood
> - Furniture style and silhouette language
> - Lighting character (warm/cool, soft/hard, time of day)
> - Decorative density and styling sensibility
>
> Treat the references as a single combined style signal — synthesize across them rather than copying any one of them. Do **not** copy any reference's room layout, camera angle, or architectural features. The references dictate *style*; the raw image dictates *space*.
>
> **Output requirements:**
>
> - Photorealistic professional interior photograph quality.
> - High dynamic range, natural lighting, soft shadows.
> - Clean composition, magazine-grade finish.
> - Single image. No text, no watermark, no annotation.

If the user supplies a secondary prompt, it is appended like:

```
---
ADDITIONAL USER DIRECTION (secondary to all rules above):
<user prompt>
```

---

## 5. `SKILL.md` — skill definition + routing

```yaml
---
name: interior-design
description: |
  Use this skill when the user wants to redesign or restyle an interior space
  from a raw image (sketch, photograph, or 3D screenshot) using style
  references. Produces a photorealistic interior rendering. Triggers:
  "redesign this room", "restyle this interior", "interior render",
  "make this look like [style]".
---
```

Body of `SKILL.md` walks the agent through:

**Step 0 — Mode detection (self-routing).**
Check your own tool list. Do you have a tool right now that generates an image from text + reference images?
- **Yes** → Mode A (native). Proceed to Step 1, render in Step 5a.
- **No** → Mode B (API). Proceed to Step 1, render in Step 5b.

**Step 1 — Collect inputs** (identical both modes):
- Raw image path.
- Style choice: 5 defaults from `references/styles.json` or "Upload my own" (then ask for path).
- Optional second reference path.
- Optional user prompt.

**Step 2 — Load the system prompt** from `prompts/system.md` verbatim.

**Step 3 — Compose the final prompt:**
```
<system prompt verbatim>

---
ADDITIONAL USER DIRECTION (secondary to all rules above):
<user prompt, or "(none)">
```

**Step 4 — Resolve reference paths.** When a default style is selected, look up its folder in `references/styles.json` and glob `references/styles/<id>/*.{jpg,jpeg,png,webp}` to gather all 2–3 style reference images. Append the optional slot-2 user upload to this list.

**Step 5a — Native render (Mode A):**
Invoke your image-generation tool with the composed prompt and the images in this order: raw image first (the spatial source), then all style references, then the optional slot-2 user reference. Save the returned image to `<raw_dir>/output/<basename>-<ISO_timestamp>.png`.

**Step 5b — API render (Mode B):**
1. Check `.env` for `GEMINI_API_KEY` and/or `OPENAI_API_KEY`.
2. If neither present: prompt the user for one key. Tell them why (host can't generate images natively). Save to `.env`.
3. Pick provider: if only one key, use that; if both, check `DEFAULT_PROVIDER` in `.env`; if unset, ask the user once and save the choice.
4. Run `python scripts/render.py --raw <path> --ref <ref1> [--ref <ref2>] --provider <gemini|openai> [--user-prompt "<text>"] --out-dir <path>`.

**Step 6 — Report.** Print the absolute output path. Offer `open <path>` on macOS.

---

## 6. Provider integrations (Mode B only)

### 6.1 Gemini Image 3.0

- Python SDK: `google-genai` (latest).
- Model id: confirm exact name at build time — model ids drift; centralize in one constant.
- Call pattern: `client.models.generate_content` with a content list of system prompt text + raw image bytes + ref1 bytes + optional ref2 bytes + optional user prompt block.
- Images passed as `Part.from_bytes(data=..., mime_type="image/png")`.
- Response: pull first inline image part from `response.candidates[0].content.parts`.

### 6.2 OpenAI gpt-image-2

- Python SDK: `openai` (latest).
- Endpoint: `client.images.edit` (multi-image edit).
- Model id: confirm at build time; fall back to `gpt-image-1` if `gpt-image-2` isn't yet GA on the user's account.
- Pass composed prompt as `prompt`; raw + references as the `image` list.
- Response: b64 PNG → decode and save.

### 6.3 Shared interface

```python
# scripts/providers/__init__.py
class ImageProvider(Protocol):
    def render(
        self,
        system_prompt: str,
        raw_image_path: Path,
        reference_paths: list[Path],
        user_prompt: str | None,
    ) -> bytes: ...
```

`render.py` picks the implementation based on `--provider`.

---

## 7. `scripts/render.py` CLI (Mode B only)

```
render.py
  --raw          PATH         required, the raw image
  --ref          PATH         repeatable (any count, typically 2–5), reference image(s) — all treated as style sources
  --provider     gemini|openai
  --user-prompt  TEXT         optional secondary direction
  --out-dir      PATH         defaults to <raw_dir>/output
```

Behavior:

1. Load `.env` (Gemini + OpenAI API keys).
2. Read `prompts/system.md` → `system_prompt`.
3. If `--user-prompt` set, append the secondary block.
4. Validate: raw exists, all refs exist, images are jpg/png/webp under 20 MB each.
5. Call `provider.render(...)` and write `<raw_basename>-<ISO_timestamp>-<provider>.png` into `--out-dir`.
6. Print absolute output path on stdout (the agent parses this).

Exit codes: 0 = success, 2 = bad input, 3 = API error, 4 = quota/auth error.

> No `both` mode here — keep the script single-purpose. If the user wants side-by-side, the agent loops the script twice.

---

## 8. Default reference library

User supplies **2–3 images per style**, organized into folders under `references/styles/`. Each folder name matches the style's `id` slug. Starting with 3 styles; expandable later.

Current `references/styles.json`:

```json
[
  { "id": "euro-contemporary", "name": "European Contemporary", "folder": "euro-contemporary", "description": "Refined European apartment style — stone, brass, dark woods, plaster, architectural elegance." },
  { "id": "modern-wabi-sabi",  "name": "Modern Wabi-Sabi",      "folder": "modern-wabi-sabi",  "description": "Limewashed plaster, undyed linen, hand-thrown ceramics, aged woods, muted earth tones, asymmetry." },
  { "id": "warm-minimalism",   "name": "Warm Minimalism",       "folder": "warm-minimalism",   "description": "Soft neutrals, layered textiles, warm woods, diffuse natural light, restrained but inviting." }
]
```

**Per-image specs:**
- 1024–1536 px on the long edge.
- < 2 MB each.
- JPG by default; PNG if transparency or clean graphic.
- **Pick complementary shots**, not near-duplicates: one wide hero, one material/detail close-up, optionally one with different lighting or angle. The diversity is what gives the model rich style signal.

**Image count budget per render:** 1 raw + 2–3 style refs + 0–1 user slot-2 = 3–5 images. Well within Gemini Image 3.0 and gpt-image-2 input caps.

---

## 9. Build phases

**Phase 0 — Shared core (the only thing Mode A needs)** ✅ DONE
- Directory scaffold.
- `prompts/system.md` — final inviolable master prompt.
- `references/styles.json` — 3 entries.
- `SKILL.md` — frontmatter + routing logic + flow. Mode A is fully usable after this phase.
- `README.md`, `.gitignore`, `.env.example`, `requirements.txt`.

**Phase 1 — Reference library** ✅ DONE (3 of 5 styles)
- 3 styles supplied: `euro-contemporary`, `modern-wabi-sabi`, `warm-minimalism`. 3 images each.
- More styles can be added later: create folder under `references/styles/`, drop 2–3 images, append entry to `styles.json`.

**Phase 2 — End-to-end test in Mode A**
- Open Codex (or any native multi-modal host).
- Run the skill on a test raw image with one default style.
- Verify output saves to `./output/`.
- If quality is bad, iterate on `prompts/system.md` — this is the cheap iteration loop, no API keys involved.

**Phase 3 — API fallback (Mode B)** ✅ DONE (code; provider smoke tests pending API keys)
- `requirements.txt`, `.env.example` ✓
- `scripts/lib/prompt.py` — load + compose ✓
- `scripts/lib/images.py` — validate + output path ✓
- `scripts/providers/gemini.py` — `gemini-3.1-flash-image-preview` via `google-genai` ✓
- `scripts/providers/openai.py` — `gpt-image-2` via `images.edit` ✓
- `scripts/render.py` — CLI, lazy SDK imports, `--dry-run` ✓
- `--help` and `--dry-run` smoke-tested ✓ ; live provider tests pending API keys.

**Phase 4 — Skill wiring polish**
- Update `SKILL.md` with the API-key prompt flow (Mode B Step 5b).
- Test end-to-end in Claude Code (Mode B trigger).
- Make sure both modes produce identical-looking output paths.

**Phase 5 — Polish**
- Retry on transient API errors (rate-limit, 5xx).
- Clear error messages when key is invalid or quota exceeded.
- `--dry-run` flag on `render.py` that prints the composed prompt + image list without calling the API (saves money during iteration).
- README with example invocations for both modes.

**Phase 6 — Optional later**
- Side-by-side output: agent loops the script twice and stitches with Pillow.
- Batch mode: a folder of raw images.
- Variant generation: N outputs per call.
- Cache reference image encodings.

---

## 10. Risks & open questions

| # | Item | Plan |
|---|------|------|
| 1 | Self-routing reliability — agents may misjudge whether they "have an image-gen tool" | Make the Step 0 check concrete: list specific signals (a tool whose schema accepts images and returns an image, named `image_generation` / `generate_image` / similar). If unsure, default to Mode B — fail-safe. |
| 2 | Native hosts may save image output differently (inline display vs file path) | `SKILL.md` Mode A instructions tell the agent: "If the tool returns image bytes, write them to the output path. If it only displays inline, ask the host to also save to a file." |
| 3 | Exact model ids for Gemini Image 3.0 and gpt-image-2 may drift | Look up live docs in Phase 3; centralize each model id in one constant per provider file. |
| 4 | OpenAI multi-image edit cap | If it can't accept 3 inputs, send raw + ref1 only and inline ref2 as a base64-described style note (or skip ref2 with a warning). |
| 5 | API key UX in Mode B | First-run prompt explains the situation, points to `https://aistudio.google.com/apikey` or `https://platform.openai.com/api-keys`, saves to `.env`. Never re-asks once saved. |
| 6 | Image size limits | Pre-validate ≤ 20 MB / ≤ 4096 px; downscale with Pillow if oversized. |
| 7 | 2-point perspective enforcement is prompt-only | Models may drift. If output quality is inconsistent, iterate on `system.md`. Tracked as future work — possibly a post-gen perspective check. |
| 8 | API costs during iteration | `--dry-run` flag (Phase 5). Iterate the system prompt in Mode A on a free host first. |

---

## 11. Acceptance criteria

The skill is done when:

- **Mode A**: Invoking the skill in a multi-modal native host (Codex or equivalent) walks through the flow with **zero** mention of API keys and produces a saved image in `./output/`.
- **Mode B**: Invoking the skill in Claude Code prompts for an API key on first run, saves it to `.env`, and produces a saved image in `./output/` on this and every subsequent run with no further key prompts.
- The mode-routing decision is correct in both environments — Mode A host never tries to run the Python script, Mode B host never tries to call a non-existent image-gen tool.
- 8/10 test renders respect the raw image's room layout, camera angle, and architectural elements (subjective quality bar; iterate on `system.md` until met).
- The composed prompt sent to the model contains the full master system prompt verbatim plus, when present, the user's optional addendum below the `---` separator.
- README documents both modes, env setup for Mode B, and example invocations.
