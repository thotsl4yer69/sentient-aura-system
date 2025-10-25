#!/usr/bin/env python3
"""
Continuous Speech Listener with Wake Word Detection - Phase 3 Upgrade
Two-state operation for efficiency:
1. WAKE_WORD_LISTENING - Low power, Porcupine listening for wake word
2. COMMAND_LISTENING - High power, Vosk full speech-to-text

Flow:
- Start in WAKE_WORD_LISTENING state
- Wake word detected → COMMAND_LISTENING for 15 seconds
- Command processed or timeout → back to WAKE_WORD_LISTENING
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import queue
import json
import threading
import logging
import time
import pyaudio
import struct
from enum import Enum

# Import Porcupine for wake word
import pvporcupine

# Import Vosk for speech-to-text
from vosk import Model, KaldiRecognizer

from . import config

logger = logging.getLogger("continuous_listener")


class ListenerState(Enum):
    """Listener operating states."""
    WAKE_WORD_LISTENING = "wake_word"    # Low power - waiting for wake word
    COMMAND_LISTENING = "command"        # High power - full speech recognition
    STOPPED = "stopped"


class ContinuousListenerWithWakeWord:
    """
    Continuous speech recognition with wake word detection.

    Operates in two states for efficiency:
    - WAKE_WORD_LISTENING: Low CPU, Porcupine only
    - COMMAND_LISTENING: Full Vosk speech-to-text (time-limited)
    """

    def __init__(self, callback=None, wake_words=None):
        """
        Initialize the listener with wake word detection.

        Args:
            callback: Function to call with transcribed text (text: str)
            wake_words: List of wake words to use (default: ['computer', 'jarvis'])
        """
        logger.info("Initializing Wake Word Listener...")

        # Callback for transcriptions
        self.callback = callback

        # Wake word configuration
        self.wake_words = wake_words or config.WAKE_WORDS or ['computer', 'jarvis']
        self.command_listen_duration = config.COMMAND_LISTEN_DURATION  # seconds after wake word

        # Audio setup
        self.sample_rate = 16000  # Porcupine requires 16kHz
        self.chunk_size = 512     # Porcupine frame length
        self.channels = 1

        # PyAudio
        self.audio = None
        self.stream = None

        # Porcupine wake word detector
        self.porcupine = None

        # Vosk model for speech-to-text
        self.vosk_model = None
        self.recognizer = None

        # State machine
        self.state = ListenerState.STOPPED
        self.command_listen_until = 0  # Timestamp when to return to wake word mode

        # Threading
        self.running = False
        self.thread = None
        self.text_queue = queue.Queue()

        # Stats
        self.wake_word_detections = 0
        self.total_transcriptions = 0
        self.last_wake_word_time = 0
        self.last_transcription_time = 0

        # Initialize wake word detector
        self._init_porcupine()

        # Load Vosk model
        self._load_vosk_model()

        logger.info("✓ Wake Word Listener initialized")
        logger.info(f"  Wake words: {self.wake_words}")
        logger.info(f"  Command listen duration: {self.command_listen_duration}s")

    def _init_porcupine(self):
        """Initialize Porcupine wake word detector."""
        logger.info("Initializing Porcupine wake word detector...")

        try:
            # Get access key (Porcupine 3.0 requires an access key)
            access_key = config.PORCUPINE_ACCESS_KEY if hasattr(config, 'PORCUPINE_ACCESS_KEY') else None

            if access_key:
                # Use API key for Porcupine 3.0+
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=self.wake_words
                )
            else:
                # Try without access key (will fail with Porcupine 3.0+)
                try:
                    self.porcupine = pvporcupine.create(keywords=self.wake_words)
                except:
                    logger.warning(
                        "Porcupine requires an access key. Get one free at https://picovoice.ai/console/\n"
                        "Add to config.py: PORCUPINE_ACCESS_KEY = 'your-key-here'\n"
                        "Falling back to continuous listening mode without wake word."
                    )
                    self.porcupine = None
                    return

            logger.info(f"✓ Porcupine initialized with wake words: {self.wake_words}")
            logger.info(f"  Sample rate: {self.sample_rate} Hz")
            logger.info(f"  Frame length: {self.porcupine.frame_length}")

        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            logger.warning("Falling back to continuous listening without wake word")
            self.porcupine = None

    def _load_vosk_model(self):
        """Load the Vosk speech recognition model."""
        logger.info(f"Loading Vosk model from {config.VOSK_MODEL_PATH}...")

        if not os.path.exists(config.VOSK_MODEL_PATH):
            raise FileNotFoundError(
                f"Vosk model not found at {config.VOSK_MODEL_PATH}\n"
                "Download it from: https://alphacephei.com/vosk/models"
            )

        # Load model
        self.vosk_model = Model(config.VOSK_MODEL_PATH)
        logger.info("✓ Vosk model loaded")

    def _create_recognizer(self):
        """Create a fresh Vosk recognizer (called when entering command mode)."""
        if self.recognizer:
            # Reset existing recognizer
            self.recognizer.Reset()
        else:
            # Create new recognizer
            self.recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
            self.recognizer.SetWords(True)

    def _setup_audio(self):
        """Initialize PyAudio and audio stream."""
        logger.info("Setting up audio input...")

        self.audio = pyaudio.PyAudio()

        # Find the right input device
        device_index = config.MIC_DEVICE_INDEX if hasattr(config, 'MIC_DEVICE_INDEX') else None

        if device_index is None:
            device_info = self.audio.get_default_input_device_info()
            device_index = device_info['index']
            logger.info(f"Using default input device: {device_info['name']}")

        # Open audio stream
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            logger.info("✓ Audio stream opened")
        except Exception as e:
            logger.error(f"Failed to open audio stream: {e}")
            raise

    def _enter_wake_word_mode(self):
        """Enter wake word listening mode."""
        logger.info("→ Entering WAKE_WORD_LISTENING mode")
        self.state = ListenerState.WAKE_WORD_LISTENING

    def _enter_command_mode(self):
        """Enter command listening mode (triggered by wake word)."""
        logger.info("→ Entering COMMAND_LISTENING mode")
        self.state = ListenerState.COMMAND_LISTENING
        self.command_listen_until = time.time() + self.command_listen_duration

        # Create fresh recognizer
        self._create_recognizer()

        logger.info(f"  Listening for commands for {self.command_listen_duration}s...")

    def _process_audio(self):
        """Main audio processing loop with state machine."""
        logger.info("Audio processing thread started")

        try:
            self._setup_audio()

            # Start in wake word mode if Porcupine available, else command mode
            if self.porcupine:
                self._enter_wake_word_mode()
            else:
                logger.warning("Porcupine not available - running in continuous command mode")
                self._enter_command_mode()
                self.command_listen_until = float('inf')  # Never timeout

            while self.running:
                # Read audio chunk
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                except Exception as e:
                    logger.error(f"Error reading audio: {e}")
                    time.sleep(0.1)
                    continue

                # Process based on current state
                if self.state == ListenerState.WAKE_WORD_LISTENING:
                    # Wake word detection mode (low power)
                    self._process_wake_word(data)

                elif self.state == ListenerState.COMMAND_LISTENING:
                    # Full speech recognition mode (high power)
                    self._process_command(data)

                    # Check if command mode should timeout
                    if time.time() > self.command_listen_until:
                        logger.info("Command listening timeout - returning to wake word mode")
                        if self.porcupine:
                            self._enter_wake_word_mode()
                        else:
                            # No Porcupine - stay in command mode forever
                            self.command_listen_until = float('inf')

        except Exception as e:
            logger.error(f"Audio processing error: {e}")
        finally:
            self._cleanup_audio()

        logger.info("Audio processing thread stopped")

    def _process_wake_word(self, audio_data):
        """Process audio for wake word detection (Porcupine)."""
        # Convert audio bytes to array of int16
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, audio_data)

        # Check for wake word
        keyword_index = self.porcupine.process(pcm)

        if keyword_index >= 0:
            # Wake word detected!
            wake_word = self.wake_words[keyword_index]
            self.wake_word_detections += 1
            self.last_wake_word_time = time.time()

            logger.info(f"🎯 WAKE WORD DETECTED: '{wake_word}'")

            # Switch to command listening mode
            self._enter_command_mode()

    def _process_command(self, audio_data):
        """Process audio for full speech recognition (Vosk)."""
        if self.recognizer.AcceptWaveform(audio_data):
            # Full result available
            result = json.loads(self.recognizer.Result())
            text = result.get('text', '').strip()

            if text:
                self.total_transcriptions += 1
                self.last_transcription_time = time.time()

                logger.info(f"📝 Transcribed: '{text}'")

                # Add to queue
                self.text_queue.put(text)

                # Call callback if provided
                if self.callback:
                    try:
                        self.callback(text)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")

                # After successful transcription, return to wake word mode
                if self.porcupine:
                    logger.info("Command processed - returning to wake word mode")
                    self._enter_wake_word_mode()

        else:
            # Partial result (for debugging)
            if config.PRINT_TRANSCRIPTIONS:
                partial = json.loads(self.recognizer.PartialResult())
                partial_text = partial.get('partial', '')
                if len(partial_text) > 3:
                    logger.debug(f"Partial: '{partial_text}'")

    def _cleanup_audio(self):
        """Clean up audio resources."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None

    def start(self):
        """Start the wake word listener in a background thread."""
        if self.running:
            logger.warning("Listener already running")
            return

        logger.info("Starting wake word listener...")
        self.running = True
        self.state = ListenerState.STOPPED  # Will transition in thread
        self.thread = threading.Thread(target=self._process_audio, daemon=True)
        self.thread.start()
        logger.info("✓ Wake word listener started")

    def stop(self):
        """Stop the listener."""
        if not self.running:
            return

        logger.info("Stopping wake word listener...")
        self.running = False
        self.state = ListenerState.STOPPED

        if self.thread:
            self.thread.join(timeout=2)

        # Cleanup Porcupine
        if self.porcupine:
            try:
                self.porcupine.delete()
            except:
                pass

        logger.info("✓ Wake word listener stopped")

    def get_text(self, timeout=None):
        """Get the next transcribed text from the queue."""
        try:
            return self.text_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def has_text(self):
        """Check if there's text available in the queue."""
        return not self.text_queue.empty()

    def get_stats(self):
        """Get listener statistics."""
        return {
            'running': self.running,
            'state': self.state.value,
            'wake_word_detections': self.wake_word_detections,
            'total_transcriptions': self.total_transcriptions,
            'last_wake_word_time': self.last_wake_word_time,
            'last_transcription_time': self.last_transcription_time,
            'queue_size': self.text_queue.qsize()
        }


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    print("=" * 60)
    print("Wake Word Listener Test")
    print("=" * 60)
    print(f"Say wake word: 'computer' or 'jarvis'")
    print("Then speak your command within 15 seconds")
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    def on_transcription(text):
        print(f"\n>>> COMMAND: '{text}'\n")

    # Create listener
    listener = ContinuousListenerWithWakeWord(callback=on_transcription)

    try:
        listener.start()

        while True:
            time.sleep(1)

            # Display stats every 10 seconds
            if int(time.time()) % 10 == 0:
                stats = listener.get_stats()
                print(f"\n[Stats] State: {stats['state']}, "
                      f"Wake words: {stats['wake_word_detections']}, "
                      f"Commands: {stats['total_transcriptions']}")

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        listener.stop()
        print("✓ Test complete")
