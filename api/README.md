# Green Fashion Wardrobe API

A FastAPI-based backend service for managing wardrobe items with MongoDB storage.

## Features

- CRUD operations for clothing items
- Image upload and storage via Google Cloud Storage
- Search functionality
- Category-based filtering
- Wardrobe statistics

## Setup

1. The API uses the project's shared dependencies. From the project root:
```bash
# Dependencies are already installed with uv sync
# FastAPI, uvicorn, and python-multipart are included in pyproject.toml
```

2. Set up environment variables (copy from main project's `.env` if available):
```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=green_fashion
COLLECTION_NAME=clothing_items
```

3. Run the server from the project root:
```bash
python api/main.py
```

Or using uvicorn directly:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Items Management
- `GET /items` - Get all clothing items
- `GET /items/{item_id}` - Get specific item
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

### Search & Filter
- `GET /items/category/{category}` - Get items by category
- `GET /search?query={query}` - Search items
- `GET /categories` - Get all categories

### Statistics
- `GET /stats` - Get wardrobe statistics

### Image Upload
- `POST /items/{item_id}/upload-image` - Upload image for item

## API Documentation

Once running, visit:
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc
