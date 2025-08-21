import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { api } from '../lib/api';

import type { ClothingItem, ColorPalette } from '../lib/api';
import { CLOTHING_CATEGORIES, BODY_SECTIONS, type ClothingCategory } from '../lib/constants';
import { Upload, Plus, Palette } from 'lucide-react';

interface AddItemFormProps {
  onItemAdded?: () => void;
}

export function AddItemForm({ onItemAdded }: AddItemFormProps) {
  const [formData, setFormData] = useState<{
    custom_name: string;
    category: ClothingCategory;
    body_section: number;
    notes: string;
  }>({
    custom_name: '',
    category: CLOTHING_CATEGORIES[0],
    body_section: BODY_SECTIONS[0].value,
    notes: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [classificationResult, setClassificationResult] = useState<string | null>(null);
  const [extractedColors, setExtractedColors] = useState<ColorPalette[]>([]);
  const [colorExtractionLoading, setColorExtractionLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // classifierAPI.healthCheck().then(s => console.log(s))

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setError(null);
        setClassificationResult(null);
        setExtractedColors([]);

        // Create image preview
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);

        // Extract colors from the selected image
        setColorExtractionLoading(true);
        try {
          const colorResult = await api.extractColors(file);
          setExtractedColors(colorResult.colors);
        } catch (colorError) {
          console.warn('Color extraction failed:', colorError);
          // Don't show error to user, just log it
        } finally {
          setColorExtractionLoading(false);
        }
      } else {
        setError('Please select a valid image file');
        setSelectedFile(null);
        setImagePreview(null);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      custom_name: '',
      category: CLOTHING_CATEGORIES[0],
      body_section: BODY_SECTIONS[0].value,
      notes: '',
    });
    setSelectedFile(null);
    setError(null);
    setSuccess(null);
    setClassificationResult(null);
    setExtractedColors([]);
    setImagePreview(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!formData.custom_name.trim()) {
      setError('Please provide an item name');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const itemData: Omit<ClothingItem, '_id'> = {
        custom_name: formData.custom_name,
        category: formData.category,
        body_section: formData.body_section,
        notes: formData.notes || '',
        colors: extractedColors,
        display_name: selectedFile?.name || formData.custom_name,
        path: undefined,
      };

      const result = await api.createItem(itemData);

      if (selectedFile && result.id) {
        try {
          await api.uploadImage(result.id, selectedFile);
        } catch (uploadError) {
          console.warn('Failed to upload image:', uploadError);
        }
      }

      setSuccess('Item added successfully!');
      resetForm();
      onItemAdded?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Add New Item
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="custom_name" className="text-sm font-medium">
              Item Name *
            </label>
            <Input
              id="custom_name"
              type="text"
              placeholder="e.g., Blue Summer Dress"
              value={formData.custom_name}
              onChange={(e) => handleInputChange('custom_name', e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="category" className="text-sm font-medium">
                Category *
              </label>
              {classificationResult && (
                <div className="p-2 rounded-md bg-blue-50 text-blue-700 text-sm">
                  ✨ Classified as "{classificationResult}"
                </div>
              )}
              <Select
                id="category"
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
              >
                {CLOTHING_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </option>
                ))}
              </Select>
            </div>

            <div className="space-y-2">
              <label htmlFor="body_section" className="text-sm font-medium">
                Body Section *
              </label>
              <Select
                id="body_section"
                value={formData.body_section.toString()}
                onChange={(e) => handleInputChange('body_section', parseInt(e.target.value))}
              >
                {BODY_SECTIONS.map((section) => (
                  <option key={section.value} value={section.value}>
                    {section.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="notes" className="text-sm font-medium">
              Notes (optional)
            </label>
            <textarea
              id="notes"
              placeholder="Add any additional notes about this item..."
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="image" className="text-sm font-medium">
              Image (optional)
            </label>
            <div className="border-2 border-gray-300 rounded-lg p-6">
              {imagePreview ? (
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full object-cover rounded-lg"
                  />
                  <div className="absolute top-2 right-2">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedFile(null);
                        setImagePreview(null);
                        setExtractedColors([]);
                        const input = document.getElementById('image') as HTMLInputElement;
                        if (input) input.value = '';
                      }}
                      className="w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 text-xs"
                    >
                      ✕
                    </button>
                  </div>
                  {selectedFile && (
                    <div className="mt-2 text-sm text-gray-600 text-center">
                      {selectedFile.name}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <label htmlFor="image" className="cursor-pointer">
                      <span className="text-sm font-medium text-blue-600 hover:text-blue-500">
                        Click to upload
                      </span>
                      <input
                        id="image"
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                    </label>
                    <p className="text-xs text-gray-500">PNG, JPG, JPEG up to 10MB</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Color Palette Display */}
          {(extractedColors.length > 0 || colorExtractionLoading) && (
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Palette className="w-4 h-4" />
                Extracted Colors
              </label>
              <div className="border rounded-lg p-4">
                {colorExtractionLoading ? (
                  <div className="text-center text-sm text-gray-500">
                    Extracting colors from image...
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-2">
                      {extractedColors.map((colorPalette, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <div
                            className="w-6 h-6 rounded border border-gray-300"
                            style={{
                              backgroundColor: `rgb(${colorPalette.color[0]}, ${colorPalette.color[1]}, ${colorPalette.color[2]})`
                            }}
                          />
                          <span className="text-xs text-gray-600">
                            {colorPalette.percentage.toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500">
                      Colors will be automatically saved with this item
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-md bg-red-50 text-red-600 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 rounded-md bg-green-50 text-green-600 text-sm">
              {success}
            </div>
          )}

          <div className="flex gap-3">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Adding...' : 'Add Item'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={resetForm}
              disabled={loading}
            >
              Clear
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
