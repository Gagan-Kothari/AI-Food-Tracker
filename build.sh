#!/bin/bash
set -e  # Exit on error

echo "========================================="
echo "Building AI Food Tracker Application"
echo "========================================="

echo "Python version: $(python --version)"
echo "Python path: $(which python)"
echo "Pip version: $(pip --version || echo 'pip not found')"

echo ""
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ""
echo "Verifying critical packages..."
python -m pip show uvicorn || { echo "ERROR: uvicorn not found!"; exit 1; }
python -m pip show fastapi || { echo "ERROR: fastapi not found!"; exit 1; }

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="

