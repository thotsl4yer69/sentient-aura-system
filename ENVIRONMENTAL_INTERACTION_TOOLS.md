# Sentient Core v4 - Environmental Interaction Tools

## Overview

The Sentient Core has multiple ways to interact with and control its physical environment through hardware actuators and smart home integrations.

---

## 🔧 Arduino Actuators (Hardware Control)

### Available Hardware Outputs

The system has **2 Arduino actuators** discovered and ready to use:

#### 1. **Status LED** (Pin 13)
- **Type:** Single LED indicator
- **Purpose:** Visual feedback and status indication
- **Commands:** ON/OFF, brightness control
- **Use cases:**
  - System status indication (idle, busy, alert)
  - Visual notifications
  - Morse code communication
  - Activity indicator

#### 2. **LED Matrix** (Pin 14)
- **Type:** LED matrix display
- **Purpose:** Text/pattern display
- **Commands:** Display text, patterns, animations
- **Use cases:**
  - Display messages
  - Show sensor readings
  - Scrolling text
  - Alert patterns
  - Status icons

### How to Control Arduino Actuators

**Command Format:**
```python
# Write to an actuator
action = ActionCommand("arduino", "write", {
    "name": "status_led",  # or "led_matrix"
    "value": "ON"          # or message/pattern for matrix
})
```

**Examples:**
```python
# Turn on status LED
write:status_led:1

# Turn off status LED
write:status_led:0

# Display text on LED matrix
write:led_matrix:HELLO

# Show pattern
write:led_matrix:PATTERN_ALERT
```

**Current Status:** ✅ **Fully implemented and tested**
- Commands sent via serial to Arduino
- Response acknowledgment received
- World state updated automatically

---

## 🏠 Smart Home Control (Home Assistant Integration)

### Current Status: ⚠️ **Available but NOT Configured**

The system has a complete Home Assistant bridge implementation, but it's **not configured** (no token set).

### Capabilities When Configured

#### **Control Devices:**

**Lights:**
```python
# Turn on a light
homeassistant.turn_on("light.living_room")

# Dim to 50%
homeassistant.turn_on("light.bedroom", brightness=128)

# Change color
homeassistant.turn_on("light.kitchen", rgb_color=[255, 0, 0])
```

**Switches:**
```python
# Turn on/off
homeassistant.turn_on("switch.fan")
homeassistant.turn_off("switch.coffee_maker")

# Toggle
homeassistant.toggle("switch.desk_lamp")
```

**Climate Control:**
```python
# Set temperature
homeassistant.call_service("climate", "set_temperature",
    entity_id="climate.thermostat",
    service_data={"temperature": 72}
)
```

**Media Players:**
```python
# Play/pause
homeassistant.call_service("media_player", "media_play",
    entity_id="media_player.living_room")

# Adjust volume
homeassistant.call_service("media_player", "volume_set",
    entity_id="media_player.bedroom",
    service_data={"volume_level": 0.5}
)
```

**Covers (Blinds/Curtains):**
```python
homeassistant.call_service("cover", "open_cover", "cover.bedroom_blinds")
homeassistant.call_service("cover", "close_cover", "cover.living_room_curtains")
```

**Locks:**
```python
homeassistant.call_service("lock", "lock", "lock.front_door")
homeassistant.call_service("lock", "unlock", "lock.back_door")
```

**Scenes:**
```python
# Activate preset scenes
homeassistant.activate_scene("scene.movie_time")
homeassistant.activate_scene("scene.goodnight")
```

**Automations:**
```python
# Trigger automations
homeassistant.call_service("automation", "trigger", "automation.evening_routine")
```

#### **Query State:**

```python
# Get all entities
entities = homeassistant.get_states()

# Get specific entity
entity = homeassistant.get_entity("light.living_room")
print(f"Light is {entity.state}, brightness: {entity.attributes.get('brightness')}")

# Get all lights
lights = homeassistant.get_entities_by_domain("light")

# Get all on devices
active = homeassistant.get_entities_by_state("on")

# Summary
summary = homeassistant.summarize_state()
# Returns: "15 lights (8 on), 5 switches (2 on), 1 climate (heat)"
```

### How to Enable Home Assistant

1. **Get your token:**
   ```bash
   # In Home Assistant web UI:
   # Profile → Long-Lived Access Tokens → Create Token
   ```

2. **Add to .env:**
   ```bash
   ENABLE_HOMEASSISTANT=true
   HOMEASSISTANT_URL=http://localhost:8123
   HOMEASSISTANT_TOKEN=your_token_here
   ```

3. **Restart Sentient Core**

---

## 🎤 Voice Output (Text-to-Speech)

### Piper TTS - Currently Active

**Capabilities:**
- Natural female voice (en_US-lessac-medium)
- 150 words per minute
- 90% volume
- Async speech generation

**How It Works:**
- AI responses automatically spoken
- Queue-based system prevents overlap
- Clean audio playback via ALSA

**Status:** ✅ **Fully working**

---

## 🧠 LLM-Driven Actions

### How the AI Can Control Things

The Sentient Core uses **Llama 3.2 3B** to understand natural language commands and translate them into actions.

**Example Interaction Flow:**

```
User: "Turn on the living room light"
  ↓
LLM processes intent → "smart_home_control"
  ↓
Extract entities → domain: "light", entity: "living_room", action: "turn_on"
  ↓
Execute → homeassistant.turn_on("light.living_room")
  ↓
Confirm → "I've turned on the living room light"
```

**Example with Arduino:**

```
User: "Blink the status LED"
  ↓
LLM processes intent → "hardware_control"
  ↓
Generate command → write:status_led:BLINK_PATTERN
  ↓
Execute → Arduino receives command
  ↓
Confirm → "Status LED is now blinking"
```

---

## 📊 Current Environmental Awareness

### Sensor Inputs (Read-Only)

The system has **4 Arduino sensors** providing environmental data:

1. **DHT1** (Temperature & Humidity)
   - Real-time ambient conditions
   - Used for context in responses

2. **Ultrasonic** (Distance/Proximity)
   - Detects nearby objects/people
   - Triggers proximity alerts

3. **PIR** (Motion Detection)
   - Passive infrared motion sensing
   - Security and presence detection

4. **Microphone** (Audio Level)
   - Acoustic spike detection
   - Noise level monitoring
   - Voice activity detection

### Contextual Awareness

The LLM receives sensor data automatically:

```
"You are the Sentient Core, an AI companion system...
Current System Status:
- Temperature: 22.5°C
- Humidity: 45%
- Pressure: 1013 hPa
- Vision: Detected 2 objects
- ALERT: Motion detected in room"
```

This allows for **context-aware responses**:
- "It's getting warm in here" (uses temp sensor)
- "I sense movement nearby" (uses PIR sensor)
- "The ambient light is low" (uses environmental data)

---

## 🔄 Integration Architecture

### Data Flow

```
User Input (Voice/Text)
         ↓
    LLM Processing (Llama 3.2 3B)
         ↓
    Intent Detection
         ↓
   ┌─────┴─────┐
   ↓           ↓
Arduino     Home Assistant
Actions      Actions
   ↓           ↓
Hardware    Smart Home
 Control     Control
   ↓           ↓
   └─────┬─────┘
         ↓
   World State Update
         ↓
  Feedback to User (TTS)
```

### Command Processing Pipeline

1. **User Input** → Text or voice command
2. **LLM Analysis** → Intent detection, entity extraction
3. **Action Routing** → Determine target system (Arduino/HA/System)
4. **Execution** → Send commands via appropriate bridge
5. **Confirmation** → Update world state, generate response
6. **Feedback** → TTS output to user

---

## 🚀 What Can It Do Right Now?

### ✅ Currently Working

1. **Read all sensors** (6 peripherals)
   - Temperature, humidity, motion, distance, audio level

2. **Control Arduino actuators** (2 outputs)
   - Status LED (on/off/brightness)
   - LED Matrix (display text/patterns)

3. **Speak responses** (TTS)
   - Natural voice output
   - Context-aware replies

4. **Natural language understanding**
   - Intent detection
   - Entity extraction
   - Contextual reasoning

### ⚠️ Available But Not Configured

1. **Smart Home Control** (Home Assistant)
   - Requires: HOME_ASSISTANT_TOKEN in .env
   - Once configured: Full control over all HA entities

2. **Weather API** (OpenWeatherMap)
   - Requires: OPENWEATHER_API_KEY in .env
   - Once configured: Live weather data + sensor fusion

### ✅ Recently Configured

1. **Web Search** (Brave API)
   - Status: ✅ **CONFIGURED AND READY**
   - API Key: Added (BSA-oDMBTB3fU7b4P5Nv68PgiJrlx2Z)
   - Capabilities: Real-time web search, result caching, rate limiting
   - Restart required: Yes (to activate)

---

## 💡 Example Use Cases

### Scenario 1: Morning Routine
```
User: "Good morning, prepare the house"

AI processes:
1. Checks time (morning detected)
2. Reads sensors (temperature, light level)
3. Executes:
   - Turn on lights (Home Assistant)
   - Set LED matrix to "GOOD MORNING"
   - Adjust thermostat based on temp
   - Blink status LED for confirmation
4. Responds: "Good morning! I've turned on the lights and set
   the temperature to 72°F. Current room temp is 68°F."
```

### Scenario 2: Security Alert
```
PIR sensor detects motion (when user is away)
  ↓
AI analyzes:
1. Checks if expected (normal schedule?)
2. If unexpected:
   - Blinks status LED red
   - Shows "ALERT" on LED matrix
   - Turns on security lights (HA)
   - Locks doors (HA)
   - Records event in memory
   - (Future: Send notification)
```

### Scenario 3: Environmental Response
```
DHT sensor reads: Temperature 78°F (too warm)
  ↓
AI responds autonomously:
1. Detects temperature threshold exceeded
2. Executes:
   - Turn on ceiling fan (HA)
   - Lower blinds (HA)
   - Adjust AC if available (HA)
   - LED matrix: "COOLING ACTIVATED"
3. Logs: "Room temperature was 78°F, activated cooling"
```

---

## 🔧 Developer: How to Add New Actions

### Arduino Actions

1. **Update Arduino sketch** to handle new command
2. **Send command** via `write:peripheral_name:value`
3. **Parse response** in `arduino_daemon.py`

### Home Assistant Actions

1. **Ensure HA bridge configured** (token in .env)
2. **Use existing methods:**
   ```python
   homeassistant.turn_on(entity_id)
   homeassistant.call_service(domain, service, entity_id, data)
   ```
3. **AI automatically** understands natural language → action

### Custom Actions

1. **Add intent** to command recognition system
2. **Implement handler** in `sentient_core_enhanced.py`
3. **Test** with natural language input

---

## 📈 Future Enhancements (Not Yet Implemented)

- **Flipper Zero Integration** - RF control, RFID, NFC
- **Vision System** - Object detection via Coral TPU
- **GPS Navigation** - Location awareness
- **LoRaWAN Communication** - Long-range mesh networking
- **4G LTE** - Internet anywhere
- **Proactive Automation** - AI-initiated actions based on patterns

---

## 🎯 Summary

**Current Tools Available:**

| Category | Tool | Status | Purpose |
|----------|------|--------|---------|
| **Hardware** | Status LED | ✅ Working | Visual feedback |
| **Hardware** | LED Matrix | ✅ Working | Display messages |
| **Voice** | Piper TTS | ✅ Working | Speech output |
| **Sensors** | 4x Arduino sensors | ✅ Working | Environmental awareness |
| **Smart Home** | Home Assistant | ⚠️ Not configured | Control lights/switches/etc |
| **LLM** | Llama 3.2 3B | ✅ Working | Natural language understanding |
| **Memory** | PostgreSQL | ✅ Working | Conversation persistence |
| **Search** | Brave API | ✅ Configured (restart needed) | Web information |
| **Weather** | OpenWeatherMap | ⚠️ Not configured | Live weather data |

**To unlock full capabilities:**
1. ✅ ~~Add Brave API key~~ → **Web search READY** (restart to activate)
2. Add Home Assistant token → Smart home control
3. Add Weather API key → Live weather + sensor fusion

The foundation is **production-ready**. You can control hardware right now and add smart home control in minutes!
