from __future__ import annotations

import os
from pathlib import Path

MODEL = "gemini-3.1-flash-image-preview"


class GeminiProvider:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY not set")
        from google import genai  # lazy import
        self._genai = genai
        self.client = genai.Client(api_key=key)

    def render(
        self,
        prompt: str,
        raw_image_path: Path,
        reference_paths: list[Path],
    ) -> bytes:
        from google.genai import types  # lazy import
        from PIL import Image  # lazy import

        # Raw first (spatial source), then references (style sources).
        images = [Image.open(raw_image_path)]
        for ref in reference_paths:
            images.append(Image.open(ref))

        response = self.client.models.generate_content(
            model=MODEL,
            contents=[prompt, *images],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                inline = getattr(part, "inline_data", None)
                if inline and inline.data:
                    return inline.data

        raise RuntimeError(
            "Gemini returned no image data. "
            "Check that the model id is current and the prompt was accepted."
        )
