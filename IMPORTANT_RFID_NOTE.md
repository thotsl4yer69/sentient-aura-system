# IMPORTANT: MFRC522 Software SPI Configuration

## Issue
The standard MFRC522 library does NOT support software SPI through custom pins. It only works with the hardware SPI pins.

## Your Hardware Configuration
- **LED Matrix**: Uses Hardware SPI (pins 50, 51, 52) + CS pin 14
- **RFID Reader**: Configured for custom pins (35, 33, 37, 39)

## Solutions

### Option 1: Use Hardware SPI for RFID (RECOMMENDED)
Move the RFID reader to use the hardware SPI pins and use different CS pins for each device:

**Wiring Changes:**
```
MFRC522 RFID Reader:
- Move MOSI to pin 51 (shared with LED Matrix)
- Move MISO to pin 50 (shared with LED Matrix)
- Move SCK to pin 52 (shared with LED Matrix)
- Keep SS/CS on pin 39 (unique to RFID)
- Keep RST on pin 8

MAX7219 LED Matrix:
- DIN (MOSI) on pin 51 (shared)
- CLK (SCK) on pin 52 (shared)
- CS on pin 14 (unique to LED Matrix)
```

Both devices can share the SPI bus (MOSI, MISO, SCK) as long as they have unique CS/SS pins.

### Option 2: Software SPI Library for RFID
Install a modified MFRC522 library that supports software SPI:
```bash
# Install SoftSPI-compatible MFRC522
cd ~/Arduino/libraries/
git clone https://github.com/miguelbalboa/rfid.git MFRC522
```

Then modify the sketch to use `MFRC522Extended` with software SPI support.

### Option 3: Use Only Hardware SPI (Keep Current Sketch)
If you're willing to rewire the RFID reader to use hardware SPI pins, the current sketch will work perfectly. Just move:
- RFID MOSI from pin 35 → pin 51
- RFID MISO from pin 33 → pin 50
- RFID SCK from pin 37 → pin 52
- Keep RFID SS on pin 39
- Keep RFID RST on pin 8

## Current Sketch Status
The sketch I created assumes **Option 3** (hardware SPI for both devices). The software SPI pin definitions are in the code but won't be used by the MFRC522 library.

## Recommendation
**Rewire the RFID reader to use hardware SPI** (Option 3). This is the simplest and most reliable solution. Both the LED Matrix and RFID reader can coexist on the same SPI bus with different CS pins.

Would you like me to update the sketch for Option 1 (proper hardware SPI sharing)?
