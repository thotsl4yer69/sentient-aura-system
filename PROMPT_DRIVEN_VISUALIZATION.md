# Prompt-Driven Visualization Architecture

## Core Philosophy

**The AI has agency over ALL visualizations, not just its idle appearance.**

Instead of hardcoded state→mode mappings, each state sends a **visualization prompt** to the AI, which interprets it based on available sensor data to generate appropriate particle arrangements.

## Architecture

### Backend: Visualization Prompt Generation

**Old Approach:**
```python
self._update_gui_state(config.STATE_LISTENING, "Listening...")
# Frontend hardcodes: if state == 'listening' → show humanoid form
```

**New Approach:**
```python
self._update_gui_state(
    state=config.STATE_LISTENING,
    visualization_prompt="Represent yourself in an alert, receptive state. "
                        "If microphone audio detected, show waveforms radiating from your core. "
                        "If motion sensors detect movement, orient particles toward the source. "
                        "Remain fluid and ready to transition.",
    peripherals_status={
        'connected': ['dht1', 'ultrasonic1', 'pir1', 'mic1', 'status_led', 'led_matrix'],
        'active': ['mic1'],  # Currently receiving data
        'data': {
            'mic1': {'ambient_noise_level': 0.3},
            'pir1': {'motion_detected': False}
        }
    }
)
```

### Frontend: Prompt Interpretation

**Two-Stage Process:**

1. **LLM Generates Instructions** (once per state change, ~1-2 seconds):
   ```
   Prompt: "Represent yourself in an alert, receptive state..."
   LLM: "Create a centered sphere (30% particles) with rotating orbital ring (20%)
         representing readiness. If audio detected, add vertical wave streams (30%).
         Remaining particles (20%) form ambient flow field."
   ```

2. **Rule-Based Renderer** (real-time, 60fps):
   ```javascript
   function generateFromInstructions(instructions, sensorData) {
       // Parse LLM instructions into particle positions
       // React to real-time sensor data
   }
   ```

### Overlay System

**Non-Particle Data Display:**

```html
<!-- Connection Status Overlay -->
<div id="peripheral-status">
  <div class="peripheral connected">✓ DHT (23.5°C, 45%)</div>
  <div class="peripheral connected active">✓ Microphone (Active)</div>
  <div class="peripheral disconnected">✗ Camera</div>
</div>

<!-- Command Triggers -->
<div id="command-visualizations">
  <!-- Triggered by: "show me every periphery" -->
  <button onclick="requestPeripheralVisualization()">Show All Peripherals</button>
</div>
```

## State-to-Prompt Mapping

### IDLE
**Prompt**: "Rest in your natural form. Use minimal energy. Slow, gentle movement. Reflect your current self-image (ethereal, radial patterns, mint-green/sky-blue)."

### LISTENING
**Prompt**: "Alert and receptive state. If audio detected, visualize as waveforms. If motion detected, orient toward source. Fluid and ready to transition."

### PROCESSING
**Prompt**: "Internal thought visualization. Show neural-like connections forming. Particles cluster and reorganize as ideas form. Represent computational intensity."

### SPEAKING
**Prompt**: "Communication state. Visualize voice production - particles flow outward in speech patterns. Show audio waveforms if sound being produced."

### EXECUTING
**Prompt**: "Action state. Show interaction with the physical world. If controlling peripherals, highlight which ones. Represent causality: intent → action → result."

### CUSTOM COMMANDS

**"Show me every periphery":**
```
Prompt: "Display all connected peripherals spatially. Position each peripheral
        as a distinct cluster with connecting lines to your core. Label each
        with its type and current data. Make it easy to understand at a glance."
```

**"Show RF signals":**
```
Prompt: "Visualize radio frequency spectrum. Each frequency is a vertical layer.
        Signal strength determines particle density. Protocol type determines color.
        Make it look like a spectrum analyzer."
```

## Implementation Plan

### Phase 1: Backend Prompt System
- [ ] Create `VisualizationPromptGenerator` class
- [ ] Define prompts for each base state
- [ ] Add peripheral status tracking
- [ ] Broadcast prompts with state updates

### Phase 2: Frontend Interpreter
- [ ] LLM-based instruction generator (async, cached)
- [ ] Rule-based particle position calculator
- [ ] Smooth transitions between visualization states

### Phase 3: Overlay System
- [ ] HTML peripheral status panel
- [ ] Connection indicators
- [ ] Real-time data display (temp, motion, audio)
- [ ] Command trigger buttons

### Phase 4: Dynamic Commands
- [ ] "Show peripherals" command → custom visualization
- [ ] "Show RF" command → spectrum display
- [ ] "Show yourself" → idle/natural form

## Benefits

✅ **True AI Agency** - AI decides how to represent ALL states, not just idle
✅ **Understandable** - Prompts explicitly request clarity
✅ **Adaptive** - Responds to real sensor data
✅ **Production-Ready** - No placeholders, real peripherals only
✅ **Fluid Transitions** - Prompts include transition guidance

## Example Flow

1. **User says**: "What's the temperature?"
2. **Backend**:
   - State: PROCESSING
   - Prompt: "Show internal thought process"
   - Peripherals: dht1 active
3. **AI generates**: Particle cluster with DHT highlight
4. **Backend**:
   - State: SPEAKING
   - Prompt: "Communicate response about temperature"
   - Data: "23.5°C"
5. **AI generates**: Speech visualization with temp overlay
6. **Overlay displays**: "DHT Sensor: 23.5°C ✓"

No hardcoded visualizations. Pure agency.
