import torch
from PIL import Image
from torchvision import transforms

from src.config import (
    STYLE_MULTI_CONFIDENCE_THRESHOLD,
    STYLE_ALTERNATIVE_MIN_CONFIDENCE,
    STYLE_CLOSE_MARGIN,
    MAX_STYLE_CANDIDATES,
    STYLE_CLASSES,
    TYPE_CLASSES,
)
from src.model_loader import get_device, load_style_model, load_type_model


image_transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)

def _predict_probabilities(model, image_tensor, class_names):
    with torch.no_grad():
        logits = model(image_tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    return {
        class_names[index]: round(float(probabilities[index].item()), 4)
        for index in range(len(class_names))
    }

def select_style_candidates(style_probabilities):
    sorted_styles = sorted(
        style_probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_style, top_confidence = sorted_styles[0]

    candidates = [
        {
            "style": top_style,
            "confidence": top_confidence,
            "reason": "Most likely aesthetic",
        }
    ]

    for style, confidence in sorted_styles[1:]:
        margin = top_confidence - confidence

        is_close_to_top = margin <= STYLE_CLOSE_MARGIN
        is_useful_alternative = (
            top_confidence < STYLE_MULTI_CONFIDENCE_THRESHOLD
            and confidence >= STYLE_ALTERNATIVE_MIN_CONFIDENCE
        )

        if is_close_to_top or is_useful_alternative:
            candidates.append(
                {
                    "style": style,
                    "confidence": confidence,
                    "reason": "Alternative aesthetic because the style prediction is uncertain",
                }
            )

        if len(candidates) >= MAX_STYLE_CANDIDATES:
            break

    return candidates

def _predict_single_model(model, image_tensor, class_names):
    with torch.no_grad():
        logits = model(image_tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    confidence, predicted_index = torch.max(probabilities, dim=0)

    return class_names[predicted_index.item()], confidence.item()


def predict_image(image: Image.Image):
    device = get_device()

    style_model = load_style_model()
    type_model = load_type_model()

    image_tensor = image_transform(image).unsqueeze(0).to(device)

    style_probabilities = _predict_probabilities(
        style_model,
        image_tensor,
        STYLE_CLASSES,
    )

    style_candidates = select_style_candidates(style_probabilities)

    predicted_style = style_candidates[0]["style"]
    style_confidence = style_candidates[0]["confidence"]

    predicted_type, type_confidence = _predict_single_model(
        type_model,
        image_tensor,
        TYPE_CLASSES,
    )

    return {
        "predicted_style": predicted_style,
        "style_confidence": round(style_confidence, 4),
        "style_probabilities": style_probabilities,
        "style_candidates": style_candidates,
        "style_mode": "multi_style" if len(style_candidates) > 1 else "single_style",
        "predicted_type": predicted_type,
        "type_confidence": round(type_confidence, 4),
    }