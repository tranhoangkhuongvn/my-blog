#!/bin/bash
# Setup script for the static site generator blog

echo "🚀 Setting up your static site generator blog..."
echo ""

# Check Python version
if command -v python3 &>/dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 is required but not installed."
    echo "Please install Python 3.8 or higher from https://python.org"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    ./venv/Scripts/pip install -r requirements.txt
else
    # Unix-like (Linux, macOS)
    ./venv/bin/pip install -r requirements.txt
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 Your blog is ready to use!"
echo ""
echo "Quick Start Commands:"
echo "---------------------"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  Build site:    python build.py"
    echo "  Preview:       python serve.py"
    echo "  New post:      Use 'make new-post' or create manually in content/posts/"
else
    echo "  Build site:    make build  (or ./venv/bin/python build.py)"
    echo "  Preview:       make serve  (or ./venv/bin/python serve.py)"
    echo "  New post:      make new-post"
    echo "  Help:          make help"
fi
echo ""
echo "Then open http://localhost:8000 in your browser"
echo ""
echo "📝 Documentation: See README.md for full documentation"
