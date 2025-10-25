#!/bin/bash
##
# Launch Sentient Core with Enhanced Coral Visualization
# Uses coral-py39 environment with working pycoral
#

echo "=========================================="
echo "SENTIENT CORE - ENHANCED LAUNCH"
echo "120-Feature Multi-Sensor Fusion"
echo "=========================================="
echo ""

# Check if Coral TPU is connected
if ! lsusb | grep -iq "Google\|Global Unichip"; then
    echo "⚠️  WARNING: Coral USB Accelerator not detected!"
    echo "   Please connect the Coral TPU and try again."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to project directory
cd /home/mz1312/Sentient-Core-v4

# Use coral-py39 environment (has pycoral installed)
PYTHON="/home/mz1312/.pyenv/versions/coral-py39/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ Error: coral-py39 Python environment not found!"
    echo "   Expected: $PYTHON"
    exit 1
fi

echo "✓ Using Python: $PYTHON"
$PYTHON --version

# Verify pycoral is available
if ! $PYTHON -c "import pycoral" 2>/dev/null; then
    echo "❌ Error: pycoral not found in coral-py39 environment!"
    exit 1
fi
echo "✓ pycoral available"

# Verify Edge TPU model exists
MODEL_PATH="models/sentient_viz_enhanced_edgetpu.tflite"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Error: Enhanced model not found!"
    echo "   Expected: $MODEL_PATH"
    exit 1
fi
echo "✓ Enhanced model found ($(du -h $MODEL_PATH | cut -f1))"

# Check Edge TPU detection
echo ""
echo "Detecting Coral TPU devices..."
$PYTHON -c "from pycoral.utils import edgetpu; devs = edgetpu.list_edge_tpus(); print(f'Found {len(devs)} Edge TPU device(s)'); [print(f'  - {d}') for d in devs]"

echo ""
echo "Starting Sentient Core with Enhanced Visualization..."
echo "=========================================="
echo ""

# Launch with coral-py39 Python
exec $PYTHON sentient_aura_main.py "$@"
