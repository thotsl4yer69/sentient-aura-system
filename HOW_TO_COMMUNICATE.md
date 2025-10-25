# How to Communicate with Sentient Core

The **3D visualizer is display-only** - it shows the consciousness state but doesn't have a communication interface. Here's how to actually interact with the system:

---

## Option 1: Text Chat (Recommended)

**Open a NEW terminal** and run:

```bash
cd /home/mz1312/Sentient-Core-v4
source venv/bin/activate
python3 simple_chat.py
```

Then just type naturally:
```
You: hello
Sentient: [AI response after 30-40 seconds]

You: what's the weather like?
Sentient: [AI response]

Commands:
  clear - Clear conversation
  quit  - Exit
```

The visualizer will automatically react to the conversation states.

---

## Option 2: Voice Input (If Microphone Connected)

The system is already listening! Just speak naturally. The visualizer will show:
- **Blue** (listening) → **Green** (processing) → **Orange** (speaking)

**No wake word needed** - it's continuous listening mode.

---

## Option 3: Manual State Testing (Visualizer Only)

Press keyboard keys in the visualizer window:

| Key | State | Color | Morph |
|-----|-------|-------|-------|
| **1** | IDLE | Blue | Avatar (head) |
| **2** | LISTENING | Blue | Avatar (head) |
| **3** | PROCESSING | Green | World (torus knot) |
| **4** | SPEAKING | Orange | Avatar (head) |
| **5** | EXECUTING | Purple | Mid-morph |
| **6** | THREAT ALERT | Red | World (torus knot) |
| **Space** | Reset | Blue | Reconnect to backend |
| **H** | Toggle Controls | - | Show/hide help |

This is just for testing - real states come from the backend.

---

## What You Should See

### In the Visualizer

**Top-left info box** shows:
```
SENTIENT CORE
State: LISTENING
Status: Listening...

— SENSORS —
Temperature: 22.5°C    (if sensor connected)
Humidity: 45.2%        (if sensor connected)
Audio: 15%             (if microphone active)
Motion: DETECTED       (if camera sees motion)
Objects: 3             (if camera sees objects)

Active Daemons:
• arduino
• vision
```

**Bottom-right controls**:
```
CONTROLS
Drag: Rotate • Scroll: Zoom
1-6: Test States • Space: Reset
H: Toggle Help
```

### In the Chat Terminal

```
Starting Sentient Core Chat Interface...
✓ Connected to Ollama
✓ Using model: llama3.2:3b

Type 'quit' to exit, 'clear' to reset conversation
Ready to chat!

You: _
```

---

## Understanding the States

The visualizer reacts to the backend's state machine:

1. **IDLE** → System waiting
2. **LISTENING** → Capturing voice/waiting for input
3. **PROCESSING** → AI thinking (LLM generating response)
4. **SPEAKING** → Delivering response via TTS
5. **EXECUTING** → Performing hardware action
6. **THREAT_ALERT** → Security event detected

**States flow automatically** based on your interaction.

---

## Monitoring Backend

**Watch system logs:**
```bash
tail -f /tmp/sentient_gui.log
```

**Check WebSocket messages (Browser Console F12):**
```javascript
WebSocket connection established
Received message: {type: "state_update", state: "listening", ...}
Sensor data updated: {temperature: 22.5, humidity: 45.2, ...}
```

---

## Troubleshooting

### "Can't communicate with visualizer"
✅ **Correct**: The visualizer is display-only
❌ Don't try to type in the visualizer window
✅ Use `simple_chat.py` in a separate terminal

### "Not responding to voice"
- Check if microphone is connected: `arecord -l`
- System is in continuous listening mode
- First response takes 30-60s (model loading)

### "Visualizer not updating"
- Check browser console (F12) for WebSocket errors
- Press **Space** to reconnect
- Verify backend is running: `lsof -i :8765`

### "States not changing"
- Backend must be running (`ps aux | grep sentient_aura_main`)
- Use `simple_chat.py` to trigger state changes
- Or use keyboard (1-6) for manual testing

---

## Quick Test Sequence

**Terminal 1** (already running):
```bash
# Backend is running, visualizer is open
```

**Terminal 2** (open this now):
```bash
cd /home/mz1312/Sentient-Core-v4
source venv/bin/activate
python3 simple_chat.py
```

Type in Terminal 2:
```
You: hello
```

Watch Terminal 1 visualizer:
- Blue (listening) → Green (processing) → Orange (speaking)
- Info box updates with state
- Model morphs between head and torus knot

**That's the complete system working!**

---

## Summary

| Want to... | Use this... |
|-----------|-------------|
| Chat with AI | `python3 simple_chat.py` in new terminal |
| Talk with voice | Just speak (if mic connected) |
| Test states manually | Press 1-6 keys in visualizer |
| See system state | Look at visualizer (top-left) |
| Monitor backend | `tail -f /tmp/sentient_gui.log` |
| Check WebSocket | Browser console (F12) |

**The visualizer is the eyes - the chat is the voice.**

Use both together for the full sentient experience!
