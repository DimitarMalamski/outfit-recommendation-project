# Catalogue and Dataset Guide

The recommendation system uses a structured image catalogue.

## Catalogue Structure

The backend expects the catalogue to follow this structure:

```text
catalogue/
├── formal/
│   ├── jacket/
│   ├── pants/
│   ├── shoes/
│   └── tshirt/
├── gothic/
├── sporty/
└── streetwear/
```

Each style folder contains clothing type folders.

Current supported styles:

```text
formal
gothic
sporty
streetwear
```

Current supported clothing types:

```text
jacket
pants
shoes
tshirt
```

## How Recommendations Work

The system:

1. Predicts the uploaded item's style.
2. Predicts the uploaded item's clothing type.
3. Filters catalogue items by predicted style.
4. Excludes the uploaded clothing type.
5. Uses CLIP similarity to rank matching outfit items.

## Adding New Catalogue Images

To add new images:

1. Place each image in the correct style and type folder.
2. Use clear filenames.
3. Rebuild `catalogue_embeddings.pt`.
4. Redeploy the backend.

Example:

```text
catalogue/streetwear/shoes/streetwear_shoes_051.png
```

## Adding New Styles or Types

To add a new style or clothing type, update:

1. Catalogue folder structure.
2. Model label mappings.
3. Training dataset.
4. CLIP embedding generation.
5. Frontend display logic if needed.

## Important Limitation

The recommendation system depends on catalogue quality. If the catalogue contains weak or inconsistent images, the recommendations will also become weaker.
