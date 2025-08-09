from typing import Dict, List

import streamlit as st

from green_fashion.database.config import CLOTHING_CATEGORIES
from green_fashion.database.mongodb_manager import MongoDBManager
from green_fashion.storage.gcs_service import get_gcs_service

# class StreamlitWardrobeManager(WardrobeManager):
#     """Extended WardrobeManager with Streamlit-specific error handling."""

#     def add_clothing_item(self, item_data):
#         try:
#             return super().add_clothing_item(item_data)
#         except Exception as e:
#             st.error(f"Error adding item: {str(e)}")
#             return None

#     def get_all_items(self):
#         try:
#             return super().get_all_items()
#         except Exception as e:
#             st.error(f"Error fetching items: {str(e)}")
#             return []

#     def update_item(self, item_id, updates):
#         try:
#             return super().update_item(item_id, updates)
#         except Exception as e:
#             st.error(f"Error updating item: {str(e)}")
#             return False

#     def delete_item(self, item_id):
#         try:
#             return super().delete_item(item_id)
#         except Exception as e:
#             st.error(f"Error deleting item: {str(e)}")
#             return False

#     def search_items(self, query):
#         try:
#             return super().search_items(query)
#         except Exception as e:
#             st.error(f"Error searching items: {str(e)}")
#             return []

#     def save_uploaded_image(self, uploaded_file, category):
#         try:
#             return super().save_uploaded_image(uploaded_file, category)
#         except Exception as e:
#             st.error(f"Error saving image: {str(e)}")
#             return None


@st.dialog("Confirm Delete")
def confirm_delete(item):
    """Delete confirmation dialog"""
    st.warning("⚠️ Are you sure you want to delete this item?")
    st.write(
        f"**Item:** {item.get('custom_name', item.get('display_name', 'Unnamed'))}"
    )
    st.write(f"**Category:** {item.get('category', 'Unknown')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete", type="primary", use_container_width=True):
            st.session_state.delete_confirmed = item["_id"]
            st.session_state.deleted_item_name = item.get(
                "custom_name", item.get("display_name", "Unnamed")
            )
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def display_color_palette(colors: List[Dict]):
    """Display color palette as colored squares"""
    cols = st.columns(len(colors))
    for i, color_info in enumerate(colors):
        with cols[i]:
            color = color_info["color"]
            percentage = color_info["percentage"]
            # Convert rgb string to hex
            rgb_values = color.replace("rgb(", "").replace(")", "").split(", ")
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2])
            )
            st.markdown(
                f'<div style="background-color: {hex_color}; height: 50px; width: 100%; '
                f'border-radius: 5px; margin: 2px;"></div>'
                f'<p style="text-align: center; font-size: 10px; margin: 0;">{percentage:.1f}%</p>',
                unsafe_allow_html=True,
            )


def main():
    st.set_page_config(page_title="Wardrobe Manager", page_icon="👗", layout="wide")

    st.title("👗 Personal Wardrobe Manager")
    st.markdown("Manage your clothing collection with custom names and MongoDB storage")

    # Initialize wardrobe manager
    db = MongoDBManager()

    # Check database connection
    if not db.client:
        st.error("❌ Failed to connect to MongoDB")

        # Show detailed error information
        if hasattr(db, "connection_error") and db.connection_error:
            with st.expander("🔍 Connection Error Details"):
                st.code(db.connection_error)

        # Add retry button
        if st.button("🔄 Retry Connection"):
            st.rerun()

        st.stop()
    else:
        st.success("✅ Connected to MongoDB successfully!")

    # Ensure wardrobe images directory exists
    gcs = get_gcs_service()
    st.write(gcs.bucket.name)

    # Sidebar for navigation
    st.sidebar.header("Navigation")

    if "current_page" not in st.session_state:
        st.session_state.current_page = "View Wardrobe"

    if st.sidebar.button("👗 View Wardrobe", use_container_width=True):
        st.session_state.current_page = "View Wardrobe"

    # if st.sidebar.button("📥 Import from Dataset", use_container_width=True):
    #     st.session_state.current_page = "Import from Dataset"

    # if st.sidebar.button("🔍 Search Items", use_container_width=True):
    #     st.session_state.current_page = "Search Items"

    if st.sidebar.button("➕ Add New Item", use_container_width=True):
        st.session_state.current_page = "Add New Item"

    action = st.session_state.current_page

    # Only execute page logic for the current action to improve performance
    if action == "View Wardrobe":
        st.header("📦 Your Wardrobe")

        # Handle delete confirmation from dialog
        if "delete_confirmed" in st.session_state:
            item_id = st.session_state.delete_confirmed
            item_name = st.session_state.deleted_item_name

            # First get the item to find its image path
            item = None
            all_items = db.get_all_items()
            for i in all_items:
                if i["_id"] == item_id:
                    item = i
                    break

            if db.delete_item(item_id):
                # Delete image from GCS if it exists
                if item and item.get("path"):
                    try:
                        gcs.delete_image(item["path"])
                    except Exception as e:
                        st.warning(f"Failed to delete image from storage: {str(e)}")

                # Refresh the cached items after deletion
                st.session_state["refresh_items"] = True
                st.session_state["delete_success"] = f"'{item_name}' deleted!"
            del st.session_state.delete_confirmed
            del st.session_state.deleted_item_name
            st.rerun()

        # Display delete success message if any
        if "delete_success" in st.session_state:
            st.success(st.session_state["delete_success"])
            del st.session_state["delete_success"]

        # Cache items in session state to avoid repeated DB calls
        if (
            "wardrobe_items" not in st.session_state
            or "refresh_items" in st.session_state
        ):
            st.session_state.wardrobe_items = db.get_all_items()
            if "refresh_items" in st.session_state:
                del st.session_state.refresh_items

        items = st.session_state.wardrobe_items
        if not items:
            st.info(
                "Your wardrobe is empty. Import items from the dataset or add new ones!"
            )
            return

        # Filter by category
        categories = list(set([item.get("category", "Unknown") for item in items]))
        selected_category = st.selectbox("Filter by category", ["All"] + categories)

        if selected_category != "All":
            items = [
                item for item in items if item.get("category") == selected_category
            ]

        st.write(f"Found {len(items)} items")

        # Display items in a grid
        cols_per_row = 4
        for i in range(0, len(items), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(items):
                    item = items[i + j]
                    with col:
                        # Display image with lazy loading using expander
                        image_container = st.container()
                        with image_container:
                            if item.get("path"):
                                # Cache loaded images in session state
                                image_key = f"image_{item['_id']}"
                                if image_key not in st.session_state:
                                    try:
                                        st.session_state[image_key] = gcs.load_image(
                                            item["path"]
                                        )
                                    except Exception:
                                        st.session_state[image_key] = None

                                if st.session_state[image_key] is not None:
                                    st.image(
                                        st.session_state[image_key],
                                        use_container_width=True,
                                    )
                                else:
                                    st.write("🖼️ Image not available")
                            else:
                                st.write("🖼️ No image")

                        # Item details and editing
                        # Custom name input
                        current_name = item.get(
                            "custom_name", item.get("display_name", "Unnamed")
                        )
                        new_name = st.text_input(
                            "Custom Name:",
                            value=current_name,
                            key=f"name_{item['_id']}",
                        )

                        # Category selection
                        categories = CLOTHING_CATEGORIES
                        current_category = item.get("category", "other")
                        new_category = st.selectbox(
                            "Category:",
                            categories,
                            index=(
                                categories.index(current_category)
                                if current_category in categories
                                else categories.index("other")
                            ),
                            key=f"category_{item['_id']}",
                        )

                        # Display success messages if any
                        if f"success_msg_{item['_id']}" in st.session_state:
                            st.success(st.session_state[f"success_msg_{item['_id']}"])
                            del st.session_state[f"success_msg_{item['_id']}"]

                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Save Changes", key=f"save_{item['_id']}"):
                                updates = {}
                                if new_name != current_name:
                                    updates["custom_name"] = new_name
                                if new_category != current_category:
                                    updates["category"] = new_category

                                if updates:
                                    if db.update_item(item["_id"], updates):
                                        # Refresh the cached items after update
                                        st.session_state["refresh_items"] = True
                                        st.session_state[
                                            f"success_msg_{item['_id']}"
                                        ] = "Changes saved!"
                                        st.rerun()
                                else:
                                    st.info("No changes to save.")

                        with col2:
                            if st.button(
                                "Delete", key=f"delete_{item['_id']}", type="secondary"
                            ):
                                confirm_delete(item)

                        # Display colors if available
                        if item.get("colors"):
                            st.write("**Colors:**")
                            display_color_palette(
                                item["colors"][:5]
                            )  # Show top 5 colors

                        st.markdown("---")

    # elif action == "Import from Dataset":
    #     st.header("📥 Import from Dataset")

    #     dataset_items = DataLoader.load_and_clean_dataset()
    #     if not dataset_items:
    #         st.error("No dataset items found or failed to load dataset.")
    #         return

    #     st.write(f"Found {len(dataset_items)} items in dataset")

    #     # Show preview
    #     if st.checkbox("Show preview"):
    #         preview_item = dataset_items[0] if dataset_items else {}
    #         st.json(preview_item)

    #     if st.button("Import All Items"):
    #         progress_bar = st.progress(0)

    #         with st.spinner("Importing items..."):
    #             imported_count = 0
    #             for i, item in enumerate(dataset_items):
    #                 # Use the database manager's method to check for existing items
    #                 if wm.add_clothing_item(item):
    #                     imported_count += 1
    #                 progress_bar.progress((i + 1) / len(dataset_items))

    #         st.success(f"Successfully imported {imported_count} new items!")
    #         if imported_count < len(dataset_items):
    #             st.info(
    #                 f"{len(dataset_items) - imported_count} items were already in the database or failed to import."
    #             )

    # elif action == "Search Items":
    #     st.header("🔍 Search Items")

    #     search_query = st.text_input("Search by name, category, or filename:")

    #     if search_query:
    #         results = wm.search_items(search_query)
    #         st.write(f"Found {len(results)} items matching '{search_query}'")

    #         for item in results:
    #             with st.expander(
    #                 f"{item.get('custom_name', item.get('display_name', 'Unnamed'))} - {item.get('category', 'Unknown')}"
    #             ):
    #                 col1, col2 = st.columns([1, 2])

    #                 with col1:
    #                     if item.get("path") and os.path.exists(item["path"]):
    #                         try:
    #                             image = Image.open(item["path"])
    #                             st.image(image, width=200)
    #                         except Exception:
    #                             st.write("🖼️ Image not available")

    #                 with col2:
    #                     st.write(f"**Category:** {item.get('category', 'Unknown')}")
    #                     st.write(
    #                         f"**Body Section:** {item.get('body_section', 'Unknown')}"
    #                     )
    #                     st.write(f"**File:** {item.get('display_name', 'Unknown')}")

    #                     if item.get("colors"):
    #                         st.write("**Colors:**")
    #                         display_color_palette(item["colors"][:5])

    elif action == "Add New Item":
        st.header("➕ Add New Item")

        with st.form("add_item_form"):
            custom_name = st.text_input(
                "Item Name*", placeholder="e.g., Blue Summer Dress"
            )
            category = st.selectbox("Category*", CLOTHING_CATEGORIES)
            body_section = st.selectbox(
                "Body Section*",
                [("Head", 0), ("Upper Body", 1), ("Lower Body", 2), ("Feet", 3)],
                format_func=lambda x: x[0],
            )

            uploaded_file = st.file_uploader(
                "Upload Image", type=["png", "jpg", "jpeg"]
            )

            notes = st.text_area("Notes (optional)")

            submitted = st.form_submit_button("Add Item")

            if submitted:
                if not custom_name:
                    st.error("Please provide an item name.")
                else:
                    # Handle file upload first
                    image_path = None
                    if uploaded_file:
                        image_path = gcs.save_image(
                            image=uploaded_file,
                            filename=custom_name.replace(" ", "_").lower(),
                            category="wardrobe",
                        )
                        if not image_path:
                            st.error("Failed to save image. Please try again.")
                            return

                    item_data = {
                        "custom_name": custom_name,
                        "category": category,
                        "body_section": body_section[1],
                        "notes": notes,
                        "colors": [],  # Could be populated with color extraction
                        "display_name": (
                            uploaded_file.name if uploaded_file else custom_name
                        ),
                        "path": image_path,
                    }

                    result = db.add_clothing_item(item_data)
                    if result:
                        # Refresh the cached items after adding new item
                        st.session_state["refresh_items"] = True
                        st.success("Item added successfully!")
                        if image_path:
                            st.success(f"Image saved to: {image_path}")
                    else:
                        st.error(
                            "Failed to add item. Please check the database connection."
                        )
                        # Clean up image if item creation failed
                        if image_path:
                            gcs.delete_image(image_path)


if __name__ == "__main__":
    main()
