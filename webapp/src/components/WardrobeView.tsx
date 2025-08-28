import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardFooter } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { api } from '../lib/api';
import type { ClothingItem } from '../lib/api';
import { getCategoryName, getWardrobeCategoryName } from '../lib/constants';
import { Trash2, Edit2, Search } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

interface WardrobeViewProps {
  onEditItem?: (item: ClothingItem) => void;
}

export function WardrobeView({ onEditItem }: WardrobeViewProps) {
  const { user } = useAuth();
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filterItems = useCallback(() => {
    let filtered = items;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item =>
        item.custom_name.toLowerCase().includes(query) ||
        getCategoryName(item.wardrobe_category, item.category).toLowerCase().includes(query) ||
        getWardrobeCategoryName(item.wardrobe_category).toLowerCase().includes(query) ||
        (item.notes && item.notes.toLowerCase().includes(query))
      );
    }

    setFilteredItems(filtered);
  }, [items, searchQuery]);

  useEffect(() => {
    if (user) {
      loadItems();
    } else {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    filterItems();
  }, [items, searchQuery, filterItems]);

  const loadItems = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const data = await api.getItems();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (id: string) => {
    if (!id || !user) return;

    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        await api.deleteItem(id);
        await loadItems();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete item');
      }
    }
  };

  const displayColorPalette = (colors: Array<{ color: number[] | string; percentage: number }>) => {
    if (!colors || colors.length === 0) return null;

    return (
      <div className="flex gap-1 mt-2">
        {colors.slice(0, 5).map((colorInfo, index) => {
          let backgroundColor = '';

          if (Array.isArray(colorInfo.color)) {
            const [r, g, b] = colorInfo.color;
            backgroundColor = `rgb(${r}, ${g}, ${b})`;
          } else if (typeof colorInfo.color === 'string') {
            const rgbMatch = colorInfo.color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
            if (!rgbMatch) return null;
            backgroundColor = colorInfo.color;
          } else {
            return null;
          }

          return (
            <div
              key={index}
              className="w-4 h-4 rounded-full border border-gray-300"
              style={{ backgroundColor }}
              title={`${colorInfo.percentage.toFixed(1)}%`}
            />
          );
        })}
      </div>
    );
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600">Log in!</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your wardrobe...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadItems}>Try Again</Button>
        </div>
      </div>
    );
  }


  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
            <Input
              placeholder="Search items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">
            {items.length === 0 ? 'Your wardrobe is empty. Add some items!' : 'No items match your search.'}
          </p>
        </div>
      ) : (
        <>
          <div className="text-sm text-gray-600">
            Showing {filteredItems.length} of {items.length} items
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {filteredItems.map((item) => (
              <Card key={item._id} className="overflow-hidden">
                <CardContent className="p-4">
                  <div className="aspect-square bg-gray-100 rounded-md mb-3 flex items-center justify-center">
                    {item.path ? (
                      <img
                        src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/images/${item.path}`}
                        alt={item.custom_name}
                        className="w-full h-full object-cover rounded-md"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                          target.nextElementSibling?.classList.remove('hidden');
                        }}
                      />
                    ) : null}
                    <div className={`text-gray-500 text-sm ${item.path ? 'hidden' : ''}`}>
                      No Image
                    </div>
                  </div>

                  <h3 className="font-semibold text-sm mb-1 line-clamp-2">{item.custom_name}</h3>
                  <p className="text-xs text-gray-500 mb-2">
                    {getCategoryName(item.wardrobe_category, item.category)}
                  </p>

                  {item.notes && (
                    <p className="text-xs text-gray-500 mb-2 line-clamp-2">{item.notes}</p>
                  )}

                  {displayColorPalette(item.colors || [])}
                </CardContent>

                <CardFooter className="p-4 pt-0 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => onEditItem?.(item)}
                  >
                    <Edit2 className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeleteItem(item._id!)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
