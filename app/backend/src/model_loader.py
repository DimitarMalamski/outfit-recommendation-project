import torch
from torchvision import models

from src.config import (
    STYLE_MODEL_PATH,
    STYLE_MULTILABEL_MODEL_PATH,
    TYPE_MODEL_PATH,
    STYLE_CLASSES,
    TYPE_CLASSES,
    STYLE_MULTILABEL_THRESHOLD,
)


_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_style_model = None
_style_multilabel_model = None
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

def load_multilabel_style_model():
    global _style_multilabel_model

    if _style_multilabel_model is not None:
        return _style_multilabel_model

    checkpoint = torch.load(
        STYLE_MULTILABEL_MODEL_PATH,
        map_location=_device,
        weights_only=False,
    )

    checkpoint_class_names = checkpoint.get("class_names", STYLE_CLASSES)

    if checkpoint_class_names != STYLE_CLASSES:
        raise ValueError(
            f"Style class mismatch. Expected {STYLE_CLASSES}, got {checkpoint_class_names}"
        )

    if checkpoint.get("uses_sigmoid") is not True:
        raise ValueError(
            "This is not the expected multi-label style checkpoint. "
            "Expected uses_sigmoid=True."
        )

    if checkpoint.get("loss_function") != "BCEWithLogitsLoss":
        raise ValueError(
            "This is not the expected BCE multi-label checkpoint. "
            f"Found loss_function={checkpoint.get('loss_function')}"
        )

    model = models.mobilenet_v3_large(weights=None)

    model.classifier[3] = torch.nn.Linear(
        model.classifier[3].in_features,
        len(STYLE_CLASSES),
    )

    model.load_state_dict(checkpoint["model_state_dict"])

    model.to(_device)
    model.eval()

    _style_multilabel_model = model
    return _style_multilabel_model

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