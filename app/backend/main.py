from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
import json

from src.prediction import predict_image
from src.recommender import recommend_outfit, recommend_replacement_item
from src.upload_validator import validate_clip_supported_garment

from fastapi.staticfiles import StaticFiles
from src.config import CATALOGUE_DIR

from src.clip_service import load_clip_model

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
}

MAX_IMAGE_SIZE_BYTES = 8 * 1024 * 1024
MIN_IMAGE_WIDTH = 128
MIN_IMAGE_HEIGHT = 128

MIN_SUPPORTED_TYPE_CONFIDENCE = 0.30
TYPE_CONFIDENCE_FOR_MODEL_TRUST = 0.55

app = FastAPI(title="Runway AI Stylist API")

app.mount(
    "/catalogue",
    StaticFiles(directory=CATALOGUE_DIR),
    name="catalogue"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Runway AI Stylist API is running"}

@app.get("/test-clip")
def test_clip():
    load_clip_model()
    return {"message": "CLIP model loaded successfully"}

async def read_validated_image(file: UploadFile) -> Image.Image:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "unsupported_file_type",
                "message": "Please upload a JPG or PNG image.",
            },
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "empty_file",
                "message": "The uploaded file appears to be empty.",
            },
        )

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "file_too_large",
                "message": "The image is too large. Please upload an image smaller than 8 MB.",
            },
        )

    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_image",
                "message": "The uploaded file could not be read as an image.",
            },
        )

    width, height = image.size

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "image_too_small",
                "message": "The image is too small. Please upload a clearer image with higher resolution.",
            },
        )

    return image

def validate_supported_garment_prediction(prediction_result):
    type_confidence = prediction_result["type_confidence"]
    predicted_type = prediction_result["predicted_type"]

    print("TYPE VALIDATION:", {
        "predicted_type": predicted_type,
        "type_confidence": type_confidence,
        "minimum_required": MIN_SUPPORTED_TYPE_CONFIDENCE,
    })

    if type_confidence < MIN_SUPPORTED_TYPE_CONFIDENCE:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "unsupported_clothing_item",
                "message": (
                    "We could not confidently detect a supported garment. "
                    "Please upload a clear image of one jacket, shirt, pair of pants, or pair of shoes."
                ),
                "predicted_type": predicted_type,
                "type_confidence": type_confidence,
            },
        )

def apply_clip_type_fallback(prediction_result, clip_validation):
    type_confidence = prediction_result["type_confidence"]
    original_type = prediction_result["predicted_type"]
    clip_type = clip_validation["best_supported_label"]

    if type_confidence < TYPE_CONFIDENCE_FOR_MODEL_TRUST:
        print("TYPE FALLBACK APPLIED:", {
            "original_type": original_type,
            "original_confidence": type_confidence,
            "clip_type": clip_type,
        })

        prediction_result["predicted_type"] = clip_type
        prediction_result["type_confidence"] = round(
            max(type_confidence, clip_validation["best_supported_score"]),
            4,
        )

    return prediction_result

@app.post("/recommend")
async def recommend(file: UploadFile = File(...)):
    image = await read_validated_image(file)

    prediction_result = predict_image(image)
    validate_supported_garment_prediction(prediction_result)

    clip_validation = validate_clip_supported_garment(image)
    prediction_result = apply_clip_type_fallback(prediction_result, clip_validation)

    recommendation_result = recommend_outfit(prediction_result, image)

    return {
        **prediction_result,
        "reliability": calculate_reliability(prediction_result),
        "styling_notes": create_styling_notes(prediction_result),
        "recommendations": recommendation_result["recommendations"],
        "outfits": recommendation_result["outfits"],
        "recommendation_groups": recommendation_result["recommendation_groups"],
    }

@app.post("/recommend/replace-item")
async def replace_item(
    file: UploadFile = File(...),
    target_type: str = Form(...),
    predicted_style: str = Form(...),
    exclude_image_urls: str = Form("[]"),
):
    image = await read_validated_image(file)

    try:
        excluded_urls = json.loads(exclude_image_urls)
    except json.JSONDecodeError:
        excluded_urls = []

    replacement_item = recommend_replacement_item(
        target_type=target_type,
        predicted_style=predicted_style,
        input_image=image,
        exclude_image_urls=excluded_urls,
    )

    if replacement_item is None:
        raise HTTPException(
            status_code=404,
            detail="No alternative item found for this category and style.",
        )

    return {
        "item": replacement_item
    }


def calculate_reliability(prediction_result):
    style_conf = prediction_result["style_confidence"]
    type_conf = prediction_result["type_confidence"]

    if style_conf >= 0.80 and type_conf >= 0.80:
        return "high"

    if style_conf >= 0.60 and type_conf >= 0.60:
        return "medium"

    return "low"


def create_styling_notes(prediction_result):
    style = prediction_result["predicted_style"]
    item_type = prediction_result["predicted_type"]
    style_conf = prediction_result["style_confidence"]
    type_conf = prediction_result["type_confidence"]
    style_mode = prediction_result.get("style_mode", "single_style")
    style_candidates = prediction_result.get("style_candidates", [])

    if style_mode == "multi_style" and len(style_candidates) > 1:
        alternative_styles = [
            candidate["style"]
            for candidate in style_candidates[1:]
        ]

        alternatives_text = ", ".join(alternative_styles)

        style_note = (
            f"The uploaded item was classified mainly as {style}, "
            f"but the style confidence is not high enough to treat it as only one aesthetic. "
            f"The system also found possible alternative aesthetic direction(s): {alternatives_text}. "
            "Because fashion items can fit multiple aesthetics, recommendations are shown for each possible direction. "
        )
    else:
        style_note = (
            f"The uploaded item was classified as {style}. "
        )

    if style_conf < 0.60 or type_conf < 0.60:
        confidence_note = (
            "Because one or both predictions are below the confidence threshold, "
            "this outfit should be treated as a suggested prototype result rather than a fully reliable recommendation."
        )
    else:
        confidence_note = (
            "Both predictions are above the confidence threshold, so the recommendation is considered more reliable."
        )

    return (
        f"{style_note}"
        f"The item was detected as a {item_type}. "
        "The system selected catalogue items from the same predicted aesthetic direction, "
        "excluded the uploaded item type, and ranked candidates using CLIP-based visual similarity. "
        f"{confidence_note}"
    )