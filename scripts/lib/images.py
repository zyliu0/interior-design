from datetime import datetime
from pathlib import Path

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE_MB = 20


def validate_image(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a regular file: {path}")
    if path.suffix.lower() not in ALLOWED_EXTS:
        raise ValueError(
            f"Unsupported image format: {path.suffix} "
            f"(allowed: {sorted(ALLOWED_EXTS)})"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise ValueError(
            f"Image too large ({size_mb:.1f} MB > {MAX_SIZE_MB} MB): {path}"
        )


def output_path(raw_path: Path, out_dir: Path, provider: str, ext: str = "png") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    basename = raw_path.stem
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return out_dir / f"{basename}-{timestamp}-{provider}.{ext}"
