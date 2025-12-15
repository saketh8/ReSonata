#!/bin/bash

echo "🎹 ReSonata - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Setup backend
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit backend/.env and add your MISTRAL_API_KEY"
    else
        echo "MISTRAL_API_KEY=UuqBcnVCwr7M7qsVZmO8G8JTmRa61DQS" > .env
    fi
fi

echo "✅ Backend setup complete"
echo ""

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install --silent
fi

echo "✅ Frontend setup complete"
echo ""

cd ..

echo "🚀 Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Terminal 1: cd backend && source venv/bin/activate && python app.py"
echo "  2. Terminal 2: cd frontend && npm start"
echo ""
echo "Or use the start script: ./start.sh"

