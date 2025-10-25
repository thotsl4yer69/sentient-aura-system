#!/usr/bin/env python3
"""
Sentient Core v4 - Unified Configuration
All system settings in one place.
Portable with relative paths.
"""

import os

# ============================================================================
# PATHS (RELATIVE TO PROJECT ROOT)
# ============================================================================

# Project root is the parent directory of sentient_aura/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Models (now included in project directory)
VOSK_MODEL_PATH = os.path.join(PROJECT_ROOT, "models/vosk/vosk-model-small-en-us-0.15")
PIPER_MODEL_FILE = os.path.join(PROJECT_ROOT, "models/piper/en_US-lessac-medium.onnx")
PIPER_VOICE_PATH = os.path.join(PROJECT_ROOT, "models/piper")

# Logs
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Config directory
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
os.makedirs(CONFIG_DIR, exist_ok=True)

# ============================================================================
# AUDIO SETTINGS
# ============================================================================

SAMPLE_RATE = 16000  # Hz (Vosk/Piper standard)
CHUNK_SIZE = 4096
CHANNELS = 1  # Mono

# Microphone (for systems with hardware mic)
MIC_DEVICE_INDEX = None  # None = default device
MIC_ADC_CHANNEL = 0  # For MCP3008 ADC

# Voice Activity Detection
VAD_THRESHOLD = 0.5
SILENCE_DURATION = 1.5  # seconds of silence to end phrase

# ============================================================================
# SPEECH RECOGNITION (Vosk)
# ============================================================================

VOSK_ENABLED = True
VOSK_LOG_LEVEL = -1  # -1 = silent, 0 = errors only

# ============================================================================
# WAKE WORD DETECTION (Porcupine) - Phase 3
# ============================================================================

# Get free access key at: https://picovoice.ai/console/
# (Required for Porcupine 3.0+)
PORCUPINE_ACCESS_KEY = None  # Set to your key: "your-key-here"

# Wake words (must be in Porcupine's built-in list)
# Available: computer, jarvis, alexa, hey google, ok google, hey siri, porcupine, etc.
WAKE_WORDS = ['computer', 'jarvis']

# How long to listen for commands after wake word (seconds)
COMMAND_LISTEN_DURATION = 15

# Enable wake word mode (False = continuous listening without wake word)
USE_WAKE_WORD = False  # Set to False to disable wake word and use continuous mode

# ============================================================================
# TEXT-TO-SPEECH (Piper)
# ============================================================================

PIPER_MODEL = "en_US-lessac-medium"  # Natural female voice
PIPER_RATE = 150  # Words per minute
PIPER_VOLUME = 0.9  # 0.0 to 1.0

# ============================================================================
# VISUAL INTERFACE (Pygame Aura)
# ============================================================================

# Window
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FULLSCREEN = False
FPS = 30

# Aura orb
ORB_RADIUS = 150  # pixels
ORB_CENTER_X = WINDOW_WIDTH // 2
ORB_CENTER_Y = WINDOW_HEIGHT // 2

# Colors (RGB tuples)
COLOR_IDLE = (0, 128, 255)          # Calm Blue
COLOR_LISTENING = (0, 180, 255)     # Bright Blue
COLOR_PROCESSING = (255, 255, 170)  # White/Yellow
COLOR_SPEAKING = (0, 255, 255)      # Cyan
COLOR_EXECUTING = (139, 0, 255)     # Vibrant Purple
COLOR_THREAT = (255, 0, 0)          # Alert Red
COLOR_ERROR = (255, 69, 0)          # Red/Orange
COLOR_BACKGROUND = (10, 10, 20)     # Dark blue-black

# Animation speeds (Hz)
PULSE_SPEED_IDLE = 0.5
PULSE_SPEED_LISTENING = 1.0
PULSE_SPEED_PROCESSING = 2.0
PULSE_SPEED_SPEAKING = 1.5
PULSE_SPEED_THREAT = 4.0

# Particle effects
PARTICLES_ENABLED = True
PARTICLE_COUNT_PROCESSING = 50
PARTICLE_COUNT_EXECUTING = 30

# ============================================================================
# SENTIENT CORE (Brain)
# ============================================================================

# States
STATE_IDLE = "IDLE"
STATE_LISTENING = "LISTENING"
STATE_PROCESSING = "PROCESSING"
STATE_SPEAKING = "SPEAKING"
STATE_EXECUTING = "EXECUTING"
STATE_THREAT = "THREAT_ALERT"
STATE_ERROR = "ERROR"

# Personality
PERSONALITY_STYLE = "friendly"  # friendly, professional, casual
VERBOSITY = "medium"  # brief, medium, verbose
USE_CONTRACTIONS = True  # "I'm" vs "I am"
HUMOR_ENABLED = True

# Response templates
ACKNOWLEDGMENTS = [
    "Got it!",
    "Sure thing!",
    "On it!",
    "You got it!",
    "Absolutely!",
]

CONFIRMATIONS = [
    "Done!",
    "All set!",
    "Complete!",
    "Finished!",
]

# ============================================================================
# COMMAND RECOGNITION
# ============================================================================

# Command keywords (lowercase)
COMMANDS = {
    # Status queries
    'status': ['status', 'sensors', 'show sensors', 'how are you', 'system status'],
    'health': ['health', 'feeling', 'doing', 'how are you'],

    # Actions
    'scan': ['scan', 'scan frequencies', 'check frequencies', 'rf scan'],
    'monitor': ['monitor', 'watch', 'keep an eye', 'track'],
    'alert': ['alert', 'notify', 'tell me', 'let me know'],

    # Queries
    'temperature': ['temperature', 'temp', 'how hot', 'how cold'],
    'threats': ['threats', 'danger', 'anything suspicious', 'all clear'],
    'location': ['where', 'location', 'position'],

    # System
    'help': ['help', 'what can you do', 'commands'],
    'test': ['test', 'demo', 'demonstration'],
}

# Wake phrases (optional - system listens continuously by default)
WAKE_PHRASES = [
    'hey core',
    'core',
    'sentient',
]

WAKE_WORD_REQUIRED = False  # Set to True to require wake word

# ============================================================================
# HARDWARE INTEGRATION
# ============================================================================

# Use existing hardware discovery
USE_HARDWARE_DISCOVERY = True

# Daemons to monitor
MONITOR_FLIPPER = True
MONITOR_VISION = True
MONITOR_PROTOTYPE_BOARD = True

# Action executor
USE_ACTION_EXECUTOR = True
ACTION_SIMULATION_MODE = False  # Set True for testing without hardware

# ============================================================================
# SENSOR DISPLAY
# ============================================================================

SENSOR_ICONS = {
    'camera_rgb': '👁',
    'flipper_zero': '📡',
    'pir_motion': '🚶',
    'microphone_array': '🔊',
    'bme280_env': '🌡',
    'arduino': '💾',
}

SENSOR_DISPLAY_DURATION = 5.0  # seconds to show sensor display
SENSOR_ICON_SIZE = 64  # pixels
SENSOR_ICON_SPACING = 100  # pixels between icons

# ============================================================================
# NETWORK CONFIGURATION (Merged from drone defense config)
# ============================================================================

# Mind-Body Architecture
MIND_HOST = "127.0.0.1"  # IP address of the Mind (Host PC)
BODY_HOST = "0.0.0.0"    # IP address of the Body (Raspberry Pi)

# Communication Ports
STREAMING_PORT = 9999
COMMAND_PORT = 10000
IMAGE_PORT = 10001

# ============================================================================
# SYSTEM INFORMATION
# ============================================================================

SYSTEM_NAME = "Sentient Core v4.0"
SYSTEM_VERSION = "4.0.0"
SYSTEM_CODENAME = "Resilient"

# Drone Defense Mode
DRONE_DEFENSE_MODE = True  # Enable RF scanning and countermeasures

# ============================================================================
# WORLD STATE CONFIGURATION
# ============================================================================

MAX_HISTORY_SIZE = 1000   # Maximum number of historical events to keep
WORLD_STATE_TTL = 60      # Time-to-live for world state entries (seconds)

# ============================================================================
# AI CONFIGURATION
# ============================================================================

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
CORAL_MODEL_PATH = os.path.join(MODELS_DIR, "mobilenet_v2_1.0_224_quant_edgetpu.tflite")
CORAL_LABELS_PATH = os.path.join(MODELS_DIR, "imagenet_labels.txt")
OBJECT_DETECTION_CONFIDENCE = 0.5
ENABLE_AI_ACCELERATION = True

# ============================================================================
# CORAL VISUALIZATION TPU CONFIGURATION
# ============================================================================

# Enhanced 120-feature multi-sensor fusion model
CORAL_VIZ_ENABLED = True
CORAL_VIZ_MODEL_PATH = os.path.join(MODELS_DIR, "sentient_viz_enhanced_edgetpu.tflite")
CORAL_VIZ_TARGET_FPS = 60
CORAL_VIZ_FALLBACK_MODE = 'llm'  # 'llm' or 'static'
CORAL_VIZ_ENABLE_METRICS = True
CORAL_VIZ_INTERPOLATION_ALPHA = 0.3  # EMA smoothing (0-1)

# Performance tuning
CORAL_VIZ_CPU_AFFINITY = [2]  # Pin to core 2
CORAL_VIZ_FEATURE_CACHE_TTL = 0.1  # 100ms cache for psutil
CORAL_VIZ_WARMUP_FRAMES = 5

# Monitoring
CORAL_VIZ_LOG_SLOW_FRAMES = True
CORAL_VIZ_SLOW_FRAME_THRESHOLD_MS = 20.0
CORAL_VIZ_METRICS_REPORT_INTERVAL = 5.0  # seconds

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = os.path.join(LOG_DIR, "sentient_aura.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# PERFORMANCE
# ============================================================================

# Threading
MAX_WORKER_THREADS = 4

# Timeouts (seconds)
SPEECH_RECOGNITION_TIMEOUT = 10
TTS_TIMEOUT = 5
COMMAND_EXECUTION_TIMEOUT = 30

# Memory
MAX_CONVERSATION_HISTORY = 50  # Keep last N interactions

# ============================================================================
# DEVELOPMENT/DEBUG
# ============================================================================

DEBUG_MODE = False
SHOW_FPS = True
SHOW_AUDIO_LEVELS = False
PRINT_TRANSCRIPTIONS = True
PRINT_STATE_CHANGES = True

# Simulations (for testing without hardware)
SIMULATE_MICROPHONE = False
SIMULATE_CAMERA = False
SIMULATE_SENSORS = False

# ============================================================================
# API INTEGRATION CONFIGURATION
# ============================================================================

# Enable API integration features
ENABLE_API_INTEGRATION = True

# API Services (controlled via .env file)
# See .env.template for configuration options

# LLM Integration
USE_LLM_FOR_RESPONSES = True  # Use LLM for intelligent responses instead of templates
LLM_FALLBACK_TO_TEMPLATES = False  # NO scripted fallbacks - AI must be honest when it can't think

# Web Search Integration
ENABLE_WEB_SEARCH = True  # Enable web search for information queries

# Weather Integration
ENABLE_WEATHER_API = True  # Enable weather API integration
FUSE_WEATHER_WITH_SENSORS = True  # Combine API weather with local sensor data

# Smart Home Integration
ENABLE_SMART_HOME_CONTROL = True  # Enable Home Assistant integration
SMART_HOME_VOICE_COMMANDS = True  # Allow voice control of smart home

# Memory & Learning
ENABLE_CONVERSATION_MEMORY = True  # Store conversations in database
ENABLE_CONTEXT_RETRIEVAL = True  # Retrieve conversation context for LLM
CONVERSATION_CONTEXT_WINDOW = 10  # Number of recent messages to include

# API Manager Settings
API_TIMEOUT = 30  # Default API timeout in seconds
API_RETRY_ATTEMPTS = 2  # Number of retry attempts for failed API calls
API_CACHE_ENABLED = True  # Enable caching of API responses

# Advanced LLM Settings
LLM_STREAMING_RESPONSES = False  # Enable streaming for real-time responses (experimental)
LLM_INJECT_SENSOR_CONTEXT = True  # Include sensor data in LLM context

# Intent Detection Enhancement
USE_LLM_FOR_INTENT = False  # Use LLM for intent detection (vs keyword matching)
INTENT_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for intent detection

# Natural Language Commands
NLP_ENHANCED_COMMANDS = True  # Allow more natural command phrasing
COMMAND_CONFIRMATION = False  # Ask for confirmation before executing commands

# ============================================================================
# EXPORT ALL CONSTANTS
# ============================================================================

# Export all uppercase constants (all settings)
__all__ = [name for name in dir() if name.isupper() and not name.startswith('_')]
