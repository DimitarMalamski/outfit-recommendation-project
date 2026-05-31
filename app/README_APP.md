# Runway AI Stylist

Runway AI Stylist is an AI fashion recommendation prototype. A user uploads one clothing item, and the system recommends a complete outfit using style classification, clothing type classification, and CLIP-based visual similarity.

## Project Structure

```text
app/
├── backend/
│   ├── main.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements-backend.txt
│   ├── catalogue/
│   ├── data/
│   ├── models/
│   └── src/
└── frontend/
    └── runway-ai-stylist/
```

## Backend

The backend is built with FastAPI and Python.

It performs:

1. Style prediction
2. Clothing type prediction
3. Catalogue filtering
4. CLIP similarity ranking
5. Outfit recommendation response

Run locally:

```bash
cd app/backend
docker compose up --build
```

Backend URL:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

## Frontend

The frontend is built with Next.js and TypeScript.

Run locally:

```bash
cd app/frontend/runway-ai-stylist
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

## Environment Variables

Frontend requires:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For deployment, use the deployed backend URL instead.

## Deployment

Current deployment:

```text
Frontend: Vercel
Backend: Hugging Face Spaces Docker
```

Live frontend:

```text
https://outfit-recommendation-project.vercel.app/
```

Live backend:

```text
https://dimitarm-runway-ai-stylist-api.hf.space
```

## Transferability

The project can be adapted by replacing or expanding the catalogue folders and rebuilding the CLIP embeddings file.

Expected catalogue structure:

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

To add new styles or clothing types, update the catalogue structure, model labels, and embedding generation process.
