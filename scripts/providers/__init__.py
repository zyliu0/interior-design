from pathlib import Path
from typing import Protocol


class ImageProvider(Protocol):
    """Common interface for image-generation providers."""

    def render(
        self,
        prompt: str,
        raw_image_path: Path,
        reference_paths: list[Path],
    ) -> bytes:
        """Return PNG bytes for the generated image."""
        ...
