# Green Fashion Webapp

A React-based web application for managing your wardrobe collection, built with modern technologies.

## Features

- **Wardrobe View**: Browse your clothing items in a responsive grid layout
- **Search & Filter**: Find items by name, category, or notes
- **Add New Items**: Add clothing items with images, categorization, and notes
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with Tailwind CSS and shadcn/ui components

## Technology Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Custom shadcn/ui components
- **Routing**: React Router DOM
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Running Green Fashion API server

### Installation

1. Navigate to the webapp directory:
   ```bash
   cd webapp
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

   Update the `.env` file with your API URL:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## API Integration

The webapp connects to the Green Fashion API running on `http://localhost:8000` by default. Make sure the API server is running before using the webapp.

### API Features Used

- GET `/items` - Fetch all wardrobe items
- POST `/items` - Create new clothing item
- PUT `/items/{id}` - Update existing item
- DELETE `/items/{id}` - Delete item
- POST `/items/{id}/upload-image` - Upload item image
- GET `/categories` - Get available categories
- GET `/search` - Search items

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Reusable UI components (Button, Card, Input, etc.)
│   ├── WardrobeView.tsx # Main wardrobe display component
│   └── AddItemForm.tsx  # Add new item form component
├── lib/
│   ├── api.ts          # API service utilities
│   ├── constants.ts    # Application constants
│   └── utils.ts        # Utility functions
├── App.tsx             # Main application component with routing
└── main.tsx           # Application entry point
```

## Usage

### Viewing Your Wardrobe

1. Navigate to the home page to see all your clothing items
2. Use the search bar to find specific items
3. Filter by category using the dropdown
4. Click "Edit" to modify item details or "Delete" to remove items

### Adding New Items

1. Click "Add Item" in the navigation
2. Fill out the form with item details:
   - **Name**: Custom name for the item
   - **Category**: Select from predefined categories
   - **Body Section**: Where the item is worn
   - **Notes**: Optional additional information
   - **Image**: Optional photo upload
3. Click "Add Item" to save

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Green Fashion wardrobe management system.
