import torch

from src.clip_service import encode_image
from src.config import TYPE_CLASSES

CATALOGUE_EMBEDDINGS_PATH = "data/catalogue_embeddings.pt"
_catalogue_records = None


def recommend_outfit(prediction_result, input_image=None):
    predicted_style = prediction_result["predicted_style"]
    predicted_type = prediction_result["predicted_type"]

    if input_image is None:
        return {
            "recommendations": [],
            "outfits": [],
        }

    input_embedding = encode_image(input_image).squeeze(0)
    records = _load_catalogue_records()

    candidates_by_type = {}

    for clothing_type in TYPE_CLASSES:
        if clothing_type == predicted_type:
            continue

        candidates = [
            record
            for record in records
            if record["style"] == predicted_style and record["type"] == clothing_type
        ]

        if not candidates:
            continue

        ranked_candidates = _rank_candidates(input_embedding, candidates)
        candidates_by_type[clothing_type] = ranked_candidates[:3]

    outfits = _build_outfits(predicted_style, candidates_by_type)

    return {
        "recommendations": outfits[0]["items"] if outfits else [],
        "outfits": outfits,
    }

def recommend_replacement_item(
    target_type: str,
    predicted_style: str,
    input_image=None,
    exclude_image_urls=None,
):
    if exclude_image_urls is None:
        exclude_image_urls = []

    if input_image is None:
        return None

    input_embedding = encode_image(input_image).squeeze(0)
    records = _load_catalogue_records()

    excluded_paths = set()

    for image_url in exclude_image_urls:
        cleaned_path = image_url.replace("/catalogue/", "")
        excluded_paths.add(cleaned_path)

    candidates = [
        record
        for record in records
        if record["style"] == predicted_style
        and record["type"] == target_type
        and record["path"] not in excluded_paths
    ]

    if not candidates:
        return None

    ranked_candidates = _rank_candidates(input_embedding, candidates)

    record, score = ranked_candidates[0]

    return {
        "type": target_type,
        "name": _format_item_name(predicted_style, target_type),
        "brand": "Catalogue Item",
        "image_url": "/catalogue/" + record["path"],
        "score": round(float(score), 4),
    }


def _load_catalogue_records():
    global _catalogue_records

    if _catalogue_records is not None:
        return _catalogue_records

    _catalogue_records = torch.load(
        CATALOGUE_EMBEDDINGS_PATH,
        map_location="cpu",
        weights_only=False,
    )

    return _catalogue_records


def _rank_candidates(input_embedding, candidates):
    ranked = []

    for record in candidates:
        candidate_embedding = record["embedding"]

        score = torch.nn.functional.cosine_similarity(
            input_embedding.unsqueeze(0),
            candidate_embedding.unsqueeze(0),
        ).item()

        ranked.append((record, score))

    ranked.sort(key=lambda item: item[1], reverse=True)

    return ranked


def _build_outfits(predicted_style, candidates_by_type):
    outfits = []

    for outfit_index in range(3):
        outfit_items = []

        for clothing_type, ranked_candidates in candidates_by_type.items():
            if outfit_index >= len(ranked_candidates):
                continue

            record, score = ranked_candidates[outfit_index]

            outfit_items.append(
                {
                    "type": clothing_type,
                    "name": _format_item_name(predicted_style, clothing_type),
                    "brand": "Catalogue Item",
                    "image_url": "/catalogue/" + record["path"],
                    "score": round(float(score), 4),
                }
            )

        if outfit_items:
            outfits.append(
                {
                    "name": f"Outfit {outfit_index + 1}",
                    "items": outfit_items[:3],
                }
            )

    return outfits


def _format_item_name(style: str, clothing_type: str):
    readable_style = style.replace("_", " ").title()
    readable_type = clothing_type.replace("_", " ").title()

    return f"{readable_style} {readable_type}"