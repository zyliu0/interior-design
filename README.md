# interior-design

> Turn any interior — a phone snapshot, a hand sketch, a 3D model screenshot — into a photorealistic professional rendering, restyled to match reference images. Same walls, same camera angle, new soul.

A small, single-purpose skill for any AI host with native multi-modal image generation. Three curated reference styles, an inviolable master prompt that protects the room's spatial fidelity, and nothing else. No Python, no API keys, no environment probing — image generation is your host's job; this skill just orchestrates the prompt and the references.

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

## Where it runs

This skill works in any host with native multi-modal image generation:

- **Codex** — with the `imagegen` system skill installed.
- **Gemini app** — built in.
- **Any other agent host with an image-generation tool or sub-skill.**

It does **not** include a fallback for text-only hosts. If your host can't generate images, the skill will tell you so honestly and stop — it won't ask for API keys or try to install dependencies. That's a feature, not a bug: keeping the skill single-purpose means it's tiny, predictable, and never surprises you with infrastructure prompts.

## Built-in styles

| Style | Vibe |
|---|---|
| **European Contemporary** | Refined apartment energy — stone, brass, dark woods, plaster, considered decorative density. |
| **Modern Wabi-Sabi** | Limewashed plaster, undyed linen, hand-thrown ceramics, aged woods, muted earth tones, embraced imperfection. |
| **Warm Minimalism** | Soft neutrals, layered textiles, warm woods, diffuse natural light. Minimal but never cold. |

Each style folder under `references/styles/` holds 2–3 reference images. The model synthesizes across all of them rather than copying any single one. You can add your own style in about thirty seconds — see [Adding your own styles](#adding-your-own-styles).

## Installation

```bash
npx skills add zyliu0/interior-design
```

That's it. The [Skills CLI](https://skills.sh) auto-detects which AI host you have installed (Codex, Cursor, Claude Code, and 50+ others) and symlinks the skill into the right directory for each one. After it finishes, invoke `/interior-design` in your host or just say "restyle this room" and point at an image.

**Useful flags:**

```bash
# Install globally (user-level) instead of project-local
npx skills add zyliu0/interior-design -g

# Target specific agents only
npx skills add zyliu0/interior-design -a codex -a cursor

# Copy files instead of symlinking
npx skills add zyliu0/interior-design --copy

# Update later
npx skills update interior-design

# Remove
npx skills remove interior-design
```

Requirements: Node 18+. Discover more skills at [skills.sh](https://skills.sh).

### Manual install

If you'd rather not use the Skills CLI:

```bash
git clone https://github.com/zyliu0/interior-design.git ~/.claude/skills/interior-design
```

For Codex, swap the destination to `~/.codex/skills/interior-design`. For the Gemini app, paste the contents of `SKILL.md` into the app as a custom instruction.

## Usage

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
Agent: Generating...
       Output: /Users/me/Desktop/output/my-living-room-20260516-104522.png
```

The skill always asks for the style explicitly. It will never pick one for you from context or vibe words — pick it yourself in the question UI, or name an exact style id (`euro-contemporary`, `modern-wabi-sabi`, `warm-minimalism`) up front.

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

The prompt lives at `prompts/system.md`. Your host reads it verbatim and passes it to the image model. The inviolable rules — spatial fidelity, camera angle preservation, 2-point perspective, architectural respect — are deliberately phrased to override user direction. If you want to relax any of them (for example, allow camera-angle drift), edit that file. The user's optional prompt is always appended *below* the system prompt, marked as secondary.

## Troubleshooting

**"This host doesn't have image generation available"** — your host doesn't have a native image-gen tool or sub-skill. Switch to Codex (with `imagegen` installed), the Gemini app, or another multi-modal host.

**The skill rendered without asking which style** — that's a bug in your host's agent runtime (not the skill). The SKILL.md instructs the agent to always ask. Report it.

**The output looks like a different room** — the spatial-fidelity rules drifted. Try:
1. Re-running with a clearer raw image (better lighting, fewer occluding objects).
2. Adding a stronger user prompt: "preserve all visible windows and the wood floor pattern exactly."

**The output ignored my reference style** — too few reference images, or the references are too generic. Make sure your style folder has 2–3 complementary shots, not one. Add one with strong material close-ups.

## File structure

```
interior-design/
├── SKILL.md                          # routing logic + agent-facing flow
├── README.md                         # this file
├── LICENSE                           # MIT
│
├── prompts/
│   └── system.md                     # inviolable master system prompt
│
└── references/
    ├── styles.json                   # default style catalog
    └── styles/
        ├── euro-contemporary/        # 2–3 reference images per style
        ├── modern-wabi-sabi/
        └── warm-minimalism/
```

That's the whole repo. Five files, three style folders, nine reference images.

## License & credits

Code is MIT licensed — see [LICENSE](./LICENSE). Reference images are placeholders bundled for testing; bring your own for production use. See [Adding your own styles](#adding-your-own-styles).
