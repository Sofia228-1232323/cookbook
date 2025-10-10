#!/bin/bash

echo "🚀 Deploying Cookbook Application..."

# Build and start production containers
echo "📦 Building production containers..."
docker compose -f docker-compose.prod.yml up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker compose -f docker-compose.prod.yml ps

# Test backend health
echo "🏥 Testing backend health..."
curl -f http://localhost:8000/health || echo "❌ Backend health check failed"

# Test frontend
echo "🌐 Testing frontend..."
curl -f http://localhost:80 || echo "❌ Frontend check failed"

echo "✅ Deployment completed!"
echo "🌐 Frontend: http://localhost:80"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
