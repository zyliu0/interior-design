from __future__ import annotations

import base64
import os
from pathlib import Path

MODEL = "gpt-image-2"
SIZE = "1024x1024"


class OpenAIProvider:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        from openai import OpenAI  # absolute import resolves to top-level SDK
        self.client = OpenAI(api_key=key)

    def render(
        self,
        prompt: str,
        raw_image_path: Path,
        reference_paths: list[Path],
    ) -> bytes:
        # gpt-image-2 accepts up to 16 input images. Raw first (spatial),
        # then references (style).
        all_paths = [raw_image_path, *reference_paths]

        handles = [open(p, "rb") for p in all_paths]
        try:
            result = self.client.images.edit(
                model=MODEL,
                image=handles,
                prompt=prompt,
                size=SIZE,
                output_format="png",
            )
        finally:
            for h in handles:
                h.close()

        if not result.data or not result.data[0].b64_json:
            raise RuntimeError("OpenAI returned no image data")

        return base64.b64decode(result.data[0].b64_json)
