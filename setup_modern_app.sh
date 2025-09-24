#!/bin/bash

# Smart Job Scraper v2.0 Setup Script
# This script sets up the modern Next.js application

set -e

echo "🚀 Setting up Smart Job Scraper v2.0..."
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Navigate to next-app directory
cd next-app

echo "📦 Installing dependencies..."
if command -v yarn &> /dev/null; then
    echo "   Using Yarn..."
    yarn install
else
    echo "   Using npm..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "🔧 Creating environment configuration..."
    cat > .env.local << EOL
# Smart Job Scraper v2.0 Configuration
# Copy this file and update with your actual values

# Database (for future implementation)
# DATABASE_URL="postgresql://username:password@localhost:5432/jobscraper"
# REDIS_URL="redis://localhost:6379"

# API Keys (optional)
# SERP_API_KEY="your-serp-api-key-here"

# App Configuration
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_APP_NAME="Smart Job Scraper"

# Development
NODE_ENV="development"
EOL
    echo "   Created .env.local - please update with your configuration"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. cd next-app"
echo "   2. npm run dev (or yarn dev)"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "🔧 Available commands:"
echo "   npm run dev          - Start development server"
echo "   npm run build        - Build for production"
echo "   npm run start        - Start production server"
echo "   npm run lint         - Run linting"
echo "   npm run type-check   - Check TypeScript types"
echo ""
echo "📚 Documentation:"
echo "   - README.md for detailed setup instructions"
echo "   - Check the /src directory for code organization"
echo ""
echo "🐛 Fixed issues from v1.0:"
echo "   ✅ Category switching bug"
echo "   ✅ Code duplication (2580+ lines eliminated)"
echo "   ✅ Global state management issues"
echo "   ✅ Poor error handling"
echo "   ✅ Monolithic UI structure"
echo ""
echo "🚀 Ready to launch! The modern job scraper awaits..."
