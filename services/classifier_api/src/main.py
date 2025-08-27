import time
from functools import lru_cache

import torch
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from green_fashion.clothing.config import CLOTHING_CATEGORIES
from green_fashion.logging_utils import (
    setup_logging,
    logger,
    request_context_middleware,
)

# Initialize logging early
setup_logging(service_name="classifier_api")

app = FastAPI(
    title="Green Fashion Clothing Classifier API",
    description="API for clothing classification",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_context_middleware)

use_small_model = True
if use_small_model:
    precision = torch.float16
else:
    precision = torch.float32


@app.get("/")
async def root():
    return {"message": "Green Fashion Wardrobe API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


def preprocess_image(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    max_size = 512
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    return image


@lru_cache(maxsize=1)
def get_cached_model():
    """Load and cache the fashion model using LRU cache"""
    try:
        torch.set_num_threads(1)
        device = "cpu"
        model_name = "patrickjohncyh/fashion-clip"

        model = CLIPModel.from_pretrained(
            model_name, torch_dtype=precision, device_map=None, low_cpu_mem_usage=True
        ).to(device)

        model.eval()

        processor = CLIPProcessor.from_pretrained(model_name, use_fast=False)

        logger.info(
            "Model loaded successfully with {precision}", precision=str(precision)
        )
        return model, processor, device

    except Exception as e:
        logger.exception("Failed to load model: {error}", error=str(e))
        return None, None, None


@app.post("/classify")
async def classify_item(file: UploadFile = File(...)):
    start_time = time.time()

    try:
        model, processor, device = get_cached_model()

        if model is None or processor is None:
            raise HTTPException(status_code=503, detail="Model was empty")

        category_prompts = [f"a photo of {cat.strip()}" for cat in CLOTHING_CATEGORIES]

        if not file:
            return {"message": "image not provided"}

        image = Image.open(file.file)
        images = preprocess_image(image)

        with torch.no_grad():
            inputs = processor(
                text=category_prompts,
                images=images,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77,
            )

            for key in inputs:
                if torch.is_tensor(inputs[key]):
                    inputs[key] = inputs[key].to(device)

            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = torch.softmax(logits_per_image, dim=1)

            results = []
            for i, category in enumerate(CLOTHING_CATEGORIES):
                results.append(
                    {"label": category.strip(), "confidence": float(probs[0][i].cpu())}
                )

            # Sort by confidence and return the highest
            results.sort(key=lambda x: x["confidence"], reverse=True)

            processing_time = time.time() - start_time
            logger.info(
                "Classification completed in {elapsed:.3f}s", elapsed=processing_time
            )

            return {"message": results[0]["label"]}

    except Exception as e:
        logger.exception("Classification failed: {error}", error=str(e))
        raise HTTPException(status_code=503, detail="Loading model failed")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
