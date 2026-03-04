#!/bin/bash
# Script to setup and run Sakhi

echo "🌸 Starting Sakhi..."

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Run App
echo "Launching Sakhi on http://127.0.0.1:5000"
python app.py
