#!/usr/bin/env python3
"""
Voice Output using Piper TTS
High-quality neural text-to-speech for Sentient Aura
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import subprocess
import tempfile
import logging
import threading
import queue
import time
import wave

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio not available, using system audio player")

from . import config

logger = logging.getLogger("voice_piper")


class VoicePiper:
    """Text-to-speech using Piper neural TTS."""

    def __init__(self):
        """Initialize the Piper TTS engine."""
        logger.info("Initializing Piper TTS...")

        # Find piper executable
        self.piper_path = self._find_piper()

        # Voice model path
        self.model_path = self._find_voice_model()

        # Audio playback
        self.audio = None
        self.speaking = False

        # Speech queue (for async speaking)
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.running = False

        # Stats
        self.total_speeches = 0

        logger.info("✓ Piper TTS initialized")

    def _find_piper(self):
        """Find the piper executable."""
        # Check common locations
        locations = [
            '/home/mz1312/.local/bin/piper',
            '/usr/local/bin/piper',
            '/usr/bin/piper',
        ]

        for path in locations:
            if os.path.exists(path):
                logger.info(f"Found piper at: {path}")
                return path

        # Try using 'which'
        try:
            result = subprocess.run(['which', 'piper'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                logger.info(f"Found piper at: {path}")
                return path
        except:
            pass

        raise FileNotFoundError(
            "Piper executable not found. Install with: pip3 install piper-tts"
        )

    def _find_voice_model(self):
        """Find the voice model file."""
        model_name = config.PIPER_MODEL
        voice_dir = config.PIPER_VOICE_PATH

        # Full model path
        model_path = os.path.join(voice_dir, f"{model_name}.onnx")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Piper voice model not found at: {model_path}\n"
                f"Download from: https://github.com/rhasspy/piper/releases"
            )

        logger.info(f"Using voice model: {model_path}")
        return model_path

    def synthesize(self, text):
        """
        Synthesize speech from text and return audio data.

        Args:
            text: Text to synthesize

        Returns:
            bytes: WAV audio data
        """
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            # Build piper command
            cmd = [
                self.piper_path,
                '--model', self.model_path,
                '--output_file', output_path
            ]

            # Run piper
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send text to piper
            stdout, stderr = process.communicate(input=text, timeout=config.TTS_TIMEOUT)

            if process.returncode != 0:
                logger.error(f"Piper synthesis failed: {stderr}")
                return None

            # Read WAV file
            with open(output_path, 'rb') as f:
                audio_data = f.read()

            return audio_data

        except subprocess.TimeoutExpired:
            logger.error("Piper synthesis timed out")
            process.kill()
            return None
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(output_path)
            except:
                pass

    def speak(self, text, blocking=True):
        """
        Speak the given text.

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not text:
            return

        logger.info(f"Speaking: '{text}'")

        if blocking:
            # Synthesize and play immediately
            self._speak_now(text)
        else:
            # Add to queue for async playback
            self.speech_queue.put(text)

    def _speak_now(self, text):
        """Synthesize and play speech immediately (blocking)."""
        self.speaking = True
        self.total_speeches += 1

        try:
            # Synthesize audio
            audio_data = self.synthesize(text)

            if audio_data:
                # Play audio
                self._play_audio(audio_data)

        except Exception as e:
            logger.error(f"Speech error: {e}")
        finally:
            self.speaking = False

    def _play_audio(self, audio_data):
        """Play WAV audio data."""
        if PYAUDIO_AVAILABLE:
            self._play_audio_pyaudio(audio_data)
        else:
            self._play_audio_system(audio_data)

    def _play_audio_pyaudio(self, audio_data):
        """Play audio using PyAudio."""
        # Write to temp file (PyAudio needs a file)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            wav_path = tmp_file.name

        try:
            # Open WAV file
            wf = wave.open(wav_path, 'rb')

            # Initialize PyAudio if needed
            if self.audio is None:
                self.audio = pyaudio.PyAudio()

            # Open stream
            stream = self.audio.open(
                format=self.audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )

            # Play audio in chunks
            chunk_size = 1024
            data = wf.readframes(chunk_size)

            while data and self.speaking:
                stream.write(data)
                data = wf.readframes(chunk_size)

            # Cleanup
            stream.stop_stream()
            stream.close()
            wf.close()

        finally:
            # Remove temp file
            try:
                os.unlink(wav_path)
            except:
                pass

    def _play_audio_system(self, audio_data):
        """Play audio using system audio player (fallback)."""
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            wav_path = tmp_file.name

        try:
            # Try different audio players
            players = [
                ['aplay', wav_path],  # ALSA
                ['paplay', wav_path],  # PulseAudio
                ['ffplay', '-nodisp', '-autoexit', wav_path],  # FFmpeg
            ]

            for player_cmd in players:
                try:
                    subprocess.run(player_cmd, check=True, capture_output=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            else:
                logger.error("No audio player found")

        finally:
            # Remove temp file
            try:
                os.unlink(wav_path)
            except:
                pass

    def _speech_worker(self):
        """Background thread for async speech playback."""
        logger.info("Speech worker thread started")

        while self.running:
            try:
                # Get next text to speak (with timeout)
                text = self.speech_queue.get(timeout=0.5)

                # Speak it
                self._speak_now(text)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Speech worker error: {e}")

        logger.info("Speech worker thread stopped")

    def start_async(self):
        """Start async speech playback thread."""
        if self.running:
            logger.warning("Async speech already running")
            return

        logger.info("Starting async speech...")
        self.running = True
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    def stop_async(self):
        """Stop async speech playback."""
        if not self.running:
            return

        logger.info("Stopping async speech...")
        self.running = False

        if self.speech_thread:
            self.speech_thread.join(timeout=2)

    def stop_speaking(self):
        """Stop current speech immediately."""
        self.speaking = False

    def is_speaking(self):
        """Check if currently speaking."""
        return self.speaking

    def cleanup(self):
        """Clean up resources."""
        self.stop_async()
        self.stop_speaking()

        if self.audio and PYAUDIO_AVAILABLE:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    print("=" * 60)
    print("Piper TTS Test")
    print("=" * 60)

    # Create voice
    voice = VoicePiper()

    # Test phrases
    test_phrases = [
        "Hello! I am your sentient core.",
        "All systems are online and ready.",
        "Speech recognition is working perfectly.",
        "I can hear you loud and clear!",
        "Let me know if you need anything."
    ]

    print("\nTesting voice output...\n")

    for i, phrase in enumerate(test_phrases, 1):
        print(f"{i}. {phrase}")
        voice.speak(phrase, blocking=True)
        time.sleep(0.5)

    print("\n✓ Test complete")
    voice.cleanup()
