from io import BytesIO

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from src.prediction import predict_image
from src.recommender import recommend_outfit

from fastapi.staticfiles import StaticFiles
from src.config import CATALOGUE_DIR

from src.clip_service import load_clip_model

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

@app.post("/recommend")
async def recommend(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    prediction_result = predict_image(image)
    recommendations = recommend_outfit(prediction_result, image)

    return {
        **prediction_result,
        "reliability": calculate_reliability(prediction_result),
        "styling_notes": create_styling_notes(prediction_result),
        "recommendations": recommendations,
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
        f"The uploaded item was classified as {style} and detected as a {item_type}. "
        "The system selected catalogue items from the same predicted style, excluded the uploaded item type, "
        "and ranked candidates using CLIP-based visual similarity. "
        f"{confidence_note}"
    )