import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Button } from './components/ui/button';
import { WardrobeView } from './components/WardrobeView';
import { AddItemForm } from './components/AddItemForm';
import type { ClothingItem } from './lib/api';
import { Shirt, Plus, Menu } from 'lucide-react';

function Navigation() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <Shirt className="h-8 w-8 text-blue-600" />
              <span className="font-bold text-xl text-gray-900">Green Fashion</span>
            </Link>
          </div>

          {/* Desktop menu */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-4">
              <Link to="/">
                <Button
                  variant={location.pathname === '/' ? 'default' : 'ghost'}
                  size="sm"
                >
                  <Shirt className="w-4 h-4 mr-2" />
                  Wardrobe
                </Button>
              </Link>
              <Link to="/add">
                <Button
                  variant={location.pathname === '/add' ? 'default' : 'ghost'}
                  size="sm"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Item
                </Button>
              </Link>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Menu className="h-6 w-6" />
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <Link to="/" onClick={() => setMobileMenuOpen(false)}>
                <Button
                  variant={location.pathname === '/' ? 'default' : 'ghost'}
                  size="sm"
                  className="w-full justify-start"
                >
                  <Shirt className="w-4 h-4 mr-2" />
                  Wardrobe
                </Button>
              </Link>
              <Link to="/add" onClick={() => setMobileMenuOpen(false)}>
                <Button
                  variant={location.pathname === '/add' ? 'default' : 'ghost'}
                  size="sm"
                  className="w-full justify-start"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Item
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

function WardrobePage() {
  const handleEditItem = (item: ClothingItem) => {
    console.log('Edit item:', item);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Your Wardrobe</h1>
        <p className="text-gray-600 mt-2">
          Manage your clothing collection
        </p>
      </div>

      <WardrobeView onEditItem={handleEditItem} />
    </div>
  );
}

function AddItemPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleItemAdded = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Add New Item</h1>
        <p className="text-gray-600 mt-2">
          Add a new clothing item to your wardrobe
        </p>
      </div>

      <AddItemForm key={refreshKey} onItemAdded={handleItemAdded} />
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />

        <main>
          <Routes>
            <Route path="/" element={<WardrobePage />} />
            <Route path="/add" element={<AddItemPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
