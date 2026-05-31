from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Runway AI Stylist API")

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


@app.post("/recommend")
async def recommend(file: UploadFile = File(...)):
    return {
        "predicted_style": "streetwear",
        "style_confidence": 0.87,
        "predicted_type": "jacket",
        "type_confidence": 0.91,
        "reliability": "high",
        "styling_notes": (
            "The uploaded item was matched with visually similar pieces from the same predicted style, "
            "while avoiding duplicate clothing categories."
        ),
        "recommendations": [
            {
                "type": "bottom",
                "name": "Wide-leg black trousers",
                "brand": "Prototype Catalogue",
                "image_url": "/demo-outfits/pants.png",
                "score": 0.84
            },
            {
                "type": "shoes",
                "name": "Minimal leather sneakers",
                "brand": "Prototype Catalogue",
                "image_url": "/demo-outfits/shoes.png",
                "score": 0.81
            },
            {
                "type": "top",
                "name": "Oversized graphic tee",
                "brand": "Prototype Catalogue",
                "image_url": "/demo-outfits/top.png",
                "score": 0.79
            }
        ]
    }