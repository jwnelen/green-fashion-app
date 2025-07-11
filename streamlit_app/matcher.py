import json
import os
from pathlib import Path

import streamlit as st
from PIL import Image

from clothing.piece_mapper import section_to_name  # Import the section_to_name mapping
from color_extracting.color_palette_extractor import plot_palette


@st.cache_data
def load_dataset(file_path):
    return json.load(open(file_path, "r"))


def display_images_by_section(image_data):
    body_sections = section_to_name.keys()

    for section in sorted(body_sections):
        section_name = section_to_name.get(section, str(section))
        st.subheader(f"{section_name}")

        # filter dict
        filtered_data = [
            item for item in image_data if item.get("body_section") == section
        ]

        max_images = 20
        image_paths = [item["path"] for item in filtered_data]
        image_paths = image_paths[:max_images]

        if not image_paths or len(image_paths) == 0:
            st.warning(f"No images found for {section_name}.")
            continue

        num_cols = 5
        cols = st.columns(min(len(image_paths), num_cols))

        for idx, image_path in enumerate(image_paths):
            col_idx = idx % num_cols

            with cols[col_idx]:
                if os.path.exists(image_path):
                    try:
                        image = Image.open(image_path)
                        local_image_data = [
                            x for x in filtered_data if x["path"] == image_path
                        ][0]
                        if not local_image_data:
                            st.error(f"No local data found for {image_path}")
                            continue

                        if local_image_data:
                            # display_name = local_image_data["display_name"]
                            st.image(image, use_container_width=True)
                            palette = local_image_data.get("colors", [])
                            fig = plot_palette(palette)
                            st.pyplot(fig, clear_figure=True)

                    except Exception as e:
                        st.error(f"Error loading image {image_path}: {str(e)}")
                else:
                    st.error(f"Image not found: {image_path}")


def main():
    st.set_page_config(page_title="Image Gallery by Body Section", layout="wide")
    st.title("Image Gallery by Body Section")

    full_path = Path(__file__).resolve().parents[1]
    data_folder = full_path / "artifacts" / "datasets"

    df = load_dataset(data_folder / "dataset_all_colors_parsed.json")
    st.success(f"Loaded {len(df)} records")

    # if st.checkbox("Show dataframe preview"):
    #     st.dataframe(df.head())

    st.divider()
    display_images_by_section(df)


if __name__ == "__main__":
    main()
