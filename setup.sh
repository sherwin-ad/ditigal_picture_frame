#!/bin/bash

# Exit on error
set -e

echo "Setting up Digital Picture Frame..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found."
    exit 1
fi

echo "Setup complete!"
echo ""
echo "To run the application, use:"
echo "  ./venv/bin/python app.py"
echo ""
