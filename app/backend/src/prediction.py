import torch
from PIL import Image
from torchvision import transforms

from src.config import STYLE_CLASSES, TYPE_CLASSES
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

    predicted_style, style_confidence = _predict_single_model(
        style_model,
        image_tensor,
        STYLE_CLASSES,
    )

    predicted_type, type_confidence = _predict_single_model(
        type_model,
        image_tensor,
        TYPE_CLASSES,
    )

    return {
        "predicted_style": predicted_style,
        "style_confidence": round(style_confidence, 4),
        "predicted_type": predicted_type,
        "type_confidence": round(type_confidence, 4),
    }