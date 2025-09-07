export interface ClothingItem {
  _id?: string;
  custom_name: string;
  wardrobe_category: number;  // 1=Clothing, 2=Shoes, 3=Accessories
  category: number;
  notes?: string;
  colors?: Array<{ color: number[]; percentage: number }>;
  display_name?: string;
  path?: string;
  image_url?: string;
}

export interface ColorPalette {
  color: number[]; // RGB values [r, g, b]
  percentage: number;
}

export interface ColorExtractionResponse {
  colors: ColorPalette[];
}

export interface UpdateClothingItem {
  custom_name?: string;
  wardrobe_category?: number;  // 1=Clothing, 2=Shoes, 3=Accessories
  category?: number;
  notes?: string;
  colors?: Array<{ color: number[]; percentage: number }>;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = "v1"

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    api_version: string = API_VERSION
  ): Promise<T> {
    const url = `${API_BASE_URL}/${api_version}${endpoint}`;

    // Get token from sessionStorage for authenticated requests
    const token = sessionStorage.getItem('googleToken');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add Bearer token if available
    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      headers,
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('API Error:', {
        url,
        status: response.status,
        statusText: response.statusText,
        errorData
      });
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getItems(): Promise<ClothingItem[]> {
    return this.request<ClothingItem[]>('/items');
  }

  async getItem(id: string): Promise<ClothingItem> {
    return this.request<ClothingItem>(`/items/${id}`);
  }

  async createItem(item: Omit<ClothingItem, '_id'>): Promise<{ id: string; message: string }> {
    return this.request<{ id: string; message: string }>('/items', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  async updateItem(id: string, updates: UpdateClothingItem): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteItem(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/items/${id}`, {
      method: 'DELETE',
    });
  }

  async getItemsByCategory(category: string): Promise<ClothingItem[]> {
    return this.request<ClothingItem[]>(`/items/category/${category}`);
  }

  async getCategories(): Promise<{ categories: string[] }> {
    return this.request<{ categories: string[] }>('/categories');
  }

  async searchItems(query: string): Promise<ClothingItem[]> {
    return this.request<ClothingItem[]>(`/search?query=${encodeURIComponent(query)}`);
  }

  async getStats(): Promise<{ total_items: number; category_counts: Record<string, number> }> {
    return this.request<{ total_items: number; category_counts: Record<string, number> }>('/stats');
  }

  async uploadImage(itemId: string, file: File): Promise<{ message: string; path: string }> {
    const formData = new FormData();
    formData.append('file', file);

    // Get token for authenticated upload
    const token = sessionStorage.getItem('googleToken');
    const headers: Record<string, string> = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/items/${itemId}/upload-image`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async addUserToDataBase(credentialResponse: { credential?: string }): Promise<{ token: string; user: { id: string; email: string; name: string; picture?: string } }> {
    return this.request(`/auth/google`, {
      method: 'POST',
      body: JSON.stringify({
        token: credentialResponse.credential
      })
    }, "v2");
  }

  async healthCheck(): Promise<{ status: string; database: string }> {
    return this.request<{ status: string; database: string }>('/health');
  }

  async extractColors(file: File, nColors: number = 5): Promise<ColorExtractionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('n_colors', nColors.toString());

    // Get token for authenticated request
    const token = sessionStorage.getItem('googleToken');
    const headers: Record<string, string> = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/extract-colors`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const api = new ApiService();
