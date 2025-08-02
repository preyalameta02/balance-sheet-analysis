#!/bin/bash

# 🚀 Balance Sheet Analysis - Deployment Script
# This script helps you deploy your app to Railway and Vercel

set -e

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for deployment"
    print_success "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    print_warning "No remote repository set. Please run:"
    echo "git remote add origin https://github.com/yourusername/balance-sheet-analysis.git"
    echo "git push -u origin main"
    echo ""
fi

print_status "Checking prerequisites..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Installing..."
    npm install -g @railway/cli
    print_success "Railway CLI installed"
else
    print_success "Railway CLI found"
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_warning "Vercel CLI not found. Installing..."
    npm install -g vercel
    print_success "Vercel CLI installed"
else
    print_success "Vercel CLI found"
fi

print_status "Creating deployment configuration..."

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    cat > .env.example << EOF
# Database (Railway will provide this)
DATABASE_URL=your_railway_postgres_url

# JWT Secret (generate a strong secret)
SECRET_KEY=your-super-secret-jwt-key-change-this

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Frontend URL (update after Vercel deployment)
FRONTEND_URL=https://your-app.vercel.app
EOF
    print_success "Created .env.example"
fi

print_status "Checking Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    exit 1
fi

print_status "Checking frontend dependencies..."
if [ ! -f "frontend/package.json" ]; then
    print_error "frontend/package.json not found!"
    exit 1
fi

print_success "All prerequisites met!"

echo ""
echo "📋 Deployment Checklist:"
echo "1. ✅ Git repository initialized"
echo "2. ✅ Railway CLI installed"
echo "3. ✅ Vercel CLI installed"
echo "4. ✅ Configuration files created"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/yourusername/balance-sheet-analysis.git"
echo "   git push -u origin main"
echo ""
echo "2. Deploy Backend to Railway:"
echo "   - Go to https://railway.app"
echo "   - Create new project"
echo "   - Connect your GitHub repository"
echo "   - Add PostgreSQL database"
echo "   - Set environment variables"
echo ""
echo "3. Deploy Frontend to Vercel:"
echo "   - Go to https://vercel.com"
echo "   - Import your GitHub repository"
echo "   - Set root directory to 'frontend'"
echo "   - Add REACT_APP_API_URL environment variable"
echo ""
echo "4. Update CORS settings in Railway with your Vercel URL"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
print_success "Deployment preparation complete!" 