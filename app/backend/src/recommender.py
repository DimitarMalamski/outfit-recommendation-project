def recommend_outfit(prediction_result):
    """
    Temporary recommendation function.

    Later this will:
    - filter catalogue by predicted style
    - exclude same predicted type
    - rank candidates with CLIP embeddings
    """

    return [
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
    ]