import torch
import open_clip

from src.model_loader import get_device


_clip_model = None
_clip_preprocess = None
_clip_tokenizer = None


def load_clip_model():
    global _clip_model, _clip_preprocess, _clip_tokenizer

    if (
        _clip_model is not None
        and _clip_preprocess is not None
        and _clip_tokenizer is not None
    ):
        return _clip_model, _clip_preprocess

    device = get_device()

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained="laion2b_s34b_b79k",
    )

    tokenizer = open_clip.get_tokenizer("ViT-B-32")

    model.to(device)
    model.eval()

    _clip_model = model
    _clip_preprocess = preprocess
    _clip_tokenizer = tokenizer

    return _clip_model, _clip_preprocess


def encode_image(image):
    device = get_device()
    model, preprocess = load_clip_model()

    image_tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model.encode_image(image_tensor)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)

    return embedding.cpu()


def encode_text_prompts(prompts):
    global _clip_tokenizer

    device = get_device()
    model, _ = load_clip_model()

    if _clip_tokenizer is None:
        _clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")

    text_tokens = _clip_tokenizer(prompts).to(device)

    with torch.no_grad():
        embeddings = model.encode_text(text_tokens)
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)

    return embeddings.cpu()