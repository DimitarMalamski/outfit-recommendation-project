# Deployment Guide

This project is deployed as two separate applications:

```text
Frontend: Vercel
Backend: Hugging Face Spaces
```

## Backend Deployment: Hugging Face Spaces

The backend is deployed as a Docker Space.

### Required Space Settings

```yml
sdk: docker
app_port: 7860
```

### Backend Docker Command

For Hugging Face, the backend must run on port `7860`:

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Important Notes

The backend includes:

- FastAPI application
- trained style classification model
- trained clothing type classification model
- CLIP recommendation logic
- catalogue images
- catalogue embeddings

Large files such as `.png`, `.pt`, and `.pth` should be tracked with Git LFS.

Recommended LFS tracking:

```bash
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.jpeg"
git lfs track "*.pt"
git lfs track "*.pth"
```

## Frontend Deployment: Vercel

The frontend is deployed from the project repository.

### Vercel Settings

Root directory:

```text
app/frontend/runway-ai-stylist
```

Framework:

```text
Next.js
```

### Required Environment Variable

```env
NEXT_PUBLIC_API_URL=https://dimitarm-runway-ai-stylist-api.hf.space
```

After setting or changing environment variables, redeploy the frontend.

## Deployment Test

After deployment, test the following:

1. Open the backend root endpoint.
2. Open the backend Swagger docs.
3. Open the Vercel frontend.
4. Upload one clothing item.
5. Confirm that predictions and recommendation images are displayed.
