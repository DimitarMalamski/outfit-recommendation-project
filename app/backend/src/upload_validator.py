import torch
from fastapi import HTTPException
from PIL import Image

from src.clip_service import encode_image, encode_text_prompts


CLIP_MIN_SUPPORTED_SCORE = 0.18
CLIP_UNSUPPORTED_MARGIN = 0.02


SUPPORTED_PROMPTS = [
    ("jacket", "a clear product photo of a jacket"),
    ("jacket", "a photo of a coat or jacket"),
    ("jacket", "a single jacket on a plain background"),

    ("pants", "a clear product photo of pants"),
    ("pants", "a photo of trousers or pants"),
    ("pants", "a single pair of pants on a plain background"),

    ("shoes", "a clear product photo of shoes"),
    ("shoes", "a photo of sneakers or shoes"),
    ("shoes", "a single pair of shoes on a plain background"),

    ("tshirt", "a clear product photo of a t-shirt"),
    ("tshirt", "a photo of a shirt or t-shirt"),
    ("tshirt", "a single t-shirt on a plain background"),
]


UNSUPPORTED_PROMPTS = [
    ("animal", "a photo of an animal"),
    ("cat", "a photo of a cat"),
    ("dog", "a photo of a dog"),

    ("person", "a photo of a person"),
    ("selfie", "a selfie photo"),
    ("full_outfit", "a photo of a person wearing a full outfit"),

    ("bag", "a photo of a bag"),
    ("hat", "a photo of a hat"),
    ("dress", "a photo of a dress"),
    ("skirt", "a photo of a skirt"),
    ("watch", "a photo of a watch"),
    ("sunglasses", "a photo of sunglasses"),

    ("phone", "a photo of a phone"),
    ("laptop", "a photo of a laptop"),
    ("car", "a photo of a car"),
    ("food", "a photo of food"),
    ("room", "a photo of a room"),
    ("landscape", "a landscape photo"),
]


_supported_prompt_embeddings = None
_unsupported_prompt_embeddings = None


def validate_clip_supported_garment(image: Image.Image):
    image_embedding = encode_image(image).squeeze(0)

    supported_embeddings = _get_supported_prompt_embeddings()
    unsupported_embeddings = _get_unsupported_prompt_embeddings()

    supported_scores = torch.matmul(supported_embeddings, image_embedding)
    unsupported_scores = torch.matmul(unsupported_embeddings, image_embedding)

    best_supported_score, best_supported_index = torch.max(supported_scores, dim=0)
    best_unsupported_score, best_unsupported_index = torch.max(unsupported_scores, dim=0)

    best_supported_label = SUPPORTED_PROMPTS[best_supported_index.item()][0]
    best_unsupported_label = UNSUPPORTED_PROMPTS[best_unsupported_index.item()][0]

    best_supported_score = float(best_supported_score.item())
    best_unsupported_score = float(best_unsupported_score.item())

    validation_result = {
        "best_supported_label": best_supported_label,
        "best_supported_score": round(best_supported_score, 4),
        "best_unsupported_label": best_unsupported_label,
        "best_unsupported_score": round(best_unsupported_score, 4),
    }

    print("CLIP VALIDATION:", validation_result)

    if best_supported_score < CLIP_MIN_SUPPORTED_SCORE:
        raise _unsupported_upload_error(validation_result)

    if best_unsupported_score > best_supported_score + CLIP_UNSUPPORTED_MARGIN:
        raise _unsupported_upload_error(validation_result)

    return validation_result


def _get_supported_prompt_embeddings():
    global _supported_prompt_embeddings

    if _supported_prompt_embeddings is not None:
        return _supported_prompt_embeddings

    prompts = [prompt for _, prompt in SUPPORTED_PROMPTS]
    _supported_prompt_embeddings = encode_text_prompts(prompts)

    return _supported_prompt_embeddings


def _get_unsupported_prompt_embeddings():
    global _unsupported_prompt_embeddings

    if _unsupported_prompt_embeddings is not None:
        return _unsupported_prompt_embeddings

    prompts = [prompt for _, prompt in UNSUPPORTED_PROMPTS]
    _unsupported_prompt_embeddings = encode_text_prompts(prompts)

    return _unsupported_prompt_embeddings


def _unsupported_upload_error(validation_result):
    return HTTPException(
        status_code=422,
        detail={
            "code": "unsupported_upload",
            "message": (
                "We could not confidently detect a supported garment. "
                "Please upload a clear image of one jacket, shirt, pair of pants, or pair of shoes."
            ),
            "clip_validation": validation_result,
        },
    )