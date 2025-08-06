from pathlib import Path

import streamlit as st
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from green_fashion.clothing.config import CLOTHING_CATEGORIES
from green_fashion.color_extracting.color_palette_extractor import display_palette

st.set_page_config(page_title="Fashion Classifier", layout="wide")

use_small_model = True
if use_small_model:
    precision = torch.float16
else:
    precision = torch.float32


@st.cache_resource
def load_fashion_model():
    try:
        torch.set_num_threads(1)
        device = "cpu"
        model_name = "patrickjohncyh/fashion-clip"

        model = CLIPModel.from_pretrained(
            model_name, torch_dtype=precision, device_map=None
        ).to(device)
        model.eval()

        processor = CLIPProcessor.from_pretrained(model_name)

        return model, processor, device

    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None, None, None


@st.cache_data
def load_image_paths(category, data_folder="artifacts/images"):
    image_paths = []
    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

    full_path = Path(__file__).resolve().parents[1]
    data_path = full_path / data_folder / category
    if not data_path.exists():
        return []

    for image_file in data_path.iterdir():
        if image_file.suffix.lower() in image_extensions:
            image_paths.append(
                {
                    "path": str(image_file),
                    "display_name": f"{image_file.name}",
                    "category": data_path.name,
                }
            )

    return sorted(image_paths, key=lambda x: x["display_name"])


def preprocess_image(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    max_size = 512
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    return image


def classify_fashion_image(image, categories):
    try:
        model, processor, device = load_fashion_model()

        if model is None:
            return []

        image = preprocess_image(image)
        category_prompts = [f"a photo of {cat.strip()}" for cat in categories]

        with torch.no_grad():
            inputs = processor(
                text=category_prompts,
                images=image,
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
            for i, category in enumerate(categories):
                results.append(
                    {"label": category.strip(), "confidence": float(probs[0][i].cpu())}
                )

            return sorted(results, key=lambda x: x["confidence"], reverse=True)

    except Exception as e:
        st.error(f"Classification error: {str(e)}")
        return []


def main():
    st.sidebar.header("Settings", width="stretch")

    selected_fashion_category = st.sidebar.selectbox(
        "Select Fashion Category",
        options=CLOTHING_CATEGORIES,
        help="Choose a category to classify fashion items",
    )

    st.sidebar.write(f"Categories to classify: {len(CLOTHING_CATEGORIES)}")

    image_paths = load_image_paths(selected_fashion_category)

    if not image_paths:
        st.error(
            "No images found in the 'data' folder. Please ensure the folder exists and contains image files."
        )
        return

    st.subheader("Select Image")

    selected_image_info = st.sidebar.selectbox(
        "Choose an image",
        options=image_paths,
        format_func=lambda x: x["display_name"],
        help="Select an image from the dataset",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if selected_image_info:
            try:
                image = Image.open(selected_image_info["path"])
                st.image(
                    image,
                    caption=f"Selected: {selected_image_info['display_name']}",
                    width=300,
                )
                st.info(f"Category folder: {selected_image_info['category']}")
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                return

    with col2:
        categories = CLOTHING_CATEGORIES

        if selected_image_info:
            display_palette(selected_image_info["path"], n_colors=5)

        if (
            selected_image_info
            and categories
            and st.button("🔍 Classify Fashion Item", type="primary")
        ):
            with st.spinner("Analyzing fashion item..."):
                try:
                    image = Image.open(selected_image_info["path"])
                    results = classify_fashion_image(image, categories)

                    if results:
                        st.subheader("Classification Results")

                        for i, result in enumerate(results[:4]):
                            confidence_pct = result["confidence"] * 100
                            percentage_str = f"{confidence_pct:.1f}%"

                            st.write(
                                f"**{i + 1}. {result['label']} ({percentage_str})**",
                            )

                except Exception as e:
                    st.error(f"Error during classification: {str(e)}")


if __name__ == "__main__":
    main()
