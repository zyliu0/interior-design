# interior-design

> Turn any interior — a phone snapshot, a hand sketch, a 3D model screenshot — into a photorealistic professional rendering, restyled to match reference images. Same walls, same camera angle, new soul.

A host-agnostic skill for Claude Code, Codex, Gemini app, and any other multi-modal AI agent. The skill ships with three curated reference styles, an inviolable master prompt that protects the room's spatial fidelity, and an optional Python fallback for hosts that can't generate images natively.

## What it does

Feed it three things:

1. **A raw image** — your room. Could be a phone photo, a SketchUp screenshot, a napkin sketch.
2. **A style** — pick one of the built-ins (European Contemporary, Modern Wabi-Sabi, Warm Minimalism) or drop in your own reference photos.
3. **Optional direction** — "evening light", "leather sofa, brass lamps", whatever you want to layer on.

You get back a photorealistic rendering of *your* room in the chosen style. Walls don't move. Windows stay where they are. The camera angle is preserved. Only the materials, palette, furniture, and lighting change.

The master prompt enforces this. The model is told, in language it cannot override: *the raw image dictates space, the references dictate style.*

## Quick start

```
/interior-design
```

The skill asks for your raw image, the style, an optional second reference, and any extra direction. The output lands in `./output/` next to your raw image as `<basename>-<timestamp>.png`.

## How it works

The skill auto-routes based on what your host can do.

**Mode A — Native (preferred, zero config).** If your host has a built-in image-generation tool — Codex with image gen, the Gemini app, future multi-modal agents — the skill hands the composed prompt and reference images directly to that tool. No API keys, no Python, nothing to install beyond the skill files.

**Mode B — API fallback.** If your host is text-only (Claude Code today, Cursor with most text models, plain LLM CLIs), the skill shells out to `scripts/render.py`, which calls either **Gemini 3.1 Flash Image Preview** or **OpenAI gpt-image-2** over HTTPS. First run prompts for an API key and saves it to `.env` so you only enter it once.

You don't have to think about which mode you're in. The skill detects it.

## Built-in styles

| Style | Vibe |
|---|---|
| **European Contemporary** | Refined apartment energy — stone, brass, dark woods, plaster, considered decorative density. |
| **Modern Wabi-Sabi** | Limewashed plaster, undyed linen, hand-thrown ceramics, aged woods, muted earth tones, embraced imperfection. |
| **Warm Minimalism** | Soft neutrals, layered textiles, warm woods, diffuse natural light. Minimal but never cold. |

Each style folder under `references/styles/` holds 2–3 reference images. The model synthesizes across all of them rather than copying any single one. You can add your own style in about thirty seconds — see [Adding your own styles](#adding-your-own-styles).

## Installation

### Option 1 — One-line install via npx (recommended)

```bash
npx github:zyliu0/interior-design
```

That's it. The skill is installed to `~/.claude/skills/interior-design` and ready to use. Invoke `/interior-design` in Claude Code or just say "restyle this room" and point at an image.

Other targets:

```bash
# Install to a Codex skills directory
npx github:zyliu0/interior-design --codex

# Install to a custom path
npx github:zyliu0/interior-design --target ~/my-skills/interior-design

# Overwrite an existing install
npx github:zyliu0/interior-design --force
```

Requirements: Node 18+. No npm publish, no global install — npx runs the installer directly from this GitHub repo.

### Option 2 — Manual git clone

If you'd rather not run a script:

```bash
git clone https://github.com/zyliu0/interior-design.git ~/.claude/skills/interior-design
```

For Codex, swap the destination to `~/.codex/skills/interior-design`. For the Gemini app, paste the contents of `SKILL.md` into the app as a custom instruction.

### Option 3 — Run as a standalone Python tool

If you just want the renderer without any AI host wrapper:

```bash
git clone https://github.com/zyliu0/interior-design.git
cd interior-design
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and paste in at least one API key. See [Mode B setup](#mode-b-setup-api-keys) below.

### Mode B setup (API keys)

Mode B is only needed when your host can't generate images itself. If you're in Claude Code, you'll hit this.

You need **one or both** of these keys:

- **Gemini** (recommended, cheaper): https://aistudio.google.com/apikey
- **OpenAI**: https://platform.openai.com/api-keys

Open `.env` and paste them in:

```bash
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
DEFAULT_PROVIDER=gemini
```

`DEFAULT_PROVIDER` is only consulted when both keys are present. Otherwise the skill uses whichever key it finds.

Then install the Python deps if you haven't already:

```bash
pip install -r requirements.txt
```

Requirements: Python 3.9+, `google-genai`, `openai`, `pillow`, `python-dotenv`.

### Verify the install

Run a dry-run — no API call, no key needed, just confirms the wiring works:

```bash
cd ~/.claude/skills/interior-design   # or wherever you cloned it
python3 scripts/render.py \
  --raw references/styles/warm-minimalism/1.jpg \
  --ref references/styles/warm-minimalism/2.jpg \
  --ref references/styles/warm-minimalism/3.jpg \
  --provider gemini \
  --user-prompt "warm evening light" \
  --dry-run
```

You should see the composed prompt, the image list in order, and the resolved output directory. If you see that, you're good.

## Usage

### Through the skill (Claude Code, Codex, etc.)

```
You: /interior-design
Agent: Where's the raw image?
You:   ~/Desktop/my-living-room.jpg
Agent: Which style?
       1) European Contemporary
       2) Modern Wabi-Sabi
       3) Warm Minimalism
       4) Upload my own
You:   2
Agent: Any second reference? (skip with enter)
You:   (enter)
Agent: Any extra direction? (skip with enter)
You:   evening, brass floor lamp
Agent: Rendering...
       Output: /Users/me/Desktop/output/my-living-room-20260516-104522.png
```

### Direct Python (Mode B only)

```bash
python3 scripts/render.py \
  --raw ~/photos/living-room.jpg \
  --ref references/styles/modern-wabi-sabi/1.jpg \
  --ref references/styles/modern-wabi-sabi/2.jpg \
  --ref references/styles/modern-wabi-sabi/3.jpg \
  --provider gemini \
  --user-prompt "morning light, ceramic vase on the table" \
  --out-dir ~/photos/output
```

Outputs land at `~/photos/output/living-room-<timestamp>-gemini.png`. The script prints the absolute output path on its last stdout line — handy for piping into `open` on macOS:

```bash
open "$(python3 scripts/render.py ... | tail -1)"
```

### CLI reference

```
render.py
  --raw          PATH     required, the raw image (spatial source)
  --ref          PATH     repeatable, reference image(s) (style source)
  --provider     gemini|openai
  --user-prompt  TEXT     optional secondary direction
  --out-dir      DIR      default: <raw_dir>/output
  --dry-run              compose + validate without calling the API
```

## Adding your own styles

About thirty seconds:

```bash
mkdir references/styles/japandi
cp ~/Desktop/japandi-{1,2,3}.jpg references/styles/japandi/
```

Then append an entry to `references/styles.json`:

```json
{
  "id": "japandi",
  "name": "Japandi",
  "folder": "japandi",
  "description": "Japanese restraint meets Scandinavian warmth — light wood, natural fibers, low decorative density."
}
```

That's it. The skill picks it up on the next invocation.

**Image guidelines:**
- 2–3 images per style. More signal, more reliable style transfer.
- 1024–1536px on the long edge, under 2 MB.
- Pick complementary shots, not three near-duplicates: one wide hero, one material close-up, optionally one with different lighting.
- JPG is fine. PNG if you have transparency.

## Tweaking the master prompt

The prompt lives at `prompts/system.md`. Both modes read it verbatim. The inviolable rules — spatial fidelity, camera angle preservation, 2-point perspective, architectural respect — are deliberately phrased to override user direction. If you want to relax any of them (for example, allow camera-angle drift), edit that file. The user's optional prompt is always appended *below* the system prompt, marked as secondary.

A practical workflow: when output quality drifts, iterate on `prompts/system.md` against a real raw image in Mode A (free) before paying for Mode B renders.

## Troubleshooting

**`ERROR: Image not found`** — the path doesn't exist or isn't readable. Check spelling and shell expansion (`~` doesn't always expand inside quotes).

**`ERROR: Image too large (X MB > 20 MB)`** — downscale with Pillow, ImageMagick, or your photo app. The 20 MB cap is enforced before any API call to fail fast.

**`ERROR: GEMINI_API_KEY not set` / `OPENAI_API_KEY not set`** — Mode B couldn't find a key. Either:
- `.env` is missing → `cp .env.example .env` and add a key.
- `.env` exists but the key is empty → check there's no whitespace around the `=`.
- Running from a directory where `.env` isn't found → the script looks for `.env` in the skill root, not your CWD.

**`ERROR: SDK not installed`** — `pip install -r requirements.txt` from the skill directory.

**The output looks like a different room** — the spatial-fidelity rules drifted. Try:
1. Re-running with a clearer raw image (better lighting, fewer occluding objects).
2. Adding a stronger user prompt: "preserve all visible windows and the wood floor pattern exactly."
3. Switching providers — Gemini and gpt-image-2 weight prompts differently.

**The output ignored my reference style** — too few reference images, or the references are too generic. Make sure your style folder has 2–3 complementary shots, not one. Add one with strong material close-ups.

## File structure

```
interior-design/
├── SKILL.md                          # routing logic + agent-facing flow
├── README.md                         # this file
├── LICENSE                           # MIT
├── PLAN.md                           # development plan and history
├── package.json                      # npx installer manifest
├── cli.mjs                           # npx installer script
├── requirements.txt                  # Python deps for Mode B
├── .env.example                      # API key template
├── .gitignore                        # ignores .env, output/, __pycache__/
│
├── prompts/
│   └── system.md                     # inviolable master system prompt
│
├── references/
│   ├── styles.json                   # default style catalog
│   └── styles/
│       ├── euro-contemporary/        # 3 reference images per style
│       ├── modern-wabi-sabi/
│       └── warm-minimalism/
│
└── scripts/                          # Mode B (API fallback)
    ├── render.py                     # CLI entry
    ├── lib/
    │   ├── prompt.py                 # load + compose prompt
    │   └── images.py                 # validation + output paths
    └── providers/
        ├── gemini.py                 # gemini-3.1-flash-image-preview
        └── openai.py                 # gpt-image-2 via images.edit
```

## License & credits

Code is MIT licensed — see [LICENSE](./LICENSE). Reference images are placeholders bundled for testing; bring your own for production use. See [Adding your own styles](#adding-your-own-styles).
