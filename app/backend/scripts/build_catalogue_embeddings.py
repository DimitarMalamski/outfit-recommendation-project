import sys
from pathlib import Path

import torch
from PIL import Image

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[3]

sys.path.append(str(BACKEND_DIR))

from src.clip_service import encode_image  # noqa: E402
from src.config import CATALOGUE_DIR  # noqa: E402


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

OUTPUT_PATH = BACKEND_DIR / "data" / "catalogue_embeddings.pt"


def main():
    records = []

    image_paths = [
        path
        for path in CATALOGUE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    print(f"Found {len(image_paths)} catalogue images.")

    for index, image_path in enumerate(image_paths, start=1):
        try:
            image = Image.open(image_path).convert("RGB")
            embedding = encode_image(image).squeeze(0)

            relative_path = image_path.relative_to(CATALOGUE_DIR)
            parts = relative_path.parts

            style = parts[0]
            clothing_type = parts[1]

            records.append(
                {
                    "path": relative_path.as_posix(),
                    "style": style,
                    "type": clothing_type,
                    "embedding": embedding.cpu(),
                }
            )

            print(f"[{index}/{len(image_paths)}] Embedded {relative_path}")

        except Exception as error:
            print(f"Skipped {image_path}: {error}")

    torch.save(records, OUTPUT_PATH)

    print(f"Saved {len(records)} embeddings to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()