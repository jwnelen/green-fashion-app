import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Select } from './ui/select';
import { api } from '../lib/api';
import type { ClothingItem } from '../lib/api';
import { getCategoryMap, getCategoryName } from '../lib/constants';
import { X } from 'lucide-react';

interface EditCategoryModalProps {
  item: ClothingItem | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditCategoryModal({ item, isOpen, onClose, onSuccess }: EditCategoryModalProps) {
  const [selectedCategory, setSelectedCategory] = useState<number>(item?.category || 1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update selected category when item changes
  useEffect(() => {
    if (item) {
      setSelectedCategory(item.category);
    }
  }, [item]);

  if (!isOpen || !item) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedCategory === item.category) {
      onClose();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await api.updateItem(item._id!, { category: selectedCategory });
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update category');
    } finally {
      setLoading(false);
    }
  };

  const categoryOptions = getCategoryMap(item.wardrobe_category);
  const currentCategoryName = getCategoryName(item.wardrobe_category, item.category);

  return (
    <div className="fixed inset-0 bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Edit Category</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="mb-4">
          <h3 className="font-medium text-sm text-gray-700 mb-2">{item.custom_name}</h3>
          <p className="text-xs text-gray-500">
            Current category: <span className="font-medium">{currentCategoryName}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              New Category
            </label>
            <Select
              id="category"
              value={selectedCategory.toString()}
              onChange={(e) => setSelectedCategory(parseInt(e.target.value, 10))}
              className="w-full"
            >
              {Object.entries(categoryOptions).map(([key, categoryName]) => (
                <option key={key} value={key}>
                  {categoryName}
                </option>
              ))}
            </Select>
          </div>

          {error && (
            <div className="p-3 rounded-md bg-red-50 text-red-600 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || selectedCategory === item.category}
              className="flex-1"
            >
              {loading ? 'Updating...' : 'Update Category'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
