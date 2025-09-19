import io
import os
import urllib.request
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse

import jwt
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from PIL import Image
from pydantic import BaseModel
from sqlalchemy import text

from green_fashion.color_extracting.color_palette_extractor import extract_color_palette
from green_fashion.database.mongodb_manager import MongoDBManager
from green_fashion.database.sql_connector import (
    AsyncSQLConnector,
    get_async_sql_connector,
)
from green_fashion.logging_utils import (
    logger,
    request_context_middleware,
    setup_logging,
)
from green_fashion.storage.gcs_service import get_gcs_service

# Load environment variables from .env file
load_dotenv()

# Initialize logging early
setup_logging(service_name="api")

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

# Request context and access logging
app.middleware("http")(request_context_middleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    try:
        body = await request.body()
        logger.error(f"Request body: {body.decode('utf-8')}")
    except Exception:
        logger.error("Could not decode request body")
    return JSONResponse(
        status_code=422, content={"detail": f"Validation error: {exc.errors()}"}
    )


# Pydantic models
class ClothingItem(BaseModel):
    custom_name: str
    wardrobe_category: int  # 1=Clothing, 2=Shoes, 3=Accessories
    category: int
    notes: Optional[str] = ""
    colors: Optional[List[Dict]] = []
    display_name: Optional[str] = ""
    path: Optional[str] = None


class UpdateClothingItem(BaseModel):
    custom_name: Optional[str] = None
    wardrobe_category: Optional[int] = None  # 1=Clothing, 2=Shoes, 3=Accessories
    category: Optional[int] = None
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


class ColorPalette(BaseModel):
    color: List[int]  # RGB values [r, g, b]
    percentage: float


class ColorExtractionResponse(BaseModel):
    colors: List[ColorPalette]


MONGO_URI = os.getenv("MONGODB_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BUCKET_NAME = os.getenv("GCS_IMAGE_BUCKET")
SQL_CONNECTION_STRING = os.getenv("MYSQL_CONNECTION_STRING")

# Validate required environment variables
for var_name, var_value in [
    ("MONGODB_URI", MONGO_URI),
    ("GOOGLE_CLIENT_ID", GOOGLE_CLIENT_ID),
    ("GOOGLE_CLIENT_SECRET", GOOGLE_CLIENT_SECRET),
    ("GCS_IMAGE_BUCKET", BUCKET_NAME),
]:
    if not var_value:
        raise RuntimeError(f"Critical environment variable '{var_name}' is not set.")

# Global variables for eager initialization
_db_manager = None
_gcs_service = None
_sql_connector = None
security = HTTPBearer()


def initialize_services():
    """Initialize services on startup"""
    global _db_manager, _gcs_service, _sql_connector

    # Initialize database manager
    if MONGO_URI:
        try:
            _db_manager = MongoDBManager(MONGO_URI)
            logger.info("Database manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            _db_manager = None

    else:
        logger.warning("Database URI not found")

    # Initialize SQL connector
    try:
        if SQL_CONNECTION_STRING:
            _sql_connector = get_async_sql_connector(SQL_CONNECTION_STRING)
            logger.info("SQL connector initialized successfully")
        else:
            logger.warning(
                "SQL connector not initialized - connection string not provided"
            )
            _sql_connector = None
    except Exception as e:
        logger.error(f"Failed to initialize SQL connector: {e}")
        _sql_connector = None

    # Initialize GCS service
    if BUCKET_NAME:
        try:
            _gcs_service = get_gcs_service(BUCKET_NAME)
            logger.info("GCS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCS service: {e}")
            _gcs_service = None


def get_db_manager():
    """Get database manager"""
    return _db_manager


def get_gcs_service_instance():
    """Get GCS service"""
    return _gcs_service


def get_sql_connector():
    """Get SQL connector"""
    return _sql_connector


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials, GOOGLE_CLIENT_SECRET, algorithms=["HS256"]
        )
        user_id = payload[
            "user_id"
        ]  # this now defaults to the mongodb user_id, not the google_id
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/v1/")
async def root():
    return {"message": "Green Fashion Wardrobe API", "version": "1.0.0"}


@app.get("/v1/health")
async def health_check():
    """Health check endpoint - lightweight check for fast deployment validation"""
    db_manager = get_db_manager()

    # Basic service availability check
    if not db_manager:
        return {"status": "starting", "database": "initializing"}

    # For deployment health checks, just verify the service is ready
    # Skip the expensive database ping during rapid checks
    return {"status": "healthy", "database": "ready", "api": "operational"}


@app.get("/v1/health/detailed")
async def detailed_health_check():
    """Detailed health check with database connectivity test"""
    db_manager = get_db_manager()
    sql_connector = get_sql_connector()

    health_status = {"status": "healthy", "api": "operational"}

    # Check MongoDB
    if not db_manager or not db_manager.client:
        health_status["mongodb"] = "connecting"
        health_status["status"] = "starting"
    else:
        try:
            db_manager.client.admin.command("ping")
            health_status["mongodb"] = "connected"
        except Exception as e:
            health_status["mongodb"] = "connection_error"
            health_status["status"] = "degraded"
            health_status["mongodb_error"] = str(e)

    # Check SQL Database
    if not sql_connector:
        health_status["sql"] = "not_configured"
    else:
        try:
            if sql_connector.test_connection():
                health_status["sql"] = "connected"
            else:
                health_status["sql"] = "connection_failed"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["sql"] = "connection_error"
            health_status["status"] = "degraded"
            health_status["sql_error"] = str(e)

    return health_status


@app.get("/v1/items", response_model=List[Dict])
async def get_all_items(current_user_id: str = Depends(get_current_user)):
    """Get all clothing items"""
    logger.bind(user_id=current_user_id).info("Fetching all items")
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        return db_manager.get_all_items(current_user_id)
    except Exception as e:
        logger.exception("Failed to get all items: {error}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/items/{item_id}")
async def get_item(item_id: str, current_user_id: str = Depends(get_current_user)):
    """Get a specific clothing item by ID"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        item = db_manager.get_item_by_id(item_id, current_user_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        logger.exception(
            "Failed to get item {item_id}: {error}", item_id=item_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/items")
async def create_item(
    item: ClothingItem, current_user_id: str = Depends(get_current_user)
):
    """Create a new clothing item"""
    try:
        logger.info(f"Received item data: {item.dict()}")
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        item_data = item.dict()
        item_data["user_id"] = current_user_id
        logger.info(f"Item data to save: {item_data}")
        logger.info(
            f"wardrobe_category type: {type(item_data['wardrobe_category'])}, value: {item_data['wardrobe_category']}"
        )
        # Ensure wardrobe_category is stored as an integer
        if "wardrobe_category" in item_data:
            item_data["wardrobe_category"] = int(item_data["wardrobe_category"])
            logger.info(
                f"After conversion - wardrobe_category type: {type(item_data['wardrobe_category'])}, value: {item_data['wardrobe_category']}"
            )
        item_id = db_manager.add_clothing_item(item_data)
        if not item_id:
            raise HTTPException(status_code=500, detail="Failed to create item")
        logger.bind(user_id=current_user_id).info("Item created", item_id=item_id)
        return {"id": item_id, "message": "Item created successfully"}
    except Exception as e:
        logger.exception("Failed to create item: {error}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/v1/items/{item_id}")
async def update_item(
    item_id: str,
    updates: UpdateClothingItem,
    current_user_id: str = Depends(get_current_user),
):
    """Update an existing clothing item"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid updates provided")

        # Ensure wardrobe_category is stored as an integer if it's being updated
        if "wardrobe_category" in update_data:
            update_data["wardrobe_category"] = int(update_data["wardrobe_category"])
            logger.info(
                f"Update - wardrobe_category converted to int: {update_data['wardrobe_category']}"
            )

        success = db_manager.update_item(item_id, update_data, current_user_id)
        if not success:
            raise HTTPException(
                status_code=404, detail="Item not found or update failed"
            )
        logger.bind(user_id=current_user_id).info("Item updated", item_id=item_id)
        return {"message": "Item updated successfully"}
    except Exception as e:
        logger.exception(
            "Failed to update item {item_id}: {error}", item_id=item_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/v1/items/{item_id}")
async def delete_item(item_id: str, current_user_id: str = Depends(get_current_user)):
    """Delete a clothing item"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
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
                gcs_service = get_gcs_service_instance()
                if gcs_service:
                    gcs_service.delete_image(item["path"])
            except Exception as e:
                logger.warning(
                    "Failed to delete image from storage: {error}", error=str(e)
                )

        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Failed to delete item {item_id}: {error}", item_id=item_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/items/category/{category}")
async def get_items_by_category(
    category: str, current_user_id: str = Depends(get_current_user)
):
    """Get all items in a specific category"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        items = db_manager.get_items_by_category(category, current_user_id)
        return items
    except Exception as e:
        logger.exception(
            "Failed to get items by category {category}: {error}",
            category=category,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/categories")
async def get_categories(current_user_id: str = Depends(get_current_user)):
    """Get all unique categories"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        categories = db_manager.get_categories(current_user_id)
        return {"categories": categories}
    except Exception as e:
        logger.exception("Failed to get categories: {error}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/search")
async def search_items(query: str, current_user_id: str = Depends(get_current_user)):
    """Search for items by name, category, or filename"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        items = db_manager.search_items(query, current_user_id)
        return items
    except Exception as e:
        logger.exception(
            "Search failed for query '{query}': {error}", query=query, error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/stats")
async def get_stats(current_user_id: str = Depends(get_current_user)):
    """Get wardrobe statistics"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        total_items = db_manager.get_item_count(current_user_id)
        category_counts = db_manager.get_category_counts(current_user_id)
        return {"total_items": total_items, "category_counts": category_counts}
    except Exception as e:
        logger.exception("Failed to get stats: {error}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/items/{item_id}/upload-image")
async def upload_image(
    item_id: str,
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
):
    """Upload an image for a clothing item"""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        # Check if item exists
        item = db_manager.get_item_by_id(item_id, current_user_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Generate unique ID for the filename to hide original name
        unique_id = str(uuid.uuid4())
        logger.debug(
            "Attempting to save image with id: {unique_id}", unique_id=unique_id
        )

        try:
            gcs_service = get_gcs_service_instance()
            if not gcs_service:
                raise HTTPException(
                    status_code=503, detail="Storage service not available"
                )
            # Construct the full blob path using unique ID
            blob_path = f"images/wardrobe/{unique_id}"
            image_path = gcs_service.save_image(image=file.file, blob_path=blob_path)
            logger.debug("GCS save_image returned: {image_path}", image_path=image_path)
        except Exception as e:
            logger.exception("GCS save_image failed: {error}", error=str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to save image to GCS: {str(e)}"
            )

        if not image_path:
            raise HTTPException(
                status_code=500, detail="Failed to save image - no path returned"
            )

        # Update item with image path
        db_manager.update_item(
            item_id,
            {"path": image_path, "display_name": file.filename},
            current_user_id,
        )

        return {"message": "Image uploaded successfully", "path": image_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Image upload failed for {item_id}: {error}", item_id=item_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/extract-colors", response_model=ColorExtractionResponse)
async def extract_colors(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
):
    """Extract color palette from an uploaded image"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Create PIL Image from uploaded file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Save temporarily to extract colors (the function expects a file path)
        temp_path = f"/tmp/{uuid.uuid4()}.jpg"
        image.save(temp_path)

        try:
            # Extract color palette
            palette = extract_color_palette(temp_path)

            # Convert to response format
            colors = [
                ColorPalette(color=color.tolist(), percentage=percentage)
                for color, percentage in palette
            ]

            return ColorExtractionResponse(colors=colors)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Color extraction failed: {str(e)}"
        )


@app.post("/v1/auth/google", response_model=AuthResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    try:
        db_manager = get_db_manager()
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")

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
        logger.exception("Authentication failed: {error}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


def get_sql_dep() -> AsyncSQLConnector:
    # You can pass a connection string OR leave None to resolve from env/Cloud SQL.
    return get_async_sql_connector(SQL_CONNECTION_STRING)


@app.post("/v2/auth/google", response_model=AuthResponse)
async def google_auth_v2(
    auth_request: GoogleAuthRequest,
    sql=Depends(get_sql_dep),
) -> AuthResponse:
    try:
        idinfo = id_token.verify_oauth2_token(
            auth_request.token, requests.Request(), GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    iss = idinfo.get("iss")
    if iss not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=401, detail="Invalid token issuer")

    if not idinfo.get("email"):
        raise HTTPException(status_code=401, detail="Email missing in token")

    if not idinfo.get("email_verified", False):
        raise HTTPException(status_code=401, detail="Email not verified")

    auth_provider_id = idinfo["sub"]
    email = idinfo["email"]
    name = idinfo.get("name")
    picture_url = idinfo.get("picture")

    # 2) Upsert + fetch user in a single transaction
    try:
        async with sql.transaction() as session:
            upsert_query = """
                INSERT INTO account (auth_provider_id, auth_provider, email, name, picture_url, created_at, last_login)
                VALUES (:auth_provider_id, :auth_provider, :email, :name, :picture_url, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON DUPLICATE KEY UPDATE
                    email = VALUES(email),
                    name = VALUES(name),
                    picture_url = VALUES(picture_url),
                    last_login = CURRENT_TIMESTAMP
            """
            await session.execute(
                text(upsert_query),
                {
                    "auth_provider_id": auth_provider_id,
                    "email": email,
                    "name": name,
                    "picture_url": picture_url,
                    "auth_provider": "google",
                },
            )

            select_query = """
                SELECT id, auth_provider_id, email, name, picture_url
                FROM account
                WHERE auth_provider_id = :auth_provider_id
                LIMIT 1
            """
            result = await session.execute(
                text(select_query), {"auth_provider_id": auth_provider_id}
            )
            row = result.mappings().first()
            if not row:
                raise HTTPException(status_code=500, detail="User fetch failed")
            user = dict(row)
            logger.info(
                "User login/upsert successful for google_id={}", auth_provider_id
            )

            jwt_token = jwt.encode(
                {
                    "auth_provider_id": str(user["auth_provider_id"]),
                    "email": user["email"],
                    "name": user["name"],
                    "picture": user.get("picture_url"),
                    "exp": datetime.utcnow() + timedelta(days=7),
                },
                GOOGLE_CLIENT_SECRET,
                algorithm="HS256",
            )

            # 4) Return user info
            return AuthResponse(
                token=jwt_token,
                user=UserResponse(
                    id=str(user["auth_provider_id"]),
                    email=user["email"],
                    name=user.get("name"),
                    picture=user.get("picture_url"),
                ),
            )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Authentication failed")
        # Do not leak raw errors to clients
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.get("/account/{google_id}")
async def get_account(
    google_id: str,
    sql: AsyncSQLConnector = Depends(lambda: get_async_sql_connector(None)),
):
    row = await sql.fetch_one(
        """
        SELECT id, google_id, email, name, picture
        FROM account
        WHERE google_id = :google_id
        LIMIT 1
        """,
        {"google_id": google_id},
    )
    if not row:
        raise HTTPException(404, "Not found")
    return row


@app.get("/v1/images/{image_path:path}")
async def get_image(image_path: str):
    """Serve images from Google Cloud Storage"""
    try:
        gcs_service = get_gcs_service_instance()
        if not gcs_service:
            raise HTTPException(status_code=503, detail="Storage service not available")
        # Construct full GCS path (add "images/" prefix back)
        logger.debug("Loading image from {path}", path=image_path)
        image = gcs_service.load_image(image_path)
        logger.debug("Image loaded")
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
        logger.exception("Image not found: {error}", error=str(e))
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")


@app.get("/v1/proxy/avatar")
async def proxy_avatar(url: str):
    """Proxy external avatar images (e.g., Google) to avoid third-party rate limits.

    Only allows specific trusted hosts to prevent SSRF.
    """
    try:
        parsed = urlparse(url)
        allowed_hosts = {
            "lh3.googleusercontent.com",
            "lh4.googleusercontent.com",
            "lh5.googleusercontent.com",
            "lh6.googleusercontent.com",
            "play-lh.googleusercontent.com",
        }
        if parsed.scheme not in {"http", "https"} or parsed.netloc not in allowed_hosts:
            raise HTTPException(status_code=400, detail="Invalid avatar host")

        # Fetch the remote image
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; GreenFashion/1.0)",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            data = resp.read()

        return StreamingResponse(
            io.BytesIO(data),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Avatar proxy failed: {error}", error=str(e))
        raise HTTPException(status_code=502, detail=f"Failed to fetch avatar: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up Green Fashion API")
    initialize_services()
    logger.info("Services initialized, API ready to serve requests")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
