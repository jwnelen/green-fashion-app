export const CLOTHING_CATEGORIES = [
  'dress',
  'hat',
  'longsleeve',
  'outwear',
  'pants',
  'shirt',
  'shoes',
  'shorts',
  'skirt',
  't-shirt',
  'other'
] as const;

export const BODY_SECTIONS = [
  { label: 'Head', value: 0 },
  { label: 'Upper Body', value: 1 },
  { label: 'Lower Body', value: 2 },
  { label: 'Feet', value: 3 },
] as const;

export type ClothingCategory = typeof CLOTHING_CATEGORIES[number];
export type BodySection = typeof BODY_SECTIONS[number]['value'];
