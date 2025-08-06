#!/bin/bash

# Local deployment script for development
# This script helps you run the application locally with all dependencies

set -e

echo "🏠 Starting Green Fashion local deployment"

# Check if required files exist
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env file with your actual configuration"
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if MongoDB is ready
echo "🗄️  Checking MongoDB connection..."
for i in {1..30}; do
    if docker-compose exec -T mongo mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; then
        echo "✅ MongoDB is ready"
        break
    fi

    if [ $i -eq 30 ]; then
        echo "❌ MongoDB failed to start after 30 attempts"
        echo "🔍 Checking logs..."
        docker-compose logs mongo
        exit 1
    fi

    echo "⏳ Waiting for MongoDB... ($i/30)"
    sleep 2
done

# Check if the app is ready
echo "🌐 Checking application health..."
for i in {1..20}; do
    if curl -f http://localhost:8080/_stcore/health >/dev/null 2>&1; then
        echo "✅ Application is ready"
        break
    fi

    if [ $i -eq 20 ]; then
        echo "❌ Application failed to start after 20 attempts"
        echo "🔍 Checking logs..."
        docker-compose logs app
        exit 1
    fi

    echo "⏳ Waiting for application... ($i/20)"
    sleep 3
done

echo ""
echo "🎉 Green Fashion is running locally!"
echo "📱 Application: http://localhost:8080"
echo "🗄️  MongoDB: mongodb://root:password@localhost:27017"
echo "🔧 MongoDB Admin (optional): http://localhost:8081"
echo ""
echo "🛠️  Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart app:      docker-compose restart app"
echo "  Shell into app:   docker-compose exec app bash"
echo ""
echo "📝 To enable MongoDB Admin UI, run:"
echo "  docker-compose --profile admin up -d"
