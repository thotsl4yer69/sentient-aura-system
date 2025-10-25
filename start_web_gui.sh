#!/bin/bash
# Sentient Core v4 - Web GUI Launcher
# Launches the full system with WebSocket server and opens the 3D visualizer in browser

echo "=================================="
echo "  Sentient Core v4 - Web GUI Mode"
echo "=================================="
echo ""

# Navigate to project directory
cd /home/mz1312/Sentient-Core-v4 || exit 1

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run the install script first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Check if llama3.2:3b model is available
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "Pulling llama3.2:3b model..."
    ollama pull llama3.2:3b
fi

# Get the HTML file path
HTML_FILE="/home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html"

if [ ! -f "$HTML_FILE" ]; then
    echo "Error: GUI file not found at $HTML_FILE"
    exit 1
fi

echo ""
echo "Starting Sentient Core with WebSocket GUI..."
echo "WebSocket Server: ws://localhost:8765"
echo "3D Visualizer will open in your browser..."
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Open browser with the HTML file (in background)
sleep 2
if command -v chromium-browser &> /dev/null; then
    chromium-browser --app="file://$HTML_FILE" &
elif command -v firefox &> /dev/null; then
    firefox "file://$HTML_FILE" &
elif command -v google-chrome &> /dev/null; then
    google-chrome --app="file://$HTML_FILE" &
else
    echo "No browser found. Please open file://$HTML_FILE manually"
fi

# Start the main system (with WebSocket server)
python3 sentient_aura_main.py

# Cleanup
echo ""
echo "Shutting down Sentient Core..."
