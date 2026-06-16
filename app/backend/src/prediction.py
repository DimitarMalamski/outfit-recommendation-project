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
    STYLE_MULTILABEL_THRESHOLD,
)

from src.model_loader import (
    get_device,
    load_style_model,
    load_type_model,
    load_multilabel_style_model,
)


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

def predict_multilabel_style(image: Image.Image):
    device = get_device()
    style_model = load_multilabel_style_model()

    image_tensor = image_transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = style_model(image_tensor)

        # Important:
        # This model was trained with BCEWithLogitsLoss,
        # so inference must use sigmoid, not softmax.
        scores = torch.sigmoid(logits)[0]

    style_scores = {
        STYLE_CLASSES[index]: round(float(scores[index].item()), 4)
        for index in range(len(STYLE_CLASSES))
    }

    sorted_styles = sorted(
        style_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    predicted_styles = [
        style
        for style, score in sorted_styles
        if score >= STYLE_MULTILABEL_THRESHOLD
    ]

    used_top1_fallback = False

    if not predicted_styles:
        predicted_styles = [sorted_styles[0][0]]
        used_top1_fallback = True

    main_style = predicted_styles[0]

    return {
        "main_style": main_style,
        "predicted_styles": predicted_styles,
        "style_scores": style_scores,
        "style_threshold": STYLE_MULTILABEL_THRESHOLD,
        "used_top1_fallback": used_top1_fallback,
    }

def predict_image(image: Image.Image):
    device = get_device()

    type_model = load_type_model()

    image_tensor = image_transform(image).unsqueeze(0).to(device)

    style_result = predict_multilabel_style(image)

    predicted_style = style_result["main_style"]
    predicted_styles = style_result["predicted_styles"]
    style_scores = style_result["style_scores"]
    style_confidence = style_scores[predicted_style]

    style_candidates = [
        {
            "style": style,
            "confidence": style_scores[style],
            "reason": (
                "Selected by multi-label sigmoid threshold"
                if not style_result["used_top1_fallback"]
                else "Selected by top-1 fallback because no style passed the threshold"
            ),
        }
        for style in predicted_styles
    ]

    predicted_type, type_confidence = _predict_single_model(
        type_model,
        image_tensor,
        TYPE_CLASSES,
    )

    return {
        "predicted_style": predicted_style,
        "main_style": predicted_style,
        "style_confidence": round(style_confidence, 4),

        # Kept for frontend compatibility
        "style_probabilities": style_scores,
        "style_candidates": style_candidates,
        "style_mode": "multi_style" if len(predicted_styles) > 1 else "single_style",

        # New final architecture fields
        "predicted_styles": predicted_styles,
        "style_scores": style_scores,
        "style_threshold": style_result["style_threshold"],
        "used_top1_fallback": style_result["used_top1_fallback"],

        "predicted_type": predicted_type,
        "type_confidence": round(type_confidence, 4),
    }