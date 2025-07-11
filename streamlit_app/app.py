import traceback
from pathlib import Path

import streamlit as st
import torch
from config import CLOTHING_CATEGORIES
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

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
def load_image_paths(data_folder="artifacts/data"):
    image_paths = []
    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

    full_path = Path(__file__).resolve().parents[1]
    data_path = full_path / data_folder
    if not data_path.exists():
        return []

    for subfolder in data_path.iterdir():
        if subfolder.is_dir():
            for image_file in subfolder.iterdir():
                if image_file.suffix.lower() in image_extensions:
                    image_paths.append(
                        {
                            "path": str(image_file),
                            "display_name": f"{subfolder.name}/{image_file.name}",
                            "category": subfolder.name,
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
        st.code(traceback.format_exc())
        return []


def main():
    st.title("🛍️ Fashion Classification App")
    st.markdown("Select a fashion image from the dataset and classify it")

    image_paths = load_image_paths()

    if not image_paths:
        st.error(
            "No images found in the 'data' folder. Please ensure the folder exists and contains image files."
        )
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Select Image")

        selected_image_info = st.selectbox(
            "Choose an image",
            options=image_paths,
            format_func=lambda x: x["display_name"],
            help="Select an image from the dataset",
        )

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
        st.subheader("Classification Categories")
        categories = CLOTHING_CATEGORIES

        if len(categories) > 15:
            st.warning(
                "Too many categories may slow down processing. Consider using fewer than 10."
            )

        st.info(f"Categories to classify: {len(categories)}")

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
                    st.subheader("📊 Classification Results")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        for i, result in enumerate(results[:5]):
                            confidence_pct = result["confidence"] * 100

                            if i == 0:
                                st.success(f"**Best Match: {result['label']}**")

                            st.metric(
                                label=f"#{i + 1} {result['label']}",
                                value=f"{confidence_pct:.1f}%",
                            )

                            st.progress(result["confidence"])

                    with col2:
                        st.subheader("All Results")
                        for result in results:
                            st.write(
                                f"• {result['label']}: {result['confidence'] * 100:.1f}%"
                            )

                    if st.checkbox("Show detailed analysis"):
                        st.subheader("🔍 Detailed Analysis")
                        st.json({r["label"]: f"{r['confidence']:.4f}" for r in results})

            except Exception as e:
                st.error(f"Error during classification: {str(e)}")

    with st.expander("ℹ️ How to use this app"):
        st.markdown(
            """
        1. **Select an image** from the dropdown menu (organized by category folders)
        2. **View the selected image** and its category folder
        3. **Click Classify** to analyze the fashion item
        4. **View results** ranked by confidence score

        **Tips:**
        - Images are organized by category folders in the 'data' directory
        - The dropdown shows the folder structure for easy navigation
        - Try different images to see how the model performs across categories
        """
        )

    with st.expander("🤖 Model Information"):
        st.markdown(
            """
        This app uses **Fashion-CLIP**, a specialized model trained on fashion data that can:
        - Understand fashion-specific terminology
        - Classify items with custom categories
        - Handle various clothing types and styles

        **Model:** `patrickjohncyh/fashion-clip`
        **Architecture:** CLIP (Vision + Language)
        **Training:** 800K+ fashion image-text pairs
        """
        )

    with st.expander("📁 Dataset Information"):
        if image_paths:
            categories_count = {}
            for img_info in image_paths:
                category = img_info["category"]
                categories_count[category] = categories_count.get(category, 0) + 1

            st.markdown("**Available categories and image counts:**")
            for category, count in sorted(categories_count.items()):
                st.write(f"• {category}: {count} images")

            st.write(f"**Total images:** {len(image_paths)}")


if __name__ == "__main__":
    main()
