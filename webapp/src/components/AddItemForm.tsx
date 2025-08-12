import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { api } from '../lib/api';
import {classifierAPI } from '../lib/classifier_api'

import type { ClothingItem } from '../lib/api';
import { CLOTHING_CATEGORIES, BODY_SECTIONS, type ClothingCategory } from '../lib/constants';
import { Upload, Plus } from 'lucide-react';

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

        try {
          const result = await classifierAPI.classifyImage(file);
          const classifiedCategory = result.message.toLowerCase();

          // Check if the classified category exists in our categories list
          if (CLOTHING_CATEGORIES.includes(classifiedCategory as ClothingCategory)) {
            setClassificationResult(classifiedCategory);
            // Automatically select the classified category
            setFormData(prev => ({
              ...prev,
              category: classifiedCategory as ClothingCategory
            }));
          } else {
            setClassificationResult(classifiedCategory);
          }
        } catch (classificationError) {
          console.warn('Classification failed:', classificationError);
        }

      } else {
        setError('Please select a valid image file');
        setSelectedFile(null);
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
        colors: [],
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
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
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
                {selectedFile && (
                  <div className="mt-2 text-sm text-gray-600">
                    Selected: {selectedFile.name}
                  </div>
                )}
              </div>
            </div>
          </div>

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
