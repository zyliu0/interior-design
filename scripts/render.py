#!/usr/bin/env python3
"""interior-design renderer (Mode B fallback).

Calls Gemini 3.1 Flash Image Preview or OpenAI gpt-image-2 with a raw image,
style reference images, and a composed prompt. Saves the result as a PNG.

The last line of stdout is the absolute output path — the calling agent
parses that. All human-readable info goes to stderr.

Exit codes:
  0 — success
  2 — bad input (missing/invalid image, bad args)
  3 — provider API call failed
  4 — missing or invalid API key
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="render.py",
        description="interior-design Mode B renderer (Gemini / OpenAI fallback).",
    )
    p.add_argument(
        "--raw", required=True, type=Path,
        help="Raw image (spatial source).",
    )
    p.add_argument(
        "--ref", required=True, action="append", type=Path, dest="ref",
        help="Reference image (style source). Repeat for multiple.",
    )
    p.add_argument(
        "--provider", required=True, choices=["gemini", "openai"],
    )
    p.add_argument(
        "--user-prompt", default=None,
        help="Optional secondary user direction.",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help="Output directory (default: <raw_dir>/output).",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print composed prompt + image list without calling the API.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    # Make sibling packages importable when run as a script.
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from lib.prompt import compose, load_system_prompt
    from lib.images import output_path, validate_image

    # Load .env from skill root.
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass  # python-dotenv optional — fall back to plain env vars

    # Validate inputs.
    try:
        validate_image(args.raw)
        for ref in args.ref:
            validate_image(ref)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Compose prompt.
    system_prompt = load_system_prompt()
    final_prompt = compose(system_prompt, args.user_prompt)

    # Dry-run: print, don't call.
    if args.dry_run:
        print("=== composed prompt ===", file=sys.stderr)
        print(final_prompt, file=sys.stderr)
        print("=== image list (in order) ===", file=sys.stderr)
        print(f"  raw : {args.raw}", file=sys.stderr)
        for i, ref in enumerate(args.ref, 1):
            print(f"  ref{i}: {ref}", file=sys.stderr)
        print(f"=== provider : {args.provider} ===", file=sys.stderr)
        out_dir = args.out_dir or (args.raw.parent / "output")
        print(f"=== out_dir  : {out_dir} ===", file=sys.stderr)
        return 0

    # Instantiate provider (lazy import — no SDK needed for dry-run).
    try:
        if args.provider == "gemini":
            from providers.gemini import GeminiProvider
            provider = GeminiProvider()
        else:
            from providers.openai import OpenAIProvider
            provider = OpenAIProvider()
    except RuntimeError as e:
        print(
            f"ERROR: {e}. Add it to .env (see .env.example) or set it in the environment.",
            file=sys.stderr,
        )
        return 4
    except ImportError as e:
        print(
            f"ERROR: SDK not installed: {e}. Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 4

    # Render.
    print(f"Rendering with {args.provider}...", file=sys.stderr)
    try:
        image_bytes = provider.render(
            prompt=final_prompt,
            raw_image_path=args.raw,
            reference_paths=list(args.ref),
        )
    except Exception as e:
        print(f"ERROR: {args.provider} render failed: {e}", file=sys.stderr)
        return 3

    # Save.
    out_dir = args.out_dir or (args.raw.parent / "output")
    out = output_path(args.raw, out_dir, args.provider)
    out.write_bytes(image_bytes)

    # Last line of stdout = absolute output path (the agent parses this).
    print(out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
