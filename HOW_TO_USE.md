# How to Use Sentient Core v4

## ✅ System is Running!

Your Sentient Core GUI is now running with **all bugs fixed** and **6 Arduino peripherals** actively discovered.

## 🎮 Keyboard Controls

**Press `S` key** - Show/hide sensor display panel
- Displays all detected hardware sensors
- Shows Arduino peripherals (DHT, ultrasonic, PIR, mic, LEDs, matrix)
- Real-time sensor status

**Press `ESC` key** - Quit the system

## 💬 How to Talk to the AI

### Method 1: Text Input (GUI)
1. **Click** in the text input box at the bottom of the window
2. **Type** your message
3. **Press ENTER** to send
4. Watch the AI respond using Llama 3.2 3B

### Examples to Try:
- "Hello, how are you?"
- "What sensors do you have?"
- "Tell me about yourself"
- "What's the temperature?"

## 📡 Discovered Peripherals

Your system has **6 Arduino sensors** working:

1. **DHT1** (Pin 2) - Temperature & Humidity sensor
2. **Ultrasonic1** (Pin 9) - Distance sensor (proximity detection)
3. **PIR1** (Pin 24) - Motion detection sensor
4. **Mic1** (Pin 57) - Audio level monitoring
5. **Status LED** (Pin 13) - Visual feedback actuator
6. **LED Matrix** (Pin 14) - Display output actuator

### ⏰ Important: Sensor Boot Time
- Arduino takes **5-10 seconds** to boot after system start
- Initially shows "0 peripherals discovered"
- After boot complete, discovers all 6 peripherals
- This is normal behavior!

## 🧠 AI Configuration

**LLM Backend:** Ollama (local inference)
- **Model:** llama3.2:3b (3 billion parameters)
- **Host:** http://localhost:11434
- **Status:** ✓ Working with fixes applied

**Voice Output:** Piper TTS
- **Voice:** en_US-lessac-medium (natural female)
- **Status:** ✓ Working

**Voice Input:** Disabled (no microphone detected)
- Use GUI text input instead
- Or run: `python text_interface.py` for terminal interface

## 📊 Hardware Status (Corrected)

```
COMPUTE: 1/2 available
  ✓ Google Coral Edge TPU (4 TOPS) - REAL
  ✗ Raspberry Pi AI HAT+ (not installed) - FIXED!

LOCATION: 1/2 available
  ✓ GPS Module (I2C 0x10)
  ✗ LIDAR Scanner

COMMUNICATION: 1/3 available
  ✓ LoRaWAN Radio
  ✗ Flipper Zero
  ✗ 4G LTE Modem

CONTROLLER: 1/1 available
  ✓ Arduino (6 peripherals)
```

## 🎨 GUI Features

### Friendly Face
- Animated eyes that blink naturally
- Moving pupils for realistic expression
- Dynamic smile that responds to system state
- More expressive during PROCESSING and SPEAKING

### Conversation History
- Left panel shows last 6 messages
- Color-coded: **Blue** = AI, **Orange** = You
- Auto-scrolls with new messages
- Word-wrapped for long messages

### Status Display
- Shows current system state (LISTENING, PROCESSING, SPEAKING)
- Animated orb changes color based on state
- Particle effects during processing

## 🐛 Bugs Fixed (2025-10-24)

1. ✅ **AI HAT+ false positive** - Now correctly shows as not installed
2. ✅ **Particle rendering crash** - Alpha attribute initialized properly
3. ✅ **LLM generator error** - Fixed streaming code, responses work correctly

## 🚀 Launch Commands

**GUI Mode (current):**
```bash
cd /home/mz1312/Sentient-Core-v4
source venv/bin/activate
python sentient_aura_main.py
```

**Text Interface Mode:**
```bash
cd /home/mz1312/Sentient-Core-v4
source venv/bin/activate
python text_interface.py
```

## 📝 Conversation Examples

**Example 1: Simple greeting**
```
You: hello
AI: [Processes with Llama 3.2 3B and responds naturally]
```

**Example 2: Sensor query**
```
You: what sensors do you have?
AI: [Describes discovered Arduino peripherals and capabilities]
```

**Example 3: Status check**
```
You: how are you feeling?
AI: [Uses sensor data to provide context-aware response]
```

## ⚙️ System Information

**Process ID:** Check with `ps aux | grep sentient_aura_main`

**Logs:** All output saved to `sentient_launch.log`

**View logs in real-time:**
```bash
tail -f sentient_launch.log
```

**Check sensor readings:**
```bash
grep "arduino - INFO" sentient_launch.log | tail -20
```

## 🔧 Troubleshooting

### Peripherals not showing?
- **Wait 5-10 seconds** after launch for Arduino to boot
- Check logs: `grep "Discovered.*peripherals" sentient_launch.log`
- Press **S** key to refresh sensor display

### Text input not responding?
- Click in the text input box to focus it
- Make sure the GUI window has focus
- Check logs for "GUI command received" messages

### LLM not responding?
- Check Ollama is running: `curl http://localhost:11434/api/version`
- Start Ollama if needed: `ollama serve` (in another terminal)
- Model loaded: `ollama list | grep llama3.2`

### System crashes?
- All critical bugs are fixed in this version
- If issues occur, check: `tail -50 sentient_launch.log`

## 📚 Additional Documentation

- **Bug fixes:** See `BUGS_FIXED_2025-10-24.md`
- **GUI improvements:** See `GUI_IMPROVEMENTS.md`
- **Production fixes:** See `FIXES_APPLIED.md`
- **Hardware requirements:** See `HARDWARE_REQUIREMENTS.md`

## 🎯 Next Steps

1. **Test text input** - Type "hello" and press ENTER
2. **View sensors** - Press **S** key to see all peripherals
3. **Have a conversation** - Ask questions and interact naturally
4. **Monitor sensors** - Watch Arduino readings update in real-time

Enjoy your fully operational Sentient Core v4! 🚀
