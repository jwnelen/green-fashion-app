export const CLOTHING_CATEGORIES_MAP: Record<number, string> = {
  1: "Outerwear",
  2: "Tops & t-shirts",
  3: "Suits & blazers",
  4: "Jumpers & sweaters",
  5: "Trousers",
  6: "Shorts",
  7: "Socks & underwear",
  8: "Sleepwear",
  9: "Activewear",
  10: "Other men's clothing",
};
export const SHOES_MAP: Record<number, string> = {
  1: "Boots",
  2: "Clogs & mules",
  3: "Espadrilles",
  4: "Flip-flops & slides",
  5: "Formal shoes",
  6: "Sandals",
  7: "Slippers",
  8: "Sports shoes",
  9: "Trainers",
  10: "Boat shoes, loafers & moccasins",
}
export const ACCESSORIES_MAP: Record<number, string> = {
  1: "Bags & backpacks",
  2: "Bandanas & headscarves",
  3: "Belts",
  4: "Braces & suspenders",
  5: "Gloves",
  6: "Handkerchiefs",
  7: "Hats & caps",
  8: "Jewellery",
  9: "Pocket squares",
  10: "Scarves & shawls",
  11: "Sunglasses",
  12: "Ties & bow ties",
  13: "Watches",
  14: "Other accessories",
};


export const CLOTHING_CATEGORIES = Object.values(CLOTHING_CATEGORIES_MAP);
export const SHOES = Object.values(SHOES_MAP);
export const ACCESSORIES = Object.values(ACCESSORIES_MAP);

export const WARDROBE_CATEGORIES_MAP: Record<number, string> = { 1: "Clothing", 2: "Shoes", 3: "Accessories" }
export const WARDROBE_CATEGORIES = Object.values(WARDROBE_CATEGORIES_MAP);

// Helper functions to get category names
export const getWardrobeCategoryName = (wardrobeCategoryNumber: number): string => {
  return WARDROBE_CATEGORIES_MAP[wardrobeCategoryNumber] || "Unknown";
};

export const getCategoryName = (wardrobeCategoryNumber: number, categoryNumber: number): string => {
  switch (wardrobeCategoryNumber) {
    case 1: // Clothing
      return CLOTHING_CATEGORIES_MAP[categoryNumber] || "Unknown";
    case 2: // Shoes
      return SHOES_MAP[categoryNumber] || "Unknown";
    case 3: // Accessories
      return ACCESSORIES_MAP[categoryNumber] || "Unknown";
    default:
      return "Unknown";
  }
};

export const getCategoryMap = (wardrobeCategoryNumber: number) => {
  switch (wardrobeCategoryNumber) {
    case 1: // Clothing
      return CLOTHING_CATEGORIES_MAP;
    case 2: // Shoes
      return SHOES_MAP;
    case 3: // Accessories
      return ACCESSORIES_MAP;
    default:
      return CLOTHING_CATEGORIES_MAP;
  }
};

// @ts-ignore
export type ClothingCategory = typeof CLOTHING_CATEGORIES[number];
export type ShoeCategory = typeof SHOES[number];
export type AccessoriesCategory = typeof ACCESSORIES[number];
