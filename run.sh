#!/bin/bash

# Script to run the FastAPI application

echo "Starting FastAPI server..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
cd src
python main.py
