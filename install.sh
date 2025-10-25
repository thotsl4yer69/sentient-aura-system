#!/bin/bash
###############################################################################
# Sentient Core v4 - Automated Installation Script
#
# This script automates the complete setup process for Sentient Core on a
# fresh Raspberry Pi or compatible Linux system.
#
# Usage: ./install.sh
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo -e "${BLUE}========================================================================${NC}"
echo -e "${BLUE}   SENTIENT CORE v4 - Automated Installation${NC}"
echo -e "${BLUE}========================================================================${NC}"
echo ""
echo -e "${GREEN}Project directory: ${PROJECT_ROOT}${NC}"
echo ""

###############################################################################
# Step 1: System Package Update
###############################################################################

echo -e "${YELLOW}[Step 1/7]${NC} Updating system packages..."
sudo apt-get update -qq

echo -e "${GREEN}✓ System packages updated${NC}"
echo ""

###############################################################################
# Step 2: Install System Dependencies
###############################################################################

echo -e "${YELLOW}[Step 2/7]${NC} Installing system dependencies..."

# Core dependencies
PACKAGES=(
    python3-pip
    python3-full
    python3-venv
    python3-dev
    python3-opencv
    python3-numpy
    git
    espeak-ng
    portaudio19-dev
    python3-pyaudio
    libasound2-dev
    libportaudio2
    libportaudiocpp0
    i2c-tools
    python3-smbus
    python3-rpi.gpio
    alsa-utils
    sox
    libsox-fmt-all
)

echo "Installing: ${PACKAGES[@]}"
sudo apt-get install -y -qq "${PACKAGES[@]}"

echo -e "${GREEN}✓ System dependencies installed${NC}"
echo ""

###############################################################################
# Step 3: Create Python Virtual Environment
###############################################################################

echo -e "${YELLOW}[Step 3/7]${NC} Creating Python virtual environment..."

cd "$PROJECT_ROOT"

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
python3 -m venv venv

echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

###############################################################################
# Step 4: Install Python Packages
###############################################################################

echo -e "${YELLOW}[Step 4/7]${NC} Installing Python packages..."

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install packages from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "${RED}ERROR: requirements.txt not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python packages installed${NC}"
echo ""

###############################################################################
# Step 5: Set File Permissions
###############################################################################

echo -e "${YELLOW}[Step 5/7]${NC} Setting file permissions..."

# Make all Python files executable
chmod +x *.py
chmod +x sentient_aura/*.py
chmod +x daemons/*.py 2>/dev/null || true

# Make this install script executable
chmod +x install.sh

# Create logs directory if it doesn't exist
mkdir -p logs
chmod 755 logs

echo -e "${GREEN}✓ File permissions set${NC}"
echo ""

###############################################################################
# Step 6: Verify Models
###############################################################################

echo -e "${YELLOW}[Step 6/7]${NC} Verifying models..."

# Check Vosk model
if [ -d "models/vosk/vosk-model-small-en-us-0.15" ]; then
    echo -e "${GREEN}✓ Vosk model found${NC}"
else
    echo -e "${RED}✗ Vosk model not found in models/vosk/${NC}"
    echo "  You may need to download it from: https://alphacephei.com/vosk/models"
fi

# Check Piper model
if [ -f "models/piper/en_US-lessac-medium.onnx" ]; then
    echo -e "${GREEN}✓ Piper voice model found${NC}"
else
    echo -e "${RED}✗ Piper voice model not found in models/piper/${NC}"
    echo "  You may need to download it from Piper TTS"
fi

echo ""

###############################################################################
# Step 7: System Configuration
###############################################################################

echo -e "${YELLOW}[Step 7/7]${NC} Configuring system..."

# Enable I2C (for Raspberry Pi sensors)
if command -v raspi-config &> /dev/null; then
    echo "Enabling I2C interface..."
    sudo raspi-config nonint do_i2c 0 2>/dev/null || true
fi

# Add user to required groups
echo "Adding user to required groups..."
sudo usermod -a -G gpio,i2c,spi,audio "$USER" 2>/dev/null || true

echo -e "${GREEN}✓ System configured${NC}"
echo ""

###############################################################################
# Installation Complete
###############################################################################

echo -e "${BLUE}========================================================================${NC}"
echo -e "${GREEN}   INSTALLATION COMPLETE!${NC}"
echo -e "${BLUE}========================================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. ${GREEN}Activate the virtual environment:${NC}"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "2. ${GREEN}Configure Porcupine access key (for wake word detection):${NC}"
echo "   Edit ${BLUE}sentient_aura/config.py${NC}"
echo "   Get free key at: ${BLUE}https://picovoice.ai/console/${NC}"
echo ""
echo "3. ${GREEN}Run the system:${NC}"
echo "   ${BLUE}python3 supervisor.py${NC}           # Production mode with auto-restart"
echo "   ${BLUE}python3 sentient_aura_main.py${NC}   # Direct mode"
echo ""
echo "4. ${GREEN}Test individual components:${NC}"
echo "   ${BLUE}python3 test_phase2_integration.py${NC}"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "   - PHASE_2_COMPLETE.md    - Hardware integration details"
echo "   - PHASE_3_PROGRESS.md    - System hardening features"
echo "   - PHASE_3_QUICKSTART.md  - Quick start guide"
echo ""
echo -e "${RED}IMPORTANT:${NC} Log out and back in for group permissions to take effect!"
echo ""
echo -e "${BLUE}========================================================================${NC}"
