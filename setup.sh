#!/bin/bash

# Setup script for the FastAPI application

echo "=== FastAPI Application Setup ==="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please update .env file with your database credentials!"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Make sure PostgreSQL and Redis are running"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start the server: cd src && python main.py"
echo ""
