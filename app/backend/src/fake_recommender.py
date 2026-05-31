def get_fake_recommendation_response():
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
                "score": 0.84,
            },
            {
                "type": "shoes",
                "name": "Minimal leather sneakers",
                "brand": "Prototype Catalogue",
                "image_url": "/demo-outfits/shoes.png",
                "score": 0.81,
            },
            {
                "type": "top",
                "name": "Oversized graphic tee",
                "brand": "Prototype Catalogue",
                "image_url": "/demo-outfits/top.png",
                "score": 0.79,
            },
        ],
    }