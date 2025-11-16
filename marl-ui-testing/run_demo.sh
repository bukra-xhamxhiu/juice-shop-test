#!/bin/bash

# MARL UI Test Generation Demo Script
# This script sets up and runs the MARL-based UI test generation demo

echo "=== MARL UI Test Generation Demo Setup ==="

# Check if we're in the right directory
if [ ! -f "demo.py" ]; then
    echo "Error: Please run this script from the marl-ui-testing directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Check if ChromeDriver is available
if ! command -v chromedriver &> /dev/null; then
    echo "Warning: ChromeDriver not found in PATH"
    echo "Please install ChromeDriver: https://chromedriver.chromium.org/"
    echo "Or use: brew install chromedriver (on macOS)"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Juice Shop is running
echo "Checking if Juice Shop is running..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Juice Shop is running on http://localhost:3000"
else
    echo "Warning: Juice Shop is not running on http://localhost:3000"
    echo "Please start Juice Shop first:"
    echo "  cd .. && npm start"
    echo ""
    echo "Continuing with demo anyway (some features may not work)..."
fi

# Run the demo
echo ""
echo "Running MARL UI Test Generation Demo..."
echo "======================================"

python3 demo.py

echo ""
echo "Demo completed!"
echo ""
echo "Generated files should be in the test/cypress/e2e/ directory"
echo "You can run the generated tests with:"
echo "  npx cypress run --spec test/cypress/e2e/demo_marl_tests.ts"
echo ""
echo "To run the full training:"
echo "  python3 train_marl.py"

