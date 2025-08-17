import io
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from green_fashion.database.mongodb_manager import MongoDBManager
from green_fashion.storage.gcs_service import get_gcs_service
from pydantic import BaseModel

app = FastAPI(
    title="Green Fashion Wardrobe API",
    description="API for managing wardrobe items with MongoDB storage",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ClothingItem(BaseModel):
    custom_name: str
    category: str
    body_section: int
    notes: Optional[str] = ""
    colors: Optional[List[Dict]] = []
    display_name: Optional[str] = ""
    path: Optional[str] = None


class UpdateClothingItem(BaseModel):
    custom_name: Optional[str] = None
    category: Optional[str] = None
    body_section: Optional[int] = None
    notes: Optional[str] = None
    colors: Optional[List[Dict]] = None


class GoogleAuthRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BUCKET_NAME = os.getenv("GCS_IMAGE_BUCKET")
# Initialize database connection
db_manager = MongoDBManager(MONGO_URI)
gcs_service = get_gcs_service(BUCKET_NAME)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials, GOOGLE_CLIENT_SECRET, algorithms=["HS256"]
        )
        user_id = payload["user_id"]
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/")
async def root():
    return {"message": "Green Fashion Wardrobe API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    if not db_manager.client:
        raise HTTPException(status_code=503, detail="Database connection failed")
    return {"status": "healthy", "database": "connected"}


@app.get("/items", response_model=List[Dict])
async def get_all_items(current_user_id: str = Depends(get_current_user)):
    """Get all clothing items"""
    print(f"getting all items for {current_user_id}")
    try:
        return db_manager.get_all_items(current_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/items/{item_id}")
async def get_item(item_id: str, current_user_id: str = Depends(get_current_user)):
    """Get a specific clothing item by ID"""
    try:
        item = db_manager.get_item_by_id(item_id, current_user_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/items")
async def create_item(
    item: ClothingItem, current_user_id: str = Depends(get_current_user)
):
    """Create a new clothing item"""
    try:
        item_data = item.dict()
        item_data["user_id"] = current_user_id
        item_id = db_manager.add_clothing_item(item_data)
        if not item_id:
            raise HTTPException(status_code=500, detail="Failed to create item")
        return {"id": item_id, "message": "Item created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/items/{item_id}")
async def update_item(
    item_id: str,
    updates: UpdateClothingItem,
    current_user_id: str = Depends(get_current_user),
):
    """Update an existing clothing item"""
    try:
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid updates provided")

        success = db_manager.update_item(item_id, update_data, current_user_id)
        if not success:
            raise HTTPException(
                status_code=404, detail="Item not found or update failed"
            )
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/items/{item_id}")
async def delete_item(item_id: str, current_user_id: str = Depends(get_current_user)):
    """Delete a clothing item"""
    try:
        # Get item first to access image path if it exists
        item = db_manager.get_item_by_id(item_id, current_user_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Delete from database
        success = db_manager.delete_item(item_id, current_user_id)
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to delete item from database"
            )

        # Delete image from GCS if it exists
        if item.get("path"):
            try:
                gcs_service.delete_image(item["path"])
            except Exception as e:
                print(f"Warning: Failed to delete image from storage: {str(e)}")

        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/items/category/{category}")
async def get_items_by_category(
    category: str, current_user_id: str = Depends(get_current_user)
):
    """Get all items in a specific category"""
    try:
        items = db_manager.get_items_by_category(category, current_user_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
async def get_categories(current_user_id: str = Depends(get_current_user)):
    """Get all unique categories"""
    try:
        categories = db_manager.get_categories(current_user_id)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_items(query: str, current_user_id: str = Depends(get_current_user)):
    """Search for items by name, category, or filename"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        items = db_manager.search_items(query, current_user_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats(current_user_id: str = Depends(get_current_user)):
    """Get wardrobe statistics"""
    try:
        total_items = db_manager.get_item_count(current_user_id)
        category_counts = db_manager.get_category_counts(current_user_id)
        return {"total_items": total_items, "category_counts": category_counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/items/{item_id}/upload-image")
async def upload_image(
    item_id: str,
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
):
    """Upload an image for a clothing item"""
    try:
        # Check if item exists
        item = db_manager.get_item_by_id(item_id, current_user_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save image to GCS using display_name (original filename)
        # Remove file extension from display_name and clean it up
        base_filename = (
            file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
        )
        filename = base_filename.replace(" ", "_").lower()
        print(f"Debug: Attempting to save image with filename: {filename}")

        try:
            # Construct the full blob path
            blob_path = f"images/wardrobe/{filename}"
            image_path = gcs_service.save_image(image=file.file, blob_path=blob_path)
            print(f"Debug: GCS save_image returned: {image_path}")
        except Exception as e:
            print(f"Debug: GCS save_image failed with error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to save image to GCS: {str(e)}"
            )

        if not image_path:
            raise HTTPException(
                status_code=500, detail="Failed to save image - no path returned"
            )

        # Store the path relative to /images/ endpoint (remove "images/" prefix)
        # API route is /images/{path}, so we store "wardrobe/filename.jpg"
        stored_path = (
            image_path.replace("images/", "", 1)
            if image_path.startswith("images/")
            else image_path
        )

        # Update item with image path
        db_manager.update_item(
            item_id,
            {"path": stored_path, "display_name": file.filename},
            current_user_id,
        )

        return {"message": "Image uploaded successfully", "path": image_path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/google", response_model=AuthResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    try:
        idinfo = id_token.verify_oauth2_token(
            auth_request.token, requests.Request(), GOOGLE_CLIENT_ID
        )

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(status_code=401, detail="Invalid token issuer")

        user = db_manager.create_or_get_user(
            {
                "google_id": idinfo["sub"],
                "email": idinfo["email"],
                "name": idinfo["name"],
                "picture": idinfo.get("picture"),
            }
        )

        jwt_token = jwt.encode(
            {
                "user_id": str(user["_id"]),
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture"),
                "exp": datetime.utcnow() + timedelta(days=7),
            },
            GOOGLE_CLIENT_SECRET,
            algorithm="HS256",
        )

        return AuthResponse(
            token=jwt_token,
            user=UserResponse(
                id=str(user["_id"]),
                email=user["email"],
                name=user["name"],
                picture=user.get("picture"),
            ),
        )

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/images/{image_path:path}")
async def get_image(image_path: str):
    """Serve images from Google Cloud Storage"""
    try:
        # Construct full GCS path (add "images/" prefix back)
        full_gcs_path = f"images/{image_path}"
        print("loading image from", full_gcs_path)
        image = gcs_service.load_image(full_gcs_path)
        print("image loaded")
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG", quality=95)
        img_byte_arr.seek(0)

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(img_byte_arr.getvalue()),
            media_type="image/jpeg",
            headers={"Cache-Control": "max-age=3600"},  # Cache for 1 hour
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
