from pathlib import Path

from src.config import CATALOGUE_DIR, TYPE_CLASSES


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def recommend_outfit(prediction_result):
    predicted_style = prediction_result["predicted_style"]
    predicted_type = prediction_result["predicted_type"]

    style_folder = CATALOGUE_DIR / predicted_style

    if not style_folder.exists():
        return []

    recommendations = []

    for clothing_type in TYPE_CLASSES:
        if clothing_type == predicted_type:
            continue

        type_folder = style_folder / clothing_type

        if not type_folder.exists():
            continue

        image_path = _get_first_image(type_folder)

        if image_path is None:
            continue

        recommendations.append(
            {
                "type": clothing_type,
                "name": _format_item_name(predicted_style, clothing_type),
                "brand": "Catalogue Item",
                "image_url": _to_public_catalogue_url(image_path),
                "score": 1.0,
            }
        )

    return recommendations[:3]


def _get_first_image(folder: Path):
    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            return file_path

    return None


def _to_public_catalogue_url(image_path: Path):
    relative_path = image_path.relative_to(CATALOGUE_DIR)
    return "/catalogue/" + relative_path.as_posix()


def _format_item_name(style: str, clothing_type: str):
    readable_style = style.replace("_", " ").title()
    readable_type = clothing_type.replace("_", " ").title()

    return f"{readable_style} {readable_type}"