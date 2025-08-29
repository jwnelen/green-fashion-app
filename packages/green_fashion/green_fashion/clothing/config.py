from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class BodySection(Enum):
    HEAD = "head"
    TORSO = "torso"
    ARMS = "arms"
    LEGS = "legs"
    FEET = "feet"


class WardrobeCategory(Enum):
    CLOTHING = "clothing"
    SHOES = "shoes"
    ACCESSORIES = "accessories"


@dataclass
class Category:
    slug: str
    name: str
    parent: Optional[WardrobeCategory | str] = None  # group enum or another slug
    covers: Set[BodySection] = field(default_factory=set)


# -------------------------
CATEGORIES: Dict[str, Category] = {}


def add(cat: Category):
    if cat.slug in CATEGORIES:
        raise ValueError(f"Duplicate slug: {cat.slug}")
    CATEGORIES[cat.slug] = cat


# Clothing
add(
    Category(
        "outerwear",
        "Outerwear",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.ARMS},
    )
)
add(
    Category(
        "tops-tshirts",
        "Tops & t-shirts",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO},
    )
)
add(
    Category(
        "suits-blazers",
        "Suits & blazers",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.ARMS},
    )
)
add(
    Category(
        "jumpers-sweaters",
        "Jumpers & sweaters",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.ARMS},
    )
)
add(
    Category(
        "trousers",
        "Trousers",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.LEGS},
    )
)
add(
    Category(
        "shorts", "Shorts", parent=WardrobeCategory.CLOTHING, covers={BodySection.LEGS}
    )
)
add(
    Category(
        "socks-underwear",
        "Socks & underwear",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.LEGS, BodySection.FEET},
    )
)
add(
    Category(
        "sleepwear",
        "Sleepwear",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.ARMS, BodySection.LEGS},
    )
)
add(
    Category(
        "activewear",
        "Activewear",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.ARMS, BodySection.LEGS},
    )
)
add(
    Category(
        "other-mens-clothing",
        "Other men's clothing",
        parent=WardrobeCategory.CLOTHING,
        covers={BodySection.TORSO, BodySection.ARMS, BodySection.LEGS},
    )
)

# Shoes
for slug, label in [
    ("boots", "Boots"),
    ("clogs-mules", "Clogs & mules"),
    ("espadrilles", "Espadrilles"),
    ("flipflops-slides", "Flip-flops & slides"),
    ("formal-shoes", "Formal shoes"),
    ("sandals", "Sandals"),
    ("slippers", "Slippers"),
    ("sports-shoes", "Sports shoes"),
    ("trainers", "Trainers"),
    ("boat-loafers-moccasins", "Boat shoes, loafers & moccasins"),
]:
    add(Category(slug, label, parent=WardrobeCategory.SHOES, covers={BodySection.FEET}))

add(
    Category(
        "bags-backpacks",
        "Bags & backpacks",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.ARMS},
    )
)
add(
    Category(
        "bandanas-headscarves",
        "Bandanas & headscarves",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.HEAD},
    )
)
add(
    Category(
        "belts",
        "Belts",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.TORSO},
    )
)
add(
    Category(
        "braces-suspenders",
        "Braces & suspenders",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.TORSO},
    )
)
add(
    Category(
        "gloves",
        "Gloves",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.ARMS},
    )
)
add(
    Category(
        "handkerchiefs",
        "Handkerchiefs",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.ARMS},
    )
)
add(
    Category(
        "hats-caps",
        "Hats & caps",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.HEAD},
    )
)
add(
    Category(
        "jewellery",
        "Jewellery",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.HEAD, BodySection.TORSO, BodySection.ARMS},
    )
)
add(
    Category(
        "pocket-squares",
        "Pocket squares",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.TORSO},
    )
)
add(
    Category(
        "scarves-shawls",
        "Scarves & shawls",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.HEAD, BodySection.TORSO},
    )
)
add(
    Category(
        "sunglasses",
        "Sunglasses",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.HEAD},
    )
)
add(
    Category(
        "ties-bowties",
        "Ties & bow ties",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.HEAD},
    )
)
add(
    Category(
        "watches",
        "Watches",
        parent=WardrobeCategory.ACCESSORIES,
        covers={BodySection.ARMS},
    )
)
add(
    Category(
        "other-accessories",
        "Other accessories",
        parent=WardrobeCategory.ACCESSORIES,
        covers=set(BodySection),
    )
)  # all sections

# ---- Helper functions ----


def children(parent) -> List[Category]:
    return [c for c in CATEGORIES.values() if c.parent == parent]


def covers(slug: str) -> Set[BodySection]:
    return CATEGORIES[slug].covers


def categories_covering(section: BodySection) -> List[Category]:
    return [c for c in CATEGORIES.values() if section in c.covers]


print(children(WardrobeCategory.SHOES))
# -> list of all shoe categories

print(covers("outerwear"))
# -> {BodySection.TORSO, BodySection.ARMS}

print(categories_covering(BodySection.HEAD))
# -> hats, bandanas, jewellery, sunglasses, ties, scarves, etc.


# BODY_SECTIONS_MAP = {1: "Head", 2: "Torso", 3: "Arms", 4: "Legs", 5: "Feet"}

# CLOTHING_CATEGORIES_MAP = {
#     1: "Outerwear",
#     2: "Tops & t-shirts",
#     3: "Suits & blazers",
#     4: "Jumpers & sweaters",
#     5: "Trousers",
#     6: "Shorts",
#     7: "Socks & underwear",
#     8: "Sleepwear",
#     9: "Activewear",
#     10: "Other men's clothing",
# }

# SHOES_MAP = {
#     1: "Boots",
#     2: "Clogs & mules",
#     3: "Espadrilles",
#     4: "Flip-flops & slides",
#     5: "Formal shoes",
#     6: "Sandals",
#     7: "Slippers",
#     8: "Sports shoes",
#     9: "Trainers",
#     10: "Boat shoes, loafers & moccasins",
# }

# ACCESSORIES_MAP = {
#     1: "Bags & backpacks",
#     2: "Bandanas & headscarves",
#     3: "Belts",
#     4: "Braces & suspenders",
#     5: "Gloves",
#     6: "Handkerchiefs",
#     7: "Hats & caps",
#     8: "Jewellery",
#     9: "Pocket squares",
#     10: "Scarves & shawls",
#     11: "Sunglasses",
#     12: "Ties & bow ties",
#     13: "Watches",
#     14: "Other accessories",
# }

# ITEM_BODY_SECTIONS_MAP = {
#     # Clothing items (IDs 1-10)
#     1: [2, 3],  # Outerwear -> torso, arms
#     2: [2],  # Tops & t-shirts -> torso
#     3: [2, 3],  # Suits & blazers -> torso, arms
#     4: [2, 3],  # Jumpers & sweaters -> torso, arms
#     5: [4],  # Trousers -> legs
#     6: [4],  # Shorts -> legs
#     7: [2, 4, 5],  # Socks & underwear -> torso, legs, feet
#     8: [2, 3, 4],  # Sleepwear -> torso, arms, legs
#     9: [2, 3, 4],  # Activewear -> torso, arms, legs
#     10: [2, 3, 4],  # Other men's clothing -> torso, arms, legs
#     # Shoes items (IDs 11-20, offset by 10)
#     11: [5],  # Boots -> feet
#     12: [5],  # Clogs & mules -> feet
#     13: [5],  # Espadrilles -> feet
#     14: [5],  # Flip-flops & slides -> feet
#     15: [5],  # Formal shoes -> feet
#     16: [5],  # Sandals -> feet
#     17: [5],  # Slippers -> feet
#     18: [5],  # Sports shoes -> feet
#     19: [5],  # Trainers -> feet
#     20: [5],  # Boat shoes, loafers & moccasins -> feet
#     # Accessories items (IDs 21-34, offset by 20)
#     21: [3],  # Bags & backpacks -> arms
#     22: [1],  # Bandanas & headscarves -> head
#     23: [2],  # Belts -> torso
#     24: [2],  # Braces & suspenders -> torso
#     25: [3],  # Gloves -> arms
#     26: [3],  # Handkerchiefs -> arms
#     27: [1],  # Hats & caps -> head
#     28: [1, 2, 3],  # Jewellery -> head, torso, arms
#     29: [2],  # Pocket squares -> torso
#     30: [1, 2],  # Scarves & shawls -> head, torso
#     31: [1],  # Sunglasses -> head
#     32: [1],  # Ties & bow ties -> head
#     33: [3],  # Watches -> arms
#     34: [1, 2, 3, 4, 5],  # Other accessories -> all sections
# }

# WARDROBE_CATEGORIES_MAP = {1: "Clothing", 2: "Shoes", 3: "Accessories"}
# CLOTHING_CATEGORIES = list(CLOTHING_CATEGORIES_MAP.values())
# SHOES = list(SHOES_MAP.values())
# ACCESSORIES = list(ACCESSORIES_MAP.values())
# BODY_SECTIONS = list(BODY_SECTIONS_MAP.values())


# def get_body_sections_for_item(item_id, category_type="clothing"):
#     """
#     Get the body sections covered by a specific item.

#     Args:
#         item_id (int): The ID of the item
#         category_type (str): Type of item - "clothing", "shoes", or "accessories"

#     Returns:
#         list: List of body section IDs, or empty list if item not found
#     """
#     if category_type == "clothing":
#         mapped_id = item_id
#     elif category_type == "shoes":
#         mapped_id = item_id + 10
#     elif category_type == "accessories":
#         mapped_id = item_id + 20
#     else:
#         return []

#     return ITEM_BODY_SECTIONS_MAP.get(mapped_id, [])


# def get_body_section_names_for_item(item_id, category_type="clothing"):
#     """
#     Get the body section names covered by a specific item.

#     Args:
#         item_id (int): The ID of the item
#         category_type (str): Type of item - "clothing", "shoes", or "accessories"

#     Returns:
#         list: List of body section names, or empty list if item not found
#     """
#     section_ids = get_body_sections_for_item(item_id, category_type)
#     return [BODY_SECTIONS_MAP.get(section_id, "") for section_id in section_ids]


# def get_items_for_body_section(section_id):
#     """
#     Get all items that cover a specific body section.

#     Args:
#         section_id (int): The body section ID

#     Returns:
#         dict: Dictionary with keys "clothing", "shoes", "accessories",
#               each containing a list of item IDs that cover this body section
#     """
#     result = {"clothing": [], "shoes": [], "accessories": []}

#     for item_id, sections in ITEM_BODY_SECTIONS_MAP.items():
#         if section_id in sections:
#             if item_id <= 10:  # clothing
#                 result["clothing"].append(item_id)
#             elif item_id <= 20:  # shoes
#                 result["shoes"].append(item_id - 10)
#             else:  # accessories
#                 result["accessories"].append(item_id - 20)

#     return result
