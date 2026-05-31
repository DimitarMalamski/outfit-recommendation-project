import torch
import open_clip

from src.model_loader import get_device


_clip_model = None
_clip_preprocess = None


def load_clip_model():
    global _clip_model, _clip_preprocess

    if _clip_model is not None and _clip_preprocess is not None:
        return _clip_model, _clip_preprocess

    device = get_device()

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained="laion2b_s34b_b79k",
    )

    model.to(device)
    model.eval()

    _clip_model = model
    _clip_preprocess = preprocess

    return _clip_model, _clip_preprocess


def encode_image(image):
    device = get_device()
    model, preprocess = load_clip_model()

    image_tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model.encode_image(image_tensor)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)

    return embedding.cpu()