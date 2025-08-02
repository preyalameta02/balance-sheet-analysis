#!/bin/bash

echo "🚀 Starting Balance Sheet Analyst Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create one based on env.example"
    echo "   Copy env.example to .env and update the values"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create uploads directory
mkdir -p uploads

echo "✅ Dependencies installed successfully!"

echo ""
echo "🌐 Starting the application..."
echo "   Backend will run on: http://localhost:8000"
echo "   Frontend will run on: http://localhost:3000"
echo "   API docs will be at: http://localhost:8000/docs"
echo ""

# Start backend in background
echo "🔧 Starting backend server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🎉 Application is running!"
echo "   Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait 