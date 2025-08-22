import io
from collections import Counter

import numpy as np
from PIL import Image
from rembg import remove
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler


def extract_color_palette(_image_path, resize_width=150, alpha_threshold=128):
    image = Image.open(_image_path)
    image = remove_background(image)

    print("hello world")

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    original_width, original_height = image.size
    aspect_ratio = original_height / original_width
    resize_height = int(resize_width * aspect_ratio)
    image = image.resize((resize_width, resize_height), Image.Resampling.LANCZOS)

    pixels_rgba = np.array(image).reshape(-1, 4)

    # Getting the correct htreshold
    foreground_mask = pixels_rgba[:, 3] > alpha_threshold

    if not np.any(foreground_mask):
        print("Warning: No foreground pixels found. Lowering alpha threshold.")
        foreground_mask = pixels_rgba[:, 3] > 64  # Fallback threshold

    if not np.any(foreground_mask):
        print(
            "Warning: Still no foreground pixels found. Using all non-zero alpha pixels."
        )
        foreground_mask = pixels_rgba[:, 3] > 0

    pixels = pixels_rgba[foreground_mask][:, :3]

    scaler = StandardScaler()
    pixels_scaled = scaler.fit_transform(pixels)

    clustering = AgglomerativeClustering(
        n_clusters=None, distance_threshold=100, linkage="ward"
    )
    labels = clustering.fit_predict(pixels_scaled)

    unique_labels = np.unique(labels)
    colors = np.array(
        [pixels[labels == label].mean(axis=0) for label in unique_labels]
    ).astype(int)

    color_counts = Counter(labels)
    color_percentages = [(count / len(labels)) * 100 for count in color_counts.values()]

    palette = list(zip(colors, color_percentages))
    palette.sort(key=lambda x: x[1], reverse=True)

    return palette


def remove_background(image: Image.Image) -> Image.Image:
    # Convert PIL image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    # Remove background and return as PIL Image
    result = remove(img_byte_arr)
    return Image.open(io.BytesIO(result))


# def plot_palette(palette, selected_indices=None):
#     if selected_indices is None:
#         selected_indices = {}

#     fig, ax = plt.subplots()
#     palette_height = 5
#     palette_width = 20
#     palette_img = np.zeros((palette_height, palette_width, 3), dtype=np.uint8)

#     x_start = 0
#     sections = []

#     for i, pair in enumerate(palette):
#         color_values = pair[0]
#         # if isinstance(color, str):
#         #     color = [
#         #         int(c) for c in color.replace("rgb(", "").replace(")", "").split(",")
#         #     ]
#         # color = np.array(color, dtype=np.uint8)
#         percentage = pair[1]
#         if i == len(palette) - 1:
#             section_width = palette_width - x_start
#         else:
#             section_width = int(palette_width * percentage / 100)

#         palette_img[:, x_start : x_start + section_width] = color_values
#         sections.append((x_start, x_start + section_width, i))
#         x_start += section_width

#     ax.imshow(palette_img)

#     for x_start, x_end, i in sections:
#         if i in selected_indices:
#             rect = plt.Rectangle(
#                 (x_start - 0.5, -0.5),
#                 x_end - x_start,
#                 palette_height,
#                 fill=False,
#                 edgecolor="blue",
#                 linewidth=3,
#             )
#             ax.add_patch(rect)

#     ax.set_title("Color Palette")
#     ax.axis("off")

#     return fig


# def display_palette(single_image_path, n_colors=5):
#     st.subheader("Extracted Color Palette")
#     palette = extract_color_palette(single_image_path, n_colors=n_colors)

#     if f"selected_colors_{single_image_path}" not in st.session_state:
#         st.session_state[f"selected_colors_{single_image_path}"] = {0}

#     selected_colors = st.session_state[f"selected_colors_{single_image_path}"]

#     cols = st.columns(len(palette))
#     for i, (color, percentage) in enumerate(palette):
#         with cols[i]:
#             is_selected = i in selected_colors

#             if st.checkbox(
#                 f"Color {i + 1}",
#                 value=is_selected,
#                 key=f"color_{single_image_path}_{i}",
#             ):
#                 selected_colors.add(i)
#             else:
#                 selected_colors.discard(i)

#     fig = plot_palette(palette, selected_colors)
#     st.pyplot(fig, clear_figure=True)
#     plt.close(fig)  # Close the figure to free memory
