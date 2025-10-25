# Sentient Core v4 - Hardware Requirements & Solutions

## Current System Status

The Sentient Core v4 is running on a Raspberry Pi 500+ (ARM64) with the following component statuses:

### ✅ Working Components
- **Arduino Daemon**: Successfully connected via /dev/ttyACM0
- **Discovered Peripherals**: 6 devices (dht1, ultrasonic1, pir1, mic1, status_led, led_matrix)
- **GUI Interface**: Fully functional with Pygame visualization
- **Core AI Brain**: Processing and responding to commands

### ⚠️ Missing/Optional Hardware

#### 1. **Microphone (Voice Input)**
**Status**: Not detected - Voice input disabled
**Impact**: System cannot accept voice commands
**Solutions**:
- **USB Microphone**: Plug in any USB microphone (recommended: Blue Yeti Nano, Samson Meteor)
- **I2S Microphone**: Connect an I2S MEMS microphone module (e.g., INMP441, SPH0645)
- **USB Audio Interface**: Use a USB audio interface with XLR/3.5mm input
- **Alternative**: Use text_interface.py for text-based interaction (no hardware needed)

#### 2. **BME280 Environmental Sensor**
**Status**: Not detected on I2C bus
**Impact**: No temperature/humidity/pressure monitoring
**Solutions**:
- **Connect BME280**: Wire BME280 sensor to I2C pins (SDA/SCL)
  - Raspberry Pi 500+ uses I2C bus 13 or 14
  - Address: 0x76 or 0x77
- **Alternative Sensors**:
  - DHT22/AM2302: Temperature & humidity (simpler, GPIO-based)
  - BMP280: Temperature & pressure only
  - SHT31: High-accuracy temperature & humidity
- **Simulation Mode**: Enable SIMULATION_MODE in prototype_board_daemon.py

#### 3. **GPIO Sensors (PIR Motion)**
**Status**: GPIO initialization attempted but no hardware connected
**Impact**: No motion detection from PIR sensor
**Solutions**:
- **Connect PIR Sensor**: Wire PIR sensor to GPIO17
- **Install gpiod**: For Raspberry Pi 5/500+ compatibility:
  ```bash
  sudo apt-get install python3-libgpiod gpiod
  pip install gpiod
  ```
- **Simulation Mode**: Already enabled to prevent errors

#### 4. **MCP3008 ADC (Analog Microphone)**
**Status**: SPI initialization attempted but no hardware
**Impact**: No analog microphone level detection
**Solutions**:
- **Connect MCP3008**: Wire MCP3008 ADC chip via SPI
- **Alternative**: Use USB microphone instead (digital, no ADC needed)

## Recommended Hardware Setup

### Minimum Configuration (Voice-Enabled)
1. **USB Microphone** - $20-50
2. **Arduino with sensors** (already connected) - $30-50
3. Total: ~$50-100

### Full Configuration (All Features)
1. **USB Microphone** - $20-50
2. **BME280 Sensor** - $5-10
3. **PIR Motion Sensor** - $3-5
4. **MCP3008 ADC Chip** - $3-5
5. **Arduino with sensors** (already connected) - $30-50
6. **Jumper wires & breadboard** - $10-15
7. Total: ~$71-135

### Professional Configuration
1. **High-quality USB Audio Interface** - $100-200
2. **Professional Microphone** - $50-150
3. **BME680 (includes gas sensor)** - $15-20
4. **Multiple PIR sensors** - $10-15
5. **Arduino Mega with expanded sensors** - $40-60
6. **Custom PCB for clean wiring** - $20-30
7. Total: ~$235-475

## API Keys & Services

### Missing Service Configurations
1. **Search Service**: No API key configured
   - Solution: Add BRAVE_API_KEY to environment or config file
   - Get free key from: https://brave.com/search/api/

2. **Home Assistant**: No token configured
   - Solution: Add HOME_ASSISTANT_TOKEN to config
   - Generate from: Home Assistant → Profile → Long-Lived Access Tokens

## Quick Setup Commands

### Install Required Libraries (Raspberry Pi 500+)
```bash
# GPIO support for Pi 5/500+
sudo apt-get update
sudo apt-get install python3-libgpiod gpiod python3-spidev python3-smbus2

# Python packages
cd /home/mz1312/Sentient-Core-v4
source venv/bin/activate
pip install gpiod spidev smbus2 adafruit-circuitpython-bme280

# Audio support
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio sounddevice
```

### Test Hardware Detection
```bash
# List audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Check I2C devices
i2cdetect -y 1  # Or -y 13 for Pi 5

# Check GPIO access
gpioinfo

# Test Arduino connection
ls /dev/ttyACM*
```

### Enable Simulation Mode (No Hardware)
Edit `/home/mz1312/Sentient-Core-v4/daemons/prototype_board_daemon.py`:
```python
SIMULATION_MODE = True  # Already set
```

## Troubleshooting

### Issue: "Cannot determine SOC peripheral base address"
**Cause**: Raspberry Pi 5/500+ uses different GPIO chip
**Solution**: Already fixed - daemon now tries gpiod first, falls back to RPi.GPIO

### Issue: "No microphone detected"
**Cause**: No audio input device connected
**Solution**: Connect USB microphone or use text_interface.py

### Issue: "No I2C bus with BME280 found"
**Cause**: BME280 not connected or wrong I2C bus
**Solution**: Check wiring, run `i2cdetect -y 13` to scan bus

### Issue: "Search service unavailable"
**Cause**: No API key configured
**Solution**: Set BRAVE_API_KEY environment variable

## Running Without Hardware

The system can run in full simulation mode:

1. **GUI Mode (Visual only)**:
   ```bash
   cd /home/mz1312/Sentient-Core-v4
   source venv/bin/activate
   python sentient_aura_main.py
   ```

2. **Text Mode (No voice/GUI)**:
   ```bash
   cd /home/mz1312/Sentient-Core-v4
   source venv/bin/activate
   python text_interface.py
   ```

3. **Headless Mode**:
   ```bash
   python sentient_aura_main.py --headless
   ```

## Contact & Support

For hardware questions or component recommendations:
- Check the project README.md
- Review Arduino sketch for peripheral connections
- Simulation mode allows full testing without hardware

## Summary

The Sentient Core v4 is designed to be hardware-flexible:
- **Runs without hardware**: GUI and core AI work in simulation
- **Modular design**: Add sensors as needed
- **Graceful degradation**: Missing hardware doesn't crash the system
- **Multiple interfaces**: Voice, text, or API access

The system automatically detects available hardware and adapts its capabilities accordingly.