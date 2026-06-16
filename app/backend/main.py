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
    "image/webp",
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
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:4000",
    ],
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

def create_analysis_response(prediction_result):
    return {
        "predicted_type": prediction_result["predicted_type"],
        "type_confidence": prediction_result["type_confidence"],
        "main_style": prediction_result["main_style"],
        "predicted_styles": prediction_result["predicted_styles"],
        "style_scores": prediction_result["style_scores"],
        "style_threshold": prediction_result["style_threshold"],
        "used_top1_fallback": prediction_result["used_top1_fallback"],
        "style_model_mode": "multi_label_sigmoid",
        "recommendation_strategy": "multi_label_style_filter_with_clip_ranking",
    }

@app.post("/recommend")
async def recommend(file: UploadFile = File(...)):
    image = await read_validated_image(file)

    clip_validation = validate_clip_supported_garment(image)

    prediction_result = predict_image(image)
    prediction_result = apply_clip_type_fallback(prediction_result, clip_validation)

    validate_supported_garment_prediction(prediction_result)

    recommendation_result = recommend_outfit(prediction_result, image)

    return {
        **prediction_result,
        "analysis": create_analysis_response(prediction_result),
        "reliability": calculate_reliability(prediction_result),
        "styling_notes": create_styling_notes(prediction_result),
        "recommendations": recommendation_result["recommendations"],
        "outfits": recommendation_result["outfits"],
        "recommendation_groups": recommendation_result["recommendation_groups"],
    }

@app.post("/recommend/refine-style")
async def refine_recommendation_style(
    file: UploadFile = File(...),
    selected_styles: str = Form(...),
    predicted_type: str = Form(...),
    main_style: str = Form(...),
    type_confidence: float = Form(1.0),
):
    image = await read_validated_image(file)

    style_pool = parse_form_list(selected_styles)

    if not style_pool:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "empty_style_pool",
                "message": "Please provide at least one selected style.",
            },
        )

    prediction_result = {
        "predicted_style": main_style,
        "main_style": main_style,
        "style_confidence": 1.0,
        "predicted_styles": style_pool,
        "style_scores": {
            style: 1.0 if style in style_pool else 0.0
            for style in ["formal", "gothic", "sporty", "streetwear"]
        },
        "style_probabilities": {
            style: 1.0 if style in style_pool else 0.0
            for style in ["formal", "gothic", "sporty", "streetwear"]
        },
        "style_candidates": [
            {
                "style": style,
                "confidence": 1.0,
                "reason": "Selected by user recommendation mode",
            }
            for style in style_pool
        ],
        "style_mode": "multi_style" if len(style_pool) > 1 else "single_style",
        "style_threshold": None,
        "used_top1_fallback": False,
        "predicted_type": predicted_type,
        "type_confidence": type_confidence,
    }

    recommendation_result = recommend_outfit(
        prediction_result,
        image,
        selected_styles=style_pool,
    )

    return {
        "selected_styles": style_pool,
        "recommendations": recommendation_result["recommendations"],
        "outfits": recommendation_result["outfits"],
        "recommendation_groups": recommendation_result["recommendation_groups"],
    }

def parse_form_list(value: str):
    if value is None:
        return []

    value = value.strip()

    if not value:
        return []

    try:
        parsed = json.loads(value)

        if isinstance(parsed, list):
            return [
                str(item).strip()
                for item in parsed
                if str(item).strip()
            ]

        if isinstance(parsed, str):
            return [parsed.strip()]

    except json.JSONDecodeError:
        pass

    cleaned_value = value.strip("[]")

    return [
        item.strip().strip("'").strip('"')
        for item in cleaned_value.split(",")
        if item.strip().strip("'").strip('"')
    ]

@app.post("/recommend/replace-item")
async def replace_item(
    file: UploadFile = File(...),
    target_type: str = Form(...),
    predicted_style: str = Form(...),
    predicted_styles: str = Form(None),
    exclude_image_urls: str = Form("[]"),
):
    image = await read_validated_image(file)

    excluded_urls = parse_form_list(exclude_image_urls)

    style_pool = predicted_styles if predicted_styles else predicted_style

    replacement_item = recommend_replacement_item(
        target_type=target_type,
        predicted_style=style_pool,
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

    style_threshold = prediction_result.get("style_threshold")
    used_top1_fallback = prediction_result.get("used_top1_fallback", False)

    is_multilabel_style_result = style_threshold is not None

    if is_multilabel_style_result:
        if used_top1_fallback:
            return "low"

        if type_conf >= 0.80 and style_conf >= 0.60:
            return "high"

        if type_conf >= 0.60 and style_conf >= style_threshold:
            return "medium"

        return "low"

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
            f"The system also detected possible alternative aesthetic direction(s): {alternatives_text}. "
            "Because fashion items can fit multiple aesthetics, the recommendation system uses all selected styles as candidates. "
        )
    else:
        style_note = (
            f"The uploaded item was classified as {style}. "
        )

    reliability = calculate_reliability(prediction_result)

    if reliability == "high":
        confidence_note = (
            "The type prediction is strong and the main style score is high for the multi-label setup, "
            "so the recommendation is considered highly reliable."
        )
    elif reliability == "medium":
        confidence_note = (
            "The type prediction is strong and the selected style passed the multi-label threshold, "
            "so the recommendation is considered moderately reliable."
        )
    else:
        confidence_note = (
            "Because the style selection or type prediction is uncertain, "
            "this outfit should be treated as a suggested prototype result rather than a fully reliable recommendation."
        )

    return (
        f"{style_note}"
        f"The item was detected as a {item_type}. "
        "The system selected catalogue items from the predicted multi-label aesthetic pool, "
        "excluded the uploaded item type, and ranked candidates using CLIP-based visual similarity. "
        f"{confidence_note}"
    )