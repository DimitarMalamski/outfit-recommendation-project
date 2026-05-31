import torch
from torchvision import models

from src.config import STYLE_MODEL_PATH, TYPE_MODEL_PATH, STYLE_CLASSES, TYPE_CLASSES


_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_style_model = None
_type_model = None


def get_device():
    return _device


def load_style_model():
    global _style_model

    if _style_model is not None:
        return _style_model

    model = models.mobilenet_v3_large(weights=None)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(STYLE_CLASSES))

    checkpoint = torch.load(
      STYLE_MODEL_PATH,
      map_location=_device,
      weights_only=False
    )

    state_dict = checkpoint["model_state_dict"]

    model.load_state_dict(state_dict)

    model.to(_device)
    model.eval()

    _style_model = model
    return _style_model


def load_type_model():
    global _type_model

    if _type_model is not None:
        return _type_model

    model = models.resnet34(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(TYPE_CLASSES))

    checkpoint = torch.load(
      TYPE_MODEL_PATH,
      map_location=_device,
      weights_only=False
    )
    
    state_dict = checkpoint["model_state_dict"]

    model.load_state_dict(state_dict)

    model.to(_device)
    model.eval()

    _type_model = model
    return _type_model