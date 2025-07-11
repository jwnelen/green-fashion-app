import traceback

import streamlit as st
import torch
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
    st.markdown("Upload a fashion image and specify categories for classification")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader(
            "Choose a fashion image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload an image of clothing or fashion items",
        )

        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", width=300)
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                return

    with col2:
        st.subheader("Classification Categories")

        preset_categories = st.selectbox(
            "Choose preset categories or create custom:",
            [
                "Custom",
                "Basic Clothing Types",
                "Formal vs Casual",
                "Seasonal Wear",
                "Gender Categories",
            ],
        )

        if preset_categories == "Basic Clothing Types":
            default_cats = "t-shirt, dress, jeans, jacket, shoes, accessories"
        elif preset_categories == "Formal vs Casual":
            default_cats = "formal wear, casual wear, sportswear, business attire"
        elif preset_categories == "Seasonal Wear":
            default_cats = (
                "summer clothing, winter clothing, spring outfit, fall fashion"
            )
        elif preset_categories == "Gender Categories":
            default_cats = "men's fashion, women's fashion, unisex clothing"
        else:
            default_cats = "casual t-shirt, formal dress, vintage jacket, modern shoes"

        custom_categories = st.text_area(
            "Enter categories (comma-separated):",
            value=default_cats,
            height=100,
            help="List the fashion categories you want to classify against",
        )

        categories = [
            cat.strip() for cat in custom_categories.split(",") if cat.strip()
        ]

        if len(categories) > 10:
            st.warning(
                "Too many categories may slow down processing. Consider using fewer than 10."
            )

        st.info(f"Categories to classify: {len(categories)}")

    if (
        uploaded_file
        and categories
        and st.button("🔍 Classify Fashion Item", type="primary")
    ):
        with st.spinner("Analyzing fashion item..."):
            try:
                image = Image.open(uploaded_file)
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
        1. **Upload an image** of clothing or fashion items
        2. **Choose categories** either from presets or create your own
        3. **Click Classify** to analyze the fashion item
        4. **View results** ranked by confidence score

        **Tips:**
        - Use clear, well-lit images for better results
        - Be specific with category names (e.g., "red summer dress" vs "dress")
        - Try different category combinations to explore the model's understanding
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


if __name__ == "__main__":
    main()
