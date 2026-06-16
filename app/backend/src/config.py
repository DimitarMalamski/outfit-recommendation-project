from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

MODELS_DIR = BACKEND_DIR / "models"
CATALOGUE_DIR = BACKEND_DIR / "catalogue"
DATA_DIR = BACKEND_DIR / "data"

STYLE_MODEL_PATH = MODELS_DIR / "style_mobilenet_v3_large_architecture_comparison.pth"
STYLE_MULTILABEL_MODEL_PATH = MODELS_DIR / "style_mobilenet_v3_large_multilabel_bce.pth"

TYPE_MODEL_PATH = MODELS_DIR / "type_resnet34_extra_data.pth"

CATALOGUE_EMBEDDINGS_PATH = DATA_DIR / "catalogue_embeddings.pt"

STYLE_CLASSES = ["formal", "gothic", "sporty", "streetwear"]
TYPE_CLASSES = ["jacket", "pants", "shoes", "tshirt"]

STYLE_MULTILABEL_THRESHOLD = 0.35

STYLE_CONFIDENCE_THRESHOLD = 0.60
TYPE_CONFIDENCE_THRESHOLD = 0.60

STYLE_MULTI_CONFIDENCE_THRESHOLD = 0.70
STYLE_ALTERNATIVE_MIN_CONFIDENCE = 0.20
STYLE_CLOSE_MARGIN = 0.15
MAX_STYLE_CANDIDATES = 3