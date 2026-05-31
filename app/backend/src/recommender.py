import torch

from src.clip_service import encode_image
from src.config import TYPE_CLASSES


_EMBEDDINGS_PATH = "data/catalogue_embeddings.pt"
_catalogue_records = None


def recommend_outfit(prediction_result, input_image=None):
    predicted_style = prediction_result["predicted_style"]
    predicted_type = prediction_result["predicted_type"]

    if input_image is None:
        return []

    input_embedding = encode_image(input_image).squeeze(0)

    records = _load_catalogue_records()

    recommendations = []

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

        best_record, best_score = _find_best_candidate(input_embedding, candidates)

        recommendations.append(
            {
                "type": clothing_type,
                "name": _format_item_name(predicted_style, clothing_type),
                "brand": "Catalogue Item",
                "image_url": "/catalogue/" + best_record["path"],
                "score": round(float(best_score), 4),
            }
        )

    return recommendations[:3]


def _load_catalogue_records():
    global _catalogue_records

    if _catalogue_records is not None:
        return _catalogue_records

    _catalogue_records = torch.load(
        _EMBEDDINGS_PATH,
        map_location="cpu",
        weights_only=False,
    )

    return _catalogue_records


def _find_best_candidate(input_embedding, candidates):
    best_record = None
    best_score = -1.0

    for record in candidates:
        candidate_embedding = record["embedding"]

        score = torch.nn.functional.cosine_similarity(
            input_embedding.unsqueeze(0),
            candidate_embedding.unsqueeze(0),
        ).item()

        if score > best_score:
            best_score = score
            best_record = record

    return best_record, best_score


def _format_item_name(style: str, clothing_type: str):
    readable_style = style.replace("_", " ").title()
    readable_type = clothing_type.replace("_", " ").title()

    return f"{readable_style} {readable_type}"