#!/usr/bin/env python3
"""
Continuous Speech Listener - Ears for Sentient Aura

Phase 3: Now supports two modes:
1. Regular mode - Continuous Vosk speech recognition
2. Wake word mode - Porcupine wake word + Vosk (more efficient)

Set config.USE_WAKE_WORD to enable wake word mode.
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
from vosk import Model, KaldiRecognizer

from . import config

logger = logging.getLogger("continuous_listener")


class ContinuousListener:
    """Continuous speech recognition using Vosk."""

    def __init__(self, callback=None):
        """
        Initialize the continuous listener.

        Args:
            callback: Function to call with transcribed text (text: str)
        """
        logger.info("Initializing Continuous Listener...")

        # Callback for transcriptions
        self.callback = callback

        # Audio setup
        self.sample_rate = config.SAMPLE_RATE
        self.chunk_size = config.CHUNK_SIZE
        self.channels = config.CHANNELS

        # PyAudio
        self.audio = None
        self.stream = None

        # Vosk model
        self.model = None
        self.recognizer = None

        # Threading
        self.running = False
        self.thread = None
        self.text_queue = queue.Queue()

        # Stats
        self.total_transcriptions = 0
        self.last_transcription_time = 0

        # Load Vosk model
        self._load_model()

        logger.info("✓ Continuous Listener initialized")

    def _load_model(self):
        """Load the Vosk speech recognition model."""
        logger.info(f"Loading Vosk model from {config.VOSK_MODEL_PATH}...")

        if not os.path.exists(config.VOSK_MODEL_PATH):
            raise FileNotFoundError(
                f"Vosk model not found at {config.VOSK_MODEL_PATH}\n"
                "Download it from: https://alphacephei.com/vosk/models"
            )

        # Load model
        self.model = Model(config.VOSK_MODEL_PATH)

        # Create recognizer
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)  # Get word-level timestamps

        logger.info("✓ Vosk model loaded")

    def _setup_audio(self):
        """Initialize PyAudio and audio stream."""
        logger.info("Setting up audio input...")

        self.audio = pyaudio.PyAudio()

        # Find the right input device (or use default)
        device_index = config.MIC_DEVICE_INDEX

        if device_index is None:
            # Use default input device
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
                stream_callback=None  # Use blocking mode
            )
            logger.info("✓ Audio stream opened")
        except Exception as e:
            logger.error(f"Failed to open audio stream: {e}")
            raise

    def _process_audio(self):
        """Main audio processing loop (runs in separate thread)."""
        logger.info("Audio processing thread started")

        try:
            self._setup_audio()

            while self.running:
                # Read audio chunk
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                except Exception as e:
                    logger.error(f"Error reading audio: {e}")
                    time.sleep(0.1)
                    continue

                # Feed to recognizer
                if self.recognizer.AcceptWaveform(data):
                    # Full result available
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()

                    if text:
                        self.total_transcriptions += 1
                        self.last_transcription_time = time.time()

                        logger.info(f"Transcribed: '{text}'")

                        # Add to queue
                        self.text_queue.put(text)

                        # Call callback if provided
                        if self.callback:
                            try:
                                self.callback(text)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                else:
                    # Partial result (optional for real-time feedback)
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '')

                    if partial_text and config.PRINT_TRANSCRIPTIONS:
                        # Only print if there's actual content
                        if len(partial_text) > 3:  # Avoid noise
                            logger.debug(f"Partial: '{partial_text}'")

        except Exception as e:
            logger.error(f"Audio processing error: {e}")
        finally:
            self._cleanup_audio()

        logger.info("Audio processing thread stopped")

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
        """Start continuous listening in a background thread."""
        if self.running:
            logger.warning("Listener already running")
            return

        logger.info("Starting continuous listener...")
        self.running = True
        self.thread = threading.Thread(target=self._process_audio, daemon=True)
        self.thread.start()
        logger.info("✓ Listener started")

    def stop(self):
        """Stop the listener."""
        if not self.running:
            return

        logger.info("Stopping continuous listener...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        logger.info("✓ Listener stopped")

    def get_text(self, timeout=None):
        """
        Get the next transcribed text from the queue.

        Args:
            timeout: Max time to wait in seconds (None = wait forever)

        Returns:
            str: Transcribed text, or None if timeout
        """
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
            'total_transcriptions': self.total_transcriptions,
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
    print("Continuous Listener Test")
    print("=" * 60)
    print("Speak into your microphone. Press Ctrl+C to stop.")
    print("=" * 60)

    # Callback for real-time display
    def on_transcription(text):
        print(f"\n>>> YOU SAID: '{text}'\n")

    # Create listener
    listener = ContinuousListener(callback=on_transcription)

    try:
        # Start listening
        listener.start()

        # Keep running
        while True:
            time.sleep(0.5)

            # Display stats every 10 seconds
            if int(time.time()) % 10 == 0:
                stats = listener.get_stats()
                print(f"\nStats: {stats['total_transcriptions']} transcriptions, "
                      f"Queue: {stats['queue_size']}")

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        listener.stop()
        print("✓ Test complete")
