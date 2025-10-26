# Multi-Accelerator Architecture - Sentient Core v4

**Hardware Platform:** Raspberry Pi 500+ with THREE AI accelerators
**Status:** Design Phase - Hardware arriving soon
**Philosophy:** Specialized accelerators for different AI tasks

---

## Hardware Inventory

### 1. Google Coral Edge TPU (USB Accelerator)
- **Performance:** 4 TOPS
- **Power:** 2.0W
- **Efficiency:** 2 TOPS/W
- **Framework:** TensorFlow Lite only (int8 quantization required)
- **Interface:** USB 3.0
- **Cost:** ~$60
- **Status:** ✅ **CURRENTLY AVAILABLE**
- **Age:** 2019 technology (6 years old)

### 2. Raspberry Pi AI HAT+ (Hailo-8L or Hailo-8)
- **Performance:** 13 TOPS (Hailo-8L) or 26 TOPS (Hailo-8)
- **Power:** 4W (13 TOPS) or 8W (26 TOPS)
- **Efficiency:** 3-4 TOPS/W
- **Framework:** TensorFlow, PyTorch via Hailo SDK
- **Interface:** PCIe Gen 3.0 (via Pi 5's PCIe port)
- **Cost:** $70 (13 TOPS) or $110 (26 TOPS)
- **Status:** 🔜 **ARRIVING SOON**
- **Age:** 2024 technology (latest)

### 3. NVIDIA Jetson Orin Nano Dev Kit
- **Performance:** 20 TOPS (10W) or 40 TOPS (15W)
- **Power:** 7-15W
- **Efficiency:** 2.7 TOPS/W
- **Framework:** Full PyTorch, TensorFlow, TensorRT, CUDA, cuDNN
- **GPU:** 512/1024-core NVIDIA Ampere
- **CPU:** 6-core Arm Cortex-A78AE
- **Cost:** $499
- **Status:** 🔜 **ARRIVING SOON**
- **Age:** 2023 technology

### Total System Capability
- **Combined TOPS:** 4 + 26 + 40 = **70 TOPS**
- **Combined Power:** 2W + 8W + 15W = **25W** (still less than a light bulb!)
- **Framework Coverage:** TFLite, TensorFlow, PyTorch, TensorRT, CUDA

---

## Accelerator Role Specialization

### Google Coral Edge TPU - "THE VISUALIZER"

**Primary Role:** Real-time particle control (pixel behavior generation)

**Strengths:**
- ✅ Ultra-low power (2W) - can run 24/7
- ✅ Fast inference (<5ms) for small models
- ✅ Mature TensorFlow Lite ecosystem
- ✅ Deterministic performance

**Weaknesses:**
- ❌ TensorFlow Lite only (no PyTorch)
- ❌ Strict quantization requirements (int8)
- ❌ Older technology (2019)
- ❌ Smallest TOPS (4)

**Assigned Tasks:**
1. **Particle Behavior Generation** - 22 sensors → 12 parameters @ 60Hz
2. **Ambient Awareness** - Low-level sensor fusion
3. **Always-On Inference** - Background monitoring
4. **Fallback Inference** - When other accelerators busy

**Model:** `sentient_pixel_controller_edgetpu.tflite` (50KB, <5ms)

---

### Raspberry Pi AI HAT+ (26 TOPS) - "THE PERCEIVER"

**Primary Role:** Computer vision and object detection

**Strengths:**
- ✅ Newest technology (2024 Hailo-8)
- ✅ Highest TOPS/W efficiency (3-4 TOPS/W)
- ✅ PCIe Gen 3.0 (low latency, high bandwidth)
- ✅ Built-in rpicam integration
- ✅ Native on Raspberry Pi 5

**Weaknesses:**
- ⚠️ Hailo SDK learning curve
- ⚠️ Less mature ecosystem than Coral/Jetson

**Assigned Tasks:**
1. **Object Detection** - YOLOv8, MobileNet SSD (real-time 30 FPS)
2. **Face Recognition** - Identify humans in camera feed
3. **Semantic Segmentation** - Understand scene composition
4. **Pose Estimation** - Track human body positions
5. **Image Classification** - Identify objects in environment

**Models:**
- `yolov8n_hailo.hef` - Object detection (nano variant, 80 classes)
- `mobilenet_ssd_hailo.hef` - Lightweight detection
- `facial_recognition_hailo.hef` - Face identification
- `segmentation_hailo.hef` - Semantic segmentation

**Integration:**
```python
from hailo_platform import HailoRT

class HailoVisionEngine:
    def __init__(self):
        self.device = HailoRT.create_device()
        self.yolo_network = self.device.create_infer_model("yolov8n_hailo.hef")

    def detect_objects(self, frame):
        """Run YOLOv8 object detection on video frame."""
        results = self.yolo_network.run(frame)
        return self.parse_yolo_output(results)
```

---

### NVIDIA Jetson Orin Nano - "THE THINKER"

**Primary Role:** Complex AI, LLMs, and heavy computation

**Strengths:**
- ✅ Highest raw TOPS (40)
- ✅ Full CUDA/cuDNN support
- ✅ Native PyTorch (no conversion needed)
- ✅ Can run LLMs (quantized)
- ✅ GPU compute for general tasks
- ✅ Training capability (not just inference)

**Weaknesses:**
- ❌ Highest power consumption (15W)
- ❌ Most expensive ($499)
- ❌ Overkill for simple tasks

**Assigned Tasks:**
1. **Local LLM Inference** - Run quantized 7B models (Llama 3, Mistral)
2. **Voice Processing** - Advanced speech-to-text (Whisper)
3. **Natural Language Understanding** - Conversational AI
4. **Audio Synthesis** - High-quality TTS (Piper, Bark)
5. **Complex Sensor Fusion** - Multi-modal AI tasks
6. **Model Training** - Fine-tune models on-device
7. **Generative AI** - Image generation, style transfer

**Models:**
- `llama-3-8b-instruct-q4.gguf` - Conversational LLM (4-bit quantized)
- `whisper-base.trt` - Speech recognition (TensorRT optimized)
- `stable-diffusion-2.1.trt` - Image generation
- `bark-voice-synthesis.onnx` - Advanced TTS

**Integration:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class OrinLanguageEngine:
    def __init__(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3-8B-Instruct",
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B-Instruct")

    def process_command(self, text):
        """Process natural language command with LLM."""
        inputs = self.tokenizer(text, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**inputs, max_length=200)
        return self.tokenizer.decode(outputs[0])
```

---

## Task Allocation Matrix

| Task | Accelerator | Reason |
|------|-------------|--------|
| **Particle control (60Hz)** | Coral TPU | Low latency, low power, always-on |
| **Object detection** | Pi AI HAT | Optimized for vision, best TOPS/W |
| **Face recognition** | Pi AI HAT | Computer vision specialty |
| **Voice commands (STT)** | Orin Nano | Whisper model, high accuracy |
| **Conversational AI** | Orin Nano | LLM inference, complex reasoning |
| **TTS synthesis** | Orin Nano | High-quality audio generation |
| **Sensor fusion (simple)** | Coral TPU | Real-time, lightweight |
| **Sensor fusion (complex)** | Orin Nano | Multi-modal, heavy computation |
| **Image generation** | Orin Nano | Stable Diffusion, GPU required |
| **Model fine-tuning** | Orin Nano | Only one with training capability |
| **Ambient monitoring** | Coral TPU | 24/7 low-power operation |
| **Scene understanding** | Pi AI HAT | Semantic segmentation |
| **Pose tracking** | Pi AI HAT | Human pose estimation |
| **Emergency fallback** | Coral TPU | Most reliable, always available |

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SENSOR LAYER                           │
│  Camera, Mic, IMU, Environment, WiFi, BT, GPS, Power, etc.  │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DAEMON LAYER                             │
│   Vision, Audio, Hardware Monitor, WiFi Scanner, etc.       │
└─────┬──────────────┬──────────────────────┬─────────────────┘
      │              │                      │
      │              │                      │
┌─────▼──────┐  ┌───▼──────┐  ┌───────────▼────────────────┐
│  Pi AI HAT │  │ Orin Nano│  │      Coral TPU             │
│  (26 TOPS) │  │ (40 TOPS)│  │      (4 TOPS)              │
│            │  │          │  │                            │
│  YOLO v8   │  │ LLM 8B   │  │  Pixel Controller          │
│  Face Rec  │  │ Whisper  │  │  Sensor Fusion             │
│  Seg       │  │ Piper    │  │  Always-on Monitor         │
└─────┬──────┘  └───┬──────┘  └───────────┬────────────────┘
      │             │                      │
      │             │                      │
      └─────────────┴──────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   WORLD STATE                               │
│         Centralized state with accelerator metadata        │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              SENTIENT CORE                                  │
│        Consciousness loop + decision making                 │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│           VISUALIZATION LAYER                               │
│    WebGL particles driven by Coral real-time inference      │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Strategy

### Phase 1: Coral TPU Only (CURRENT)
**Status:** Design complete, ready to train

```python
# sentient_core.py
self.pixel_engine = CoralPixelEngine()  # Particle control

# Runs at 60 FPS, <5ms latency
params = self.pixel_engine.predict_particle_params(world_state)
```

**Capabilities:**
- ✅ Particle visualization
- ✅ Basic sensor fusion
- ✅ WiFi/BT monitoring

---

### Phase 2: Add Pi AI HAT (WHEN IT ARRIVES)
**Status:** Waiting for hardware

```python
# sentient_core.py
self.vision_engine = HailoVisionEngine()  # Object detection
self.pixel_engine = CoralPixelEngine()    # Particle control

# Vision runs at 30 FPS
objects = self.vision_engine.detect_objects(camera_frame)

# Update WorldState with detected objects
world_state.update_vision({
    'detected_objects': objects,
    'faces_detected': self.vision_engine.detect_faces(camera_frame)
})

# Coral uses vision data to control particles
params = self.pixel_engine.predict_particle_params(world_state)
```

**New Capabilities:**
- ✅ Real-time object detection
- ✅ Face recognition
- ✅ Scene understanding
- ✅ Particles react to detected objects

---

### Phase 3: Add Orin Nano (WHEN IT ARRIVES)
**Status:** Waiting for hardware

```python
# sentient_core.py
self.language_engine = OrinLanguageEngine()  # LLM
self.vision_engine = HailoVisionEngine()     # Vision
self.pixel_engine = CoralPixelEngine()       # Particles

# Voice command → LLM processing
user_speech = self.language_engine.speech_to_text(audio)
llm_response = self.language_engine.process_command(user_speech)
synthesized_speech = self.language_engine.text_to_speech(llm_response)

# All accelerators working together
```

**Full Capabilities:**
- ✅ Conversational AI
- ✅ Advanced voice interaction
- ✅ Complex reasoning
- ✅ Generative features
- ✅ All sensors + all AI models

---

## Power Management

### Idle State (Low Power Mode)
```
Coral TPU:   2W (active, always monitoring)
Pi AI HAT:   0W (idle, no camera feed)
Orin Nano:   0W (powered off or sleep)
Total:       2W
```

### Active Monitoring (Camera On)
```
Coral TPU:   2W (particle control)
Pi AI HAT:   8W (object detection @ 30 FPS)
Orin Nano:   0W (sleep)
Total:       10W
```

### Full Engagement (User Interaction)
```
Coral TPU:   2W (particle control)
Pi AI HAT:   8W (vision processing)
Orin Nano:  15W (LLM conversation)
Total:      25W
```

### Power Budget Strategy
```python
class PowerManager:
    def __init__(self):
        self.max_power = 30.0  # Watts
        self.coral_always_on = True
        self.hailo_on_demand = True
        self.orin_on_request = True

    def allocate_workload(self, task):
        """Dynamically allocate tasks to minimize power."""
        current_power = self.get_current_draw()

        if task == 'particle_control':
            return 'coral'  # Always use Coral (2W)

        elif task == 'object_detection':
            if current_power + 8 < self.max_power:
                return 'hailo'  # Preferred for vision
            else:
                return None  # Skip if over budget

        elif task == 'llm_inference':
            if current_power + 15 < self.max_power:
                return 'orin'  # Only if power available
            else:
                return 'defer'  # Queue for later
```

---

## Model Training Strategy

### Coral Models (TensorFlow Lite)
**Trained in:** Google Colab
**Process:**
1. Train with TensorFlow/Keras
2. Apply quantization-aware training
3. Convert to TFLite with int8 quantization
4. Compile with `edgetpu_compiler`
5. Deploy to Raspberry Pi

### Hailo Models
**Trained in:** Hailo Dataflow Compiler
**Process:**
1. Train with TensorFlow or PyTorch
2. Export to ONNX
3. Quantize with Hailo tools
4. Compile to HEF format
5. Deploy to Pi AI HAT

### Orin Models (TensorRT)
**Trained in:** PyTorch, then optimized with TensorRT
**Process:**
1. Train with PyTorch on cloud GPU
2. Quantize to FP16 or INT8
3. Convert to TensorRT engine
4. Deploy to Orin Nano

**OR use pre-trained:**
- Hugging Face models directly (no conversion needed!)
- GGUF quantized LLMs (llama.cpp)
- ONNX models

---

## Accelerator Selection Logic

```python
class AcceleratorRouter:
    """Routes AI tasks to optimal accelerator."""

    def __init__(self):
        self.coral = CoralPixelEngine()
        self.hailo = HailoVisionEngine()
        self.orin = OrinLanguageEngine()

    def route_task(self, task_type, data):
        """Route task to best accelerator."""

        # Particle control: ALWAYS Coral
        if task_type == 'particle_control':
            return self.coral.predict_particle_params(data)

        # Vision tasks: Prefer Hailo, fallback to Orin
        elif task_type == 'object_detection':
            if self.hailo.available:
                return self.hailo.detect_objects(data)
            elif self.orin.available:
                return self.orin.detect_objects_gpu(data)  # CUDA
            else:
                return []  # No detection available

        # Language tasks: ONLY Orin (no alternatives)
        elif task_type == 'llm_inference':
            if self.orin.available:
                return self.orin.process_command(data)
            else:
                return "LLM unavailable"  # Cannot run on Coral/Hailo

        # Sensor fusion: Coral for simple, Orin for complex
        elif task_type == 'sensor_fusion_simple':
            return self.coral.fuse_sensors(data)
        elif task_type == 'sensor_fusion_complex':
            return self.orin.multimodal_fusion(data)

        # Fallback
        else:
            raise ValueError(f"Unknown task type: {task_type}")
```

---

## Future: Multi-Model Ensemble

When all three accelerators are running simultaneously:

```python
# Example: Coral + Hailo + Orin working together
camera_frame = get_camera_frame()
audio_stream = get_audio_stream()
sensor_data = get_sensor_readings()

# Pi AI HAT: Vision processing (30 FPS)
detected_objects = hailo.detect_objects(camera_frame)
detected_faces = hailo.detect_faces(camera_frame)

# Orin Nano: Audio + LLM processing
transcribed_text = orin.speech_to_text(audio_stream)
llm_response = orin.process_with_vision_context(
    text=transcribed_text,
    vision_context=detected_objects
)

# Coral TPU: Real-time particle control (60 FPS)
world_state.update({
    'vision': {'detected_objects': detected_objects, 'faces': detected_faces},
    'audio': {'transcription': transcribed_text},
    'sensors': sensor_data
})
particle_params = coral.predict_particle_params(world_state)

# All three accelerators feeding the visualization!
```

**Result:** Sentient Core sees (Hailo), hears (Orin), understands (Orin), and visualizes (Coral) - **true multi-sensory AI**.

---

## Conclusion

### Tri-Accelerator Advantage

**Specialization > Generalization**

Instead of one powerful accelerator doing everything, we have THREE optimized for different domains:

1. **Coral** - Always-on, low-power, fast pixel control
2. **Hailo** - Efficient vision, camera integration
3. **Orin** - Complex AI, LLMs, generative models

**Combined:** 70 TOPS of specialized intelligence for 25W.

---

## Next Steps

1. ✅ **Complete Coral training** (current focus)
2. 🔜 **Wait for Pi AI HAT arrival** (integrate Hailo SDK)
3. 🔜 **Wait for Orin Nano arrival** (set up JetPack, test LLMs)
4. 🔄 **Implement AcceleratorRouter** (dynamic task allocation)
5. 🔄 **Train models for each platform** (TFLite, HEF, TensorRT)
6. 🎯 **Deploy full tri-accelerator system**

**The Sentient Core will see, hear, think, and visualize like never before.** 🧠✨

---

**Document Status:** Complete
**Last Updated:** 2025-10-26
**Next Review:** When Pi AI HAT and Orin Nano arrive
