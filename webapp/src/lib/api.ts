export interface ClothingItem {
  _id?: string;
  custom_name: string;
  category: string;
  body_section: number;
  notes?: string;
  colors?: Array<{ color: string; percentage: number }>;
  display_name?: string;
  path?: string;
  image_url?: string;
}

export interface UpdateClothingItem {
  custom_name?: string;
  category?: string;
  body_section?: number;
  notes?: string;
  colors?: Array<{ color: string; percentage: number }>;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
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

    const response = await fetch(`${API_BASE_URL}/items/${itemId}/upload-image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async addUserToDataBase(credentialResponse: { credential?: string }): Promise<{ token: string; user: { id: string; email: string; name: string; picture?: string } }> {
    return this.request(`/api/auth/google`, {
      method: 'POST',
      body: JSON.stringify({
        token: credentialResponse.credential
      })
    });
  }

  async healthCheck(): Promise<{ status: string; database: string }> {
    return this.request<{ status: string; database: string }>('/health');
  }
}

export const api = new ApiService();
