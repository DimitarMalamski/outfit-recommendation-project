from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

MODELS_DIR = BASE_DIR / "models"
DATASET_DIR = BASE_DIR / "dataset"
RESULTS_DIR = BASE_DIR / "results"

STYLE_MODEL_PATH = MODELS_DIR / "style_mobilenet_v3_large_architecture_comparison.pth"
TYPE_MODEL_PATH = MODELS_DIR / "type_resnet34_extra_data.pth"

CATALOGUE_DIR = DATASET_DIR / "cleaned"

STYLE_CLASSES = ["formal", "gothic", "sporty", "streetwear"]
TYPE_CLASSES = ["jacket", "pants", "shoes", "tshirt"]

STYLE_CONFIDENCE_THRESHOLD = 0.60
TYPE_CONFIDENCE_THRESHOLD = 0.60