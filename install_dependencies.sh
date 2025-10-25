#!/bin/bash
#
# Enhanced Sentient Core - Automated Dependency Installation
# For Raspberry Pi 5 (ARM64) running Raspberry Pi OS Bookworm
#
# Usage: ./install_dependencies.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_platform() {
    log_info "Checking platform..."

    if [ ! -f /proc/cpuinfo ]; then
        log_error "Cannot read /proc/cpuinfo"
        exit 1
    fi

    if grep -q "BCM2712" /proc/cpuinfo; then
        log_success "Detected Raspberry Pi 5"
    elif grep -q "BCM" /proc/cpuinfo; then
        log_warning "Detected Raspberry Pi (not Pi 5)"
        log_warning "This script is optimized for Pi 5 but will continue"
    else
        log_error "Not running on Raspberry Pi"
        exit 1
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
    log_success "System updated"
}

# Install system dependencies
install_system_packages() {
    log_info "Installing system packages..."

    sudo apt install -y \
        build-essential \
        git \
        curl \
        wget \
        libffi-dev \
        libssl-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        liblzma-dev \
        python3-dev \
        usbutils \
        i2c-tools \
        python3-serial \
        screen \
        minicom \
        portaudio19-dev \
        python3-pyaudio \
        espeak

    log_success "System packages installed"
}

# Install pyenv
install_pyenv() {
    log_info "Installing pyenv..."

    if [ -d "$HOME/.pyenv" ]; then
        log_warning "pyenv already installed"
    else
        curl https://pyenv.run | bash

        # Add to shell configuration
        if ! grep -q "PYENV_ROOT" ~/.bashrc; then
            echo '' >> ~/.bashrc
            echo '# pyenv configuration' >> ~/.bashrc
            echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
            echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
            echo 'eval "$(pyenv init -)"' >> ~/.bashrc
        fi

        # Load pyenv for current session
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"

        log_success "pyenv installed"
    fi
}

# Install Python 3.9
install_python39() {
    log_info "Installing Python 3.9.18..."

    # Load pyenv
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    if pyenv versions | grep -q "3.9.18"; then
        log_warning "Python 3.9.18 already installed"
    else
        pyenv install 3.9.18
        log_success "Python 3.9.18 installed"
    fi

    # Create or update coral-py39 virtualenv
    if pyenv versions | grep -q "coral-py39"; then
        log_warning "coral-py39 environment already exists"
    else
        pyenv virtualenv 3.9.18 coral-py39
        log_success "coral-py39 environment created"
    fi
}

# Install Google Coral Edge TPU runtime
install_coral_runtime() {
    log_info "Installing Google Coral Edge TPU runtime..."

    # Add repository if not already present
    if [ ! -f /etc/apt/sources.list.d/coral-edgetpu.list ]; then
        echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
            sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
            sudo apt-key add -

        sudo apt update
    fi

    # Install libedgetpu
    sudo apt install -y libedgetpu1-std

    log_success "Coral Edge TPU runtime installed"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."

    # Load pyenv
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    PYTHON="$HOME/.pyenv/versions/coral-py39/bin/python"
    PIP="$HOME/.pyenv/versions/coral-py39/bin/pip"

    # Upgrade pip
    $PIP install --upgrade pip

    # Install pycoral
    $PIP install --extra-index-url https://google-coral.github.io/py-repo/ pycoral

    # Install core dependencies
    $PIP install \
        numpy \
        opencv-python \
        pillow \
        pyserial \
        websockets \
        aiohttp \
        psutil \
        scikit-learn \
        tflite-runtime \
        requests

    # Install optional dependencies
    log_info "Installing optional dependencies..."
    $PIP install vosk piper-tts python-dotenv prometheus-client || {
        log_warning "Some optional dependencies failed to install (non-critical)"
    }

    log_success "Python dependencies installed"
}

# Configure udev rules
configure_udev() {
    log_info "Configuring udev rules..."

    # Coral TPU rules
    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="1a6e", GROUP="plugdev"' | \
        sudo tee /etc/udev/rules.d/99-edgetpu-accelerator.rules > /dev/null

    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="18d1", ATTRS{idProduct}=="9302", GROUP="plugdev"' | \
        sudo tee -a /etc/udev/rules.d/99-edgetpu-accelerator.rules > /dev/null

    # Serial device rules
    sudo tee /etc/udev/rules.d/99-sentient-serial.rules > /dev/null << 'EOF'
# Flipper Zero
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", SYMLINK+="flipper", GROUP="dialout", MODE="0666"

# Arduino Mega
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0042", SYMLINK+="arduino_mega", GROUP="dialout", MODE="0666"

# Arduino Uno (CH340)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="arduino_uno", GROUP="dialout", MODE="0666"
EOF

    # USB power management
    echo 'SUBSYSTEM=="usb", TEST=="power/control", ATTR{power/control}="on"' | \
        sudo tee /etc/udev/rules.d/50-usb-power.rules > /dev/null

    # Reload udev rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger

    log_success "udev rules configured"
}

# Add user to required groups
configure_groups() {
    log_info "Adding user to required groups..."

    sudo usermod -a -G plugdev $USER
    sudo usermod -a -G dialout $USER
    sudo usermod -a -G i2c $USER

    log_success "User added to groups: plugdev, dialout, i2c"
    log_warning "You must log out and back in for group changes to take effect"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Load pyenv
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    PYTHON="$HOME/.pyenv/versions/coral-py39/bin/python"

    # Check Python version
    VERSION=$($PYTHON --version)
    if [[ $VERSION == *"3.9"* ]]; then
        log_success "Python version: $VERSION"
    else
        log_error "Python version mismatch: $VERSION"
    fi

    # Check pycoral
    if $PYTHON -c "import pycoral" 2>/dev/null; then
        log_success "pycoral: OK"
    else
        log_error "pycoral: FAILED"
    fi

    # Check numpy
    if $PYTHON -c "import numpy" 2>/dev/null; then
        log_success "numpy: OK"
    else
        log_error "numpy: FAILED"
    fi

    # Check websockets
    if $PYTHON -c "import websockets" 2>/dev/null; then
        log_success "websockets: OK"
    else
        log_error "websockets: FAILED"
    fi

    # Check Coral TPU (if connected)
    if lsusb | grep -q "18d1:9302"; then
        log_success "Coral USB Accelerator detected"
    else
        log_warning "Coral USB Accelerator not detected (connect it after installation)"
    fi
}

# Main installation flow
main() {
    echo "=========================================="
    echo "  Enhanced Sentient Core Installation"
    echo "  Raspberry Pi 5 Dependencies"
    echo "=========================================="
    echo ""

    check_platform
    update_system
    install_system_packages
    install_pyenv
    install_python39
    install_coral_runtime
    install_python_deps
    configure_udev
    configure_groups
    verify_installation

    echo ""
    echo "=========================================="
    log_success "Installation complete!"
    echo "=========================================="
    echo ""
    log_warning "IMPORTANT: Log out and back in for group changes to take effect"
    echo ""
    log_info "Next steps:"
    echo "  1. Log out and back in (or run: exec \$SHELL)"
    echo "  2. Connect hardware peripherals (Coral TPU, Flipper Zero, Arduino)"
    echo "  3. Read HARDWARE_CONNECTIONS.md for wiring instructions"
    echo "  4. Read PERIPHERAL_CONFIGURATION.md for device configuration"
    echo ""
}

# Run main installation
main
