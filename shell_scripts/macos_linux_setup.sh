#!/bin/bash
#  Setup Script for macOS/Linux

# Change context to the project root directory regardless of where script is run
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.." || exit

echo " Setting up Optamo Movie Ratings Platform..."

# 1. Backend Setup
echo ""
echo " [1/2] Setting up Python backend..."
cd backend || exit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "⏳ Running data migration (this may take ~60 seconds)..."
python migrate.py
cd ..

# 2. Frontend Setup
echo ""
echo "  [2/2] Setting up Angular frontend..."
cd frontend || exit
npm install
cd ..

echo ""
echo " Setup complete! You can now start the application by running: ./shell_scripts/macos_linux_run.sh"
