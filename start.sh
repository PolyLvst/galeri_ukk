#!/bin/bash

# Check if venv directory exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    # Install pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm get-pip.py
fi

# Install required Python packages using pip in the virtual environment
pip install -r requirements-glitch.txt

# Start your Python application
python storage_server.py
# python app.py

# Deactivate the virtual environment
deactivate