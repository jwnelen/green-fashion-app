import json
import os
import random
from pathlib import Path

import streamlit as st
from PIL import Image

from clothing.piece_mapper import section_to_name  # Import the section_to_name mapping
from color_extracting.color_palette_extractor import plot_palette


@st.cache_data
def load_dataset(file_path):
    return json.load(open(file_path, "r"))


def generate_outfit(image_data):
    """Generate a random outfit by selecting one item from each available body section."""
    # Group items by body section
    sections = {}
    for item in image_data:
        section = item.get("body_section")
        if section not in sections:
            sections[section] = []
        sections[section].append(item)

    outfit = []

    # Randomly choose between full body outfit or separate pieces
    has_full_body = 3 in sections and sections[3]
    has_upper_lower = (1 in sections and sections[1]) or (2 in sections and sections[2])

    # If both options are available, randomly choose
    use_full_body = False
    if has_full_body and has_upper_lower:
        use_full_body = random.choice([True, False])
    elif has_full_body:
        use_full_body = True

    if use_full_body:
        # Use full body item (dress)
        full_body_item = random.choice(sections[3])
        outfit.append(full_body_item)
    else:
        # Create outfit with separate upper and lower body items
        # Add upper body item if available
        if 1 in sections and sections[1]:
            upper_item = random.choice(sections[1])
            outfit.append(upper_item)

        # Add lower body item if available
        if 2 in sections and sections[2]:
            lower_item = random.choice(sections[2])
            outfit.append(lower_item)

    # Always add shoes and head accessories when available
    if 4 in sections and sections[4]:
        shoes = random.choice(sections[4])
        outfit.append(shoes)

    if 0 in sections and sections[0]:
        head_item = random.choice(sections[0])
        outfit.append(head_item)

    return outfit


def display_outfit(outfit):
    """Display the generated outfit with images and color palettes."""
    if not outfit:
        st.warning("No outfit could be generated with the available items.")
        return

    st.subheader("Generated Outfit")

    # Create columns for each outfit piece
    num_cols = len(outfit)
    cols = st.columns(num_cols)

    for idx, item in enumerate(outfit):
        with cols[idx]:
            section_name = section_to_name.get(
                item["body_section"], f"Section {item['body_section']}"
            )
            st.write(f"**{section_name}**: {item['category']}")

            if os.path.exists(item["path"]):
                try:
                    image = Image.open(item["path"])
                    st.image(image, use_container_width=True)

                    # Display color palette
                    palette = item.get("colors", [])
                    if palette:
                        fig = plot_palette(palette)
                        st.pyplot(fig, clear_figure=True)
                        fig.clf()  # Clear the figure to free memory

                except Exception as e:
                    st.error(f"Error loading image {item['path']}: {str(e)}")
            else:
                st.error(f"Image not found: {item['path']}")


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
                            fig.clf()  # Clear the figure to free memory

                    except Exception as e:
                        st.error(f"Error loading image {image_path}: {str(e)}")
                else:
                    st.error(f"Image not found: {image_path}")


def main():
    st.set_page_config(page_title="Green Fashion Outfit Generator", layout="wide")
    st.title("Green Fashion Outfit Generator")

    full_path = Path(__file__).resolve().parents[1]
    data_folder = full_path / "artifacts" / "datasets"

    df = load_dataset(data_folder / "dataset_all_colors_parsed.json")

    st.success(f"Loaded {len(df)} records")

    # Outfit Generator Section
    st.header("Outfit Generator")
    st.write("Generate a complete outfit from the available clothing pieces!")

    # Initialize session state for outfit if it doesn't exist
    if "current_outfit" not in st.session_state:
        st.session_state.current_outfit = None

    # Generate Outfit Button
    if st.button("🎲 Generate New Outfit", type="primary"):
        st.session_state.current_outfit = generate_outfit(df)

    # Display current outfit if one exists
    if st.session_state.current_outfit:
        display_outfit(st.session_state.current_outfit)

    st.divider()
    st.subheader("Dataset Overview")
    with st.expander("View all clothing pieces by section"):
        display_images_by_section(df)


if __name__ == "__main__":
    main()
