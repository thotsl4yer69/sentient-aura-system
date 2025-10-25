#!/usr/bin/env python3
"""
Audio Daemon - Audio Input Level Monitoring

Monitors audio input levels without recording actual audio.
Provides amplitude and frequency features for visualization.
"""

import logging
import time
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daemon_base import BaseDaemon
from world_state import WorldState

logger = logging.getLogger("Audio")


class AudioDaemon(BaseDaemon):
    """
    Audio Input Monitoring Daemon.

    Features:
    - Audio level (amplitude) monitoring
    - Frequency band analysis (low, mid, high)
    - Speech/music detection
    - NO audio recording (privacy-preserving)
    """

    def __init__(self, world_state: WorldState, update_rate: float = 20.0):
        """
        Initialize audio daemon.

        Args:
            world_state: Central world state
            update_rate: Update frequency in Hz
        """
        super().__init__("audio", world_state, update_rate)

        self.audio_available = False
        self.sample_count = 0
        self.pyaudio_instance = None
        self.stream = None

        # Audio parameters
        self.sample_rate = 44100
        self.chunk_size = 2048  # ~46ms at 44.1kHz
        self.channels = 1

    def initialize(self) -> bool:
        """Initialize audio input."""
        self.logger.info("Initializing Audio Daemon...")

        try:
            # Try to import pyaudio
            import pyaudio

            self.pyaudio_instance = pyaudio.PyAudio()

            # Find default input device
            default_input = self.pyaudio_instance.get_default_input_device_info()
            self.logger.info(f"Default audio input: {default_input['name']}")

            # Open audio stream (input only, no recording)
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=None  # Blocking mode
            )

            self.audio_available = True
            self.logger.info("✓ Audio Daemon initialized (level monitoring only)")
            return True

        except ImportError as e:
            self.logger.warning(f"PyAudio library not available: {e}")
            self.logger.info("Install with: pip3 install pyaudio")
            self.audio_available = False
            return False
        except Exception as e:
            self.logger.error(f"Audio initialization failed: {e}")
            self.audio_available = False
            return False

    def update(self) -> None:
        """Read audio levels and update world state."""

        if not self.audio_available or self.stream is None:
            # No audio input - return empty data
            self.world_state.update("audio", {
                "available": False,
                "status": "no_input"
            })
            return

        try:
            # Read audio chunk (non-blocking)
            audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)

            # Convert to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

            # Normalize to [-1, 1]
            audio_np /= 32768.0

            # Calculate amplitude (RMS)
            rms = np.sqrt(np.mean(audio_np**2))
            amplitude = float(rms)

            # Calculate peak amplitude
            peak = float(np.max(np.abs(audio_np)))

            # FFT for frequency analysis
            fft = np.fft.rfft(audio_np)
            fft_magnitude = np.abs(fft)

            # Frequency bands
            freqs = np.fft.rfftfreq(len(audio_np), 1.0 / self.sample_rate)

            # Low (20-250 Hz), Mid (250-2000 Hz), High (2000-20000 Hz)
            low_band = np.mean(fft_magnitude[(freqs >= 20) & (freqs < 250)])
            mid_band = np.mean(fft_magnitude[(freqs >= 250) & (freqs < 2000)])
            high_band = np.mean(fft_magnitude[(freqs >= 2000) & (freqs < 20000)])

            # Normalize frequency bands
            total_energy = low_band + mid_band + high_band
            if total_energy > 0:
                low_norm = float(low_band / total_energy)
                mid_norm = float(mid_band / total_energy)
                high_norm = float(high_band / total_energy)
            else:
                low_norm = mid_norm = high_norm = 0.0

            # Dominant frequency
            dominant_freq_idx = np.argmax(fft_magnitude)
            dominant_freq = float(freqs[dominant_freq_idx])

            # Speech detection (heuristic: strong mid-band energy)
            speech_detected = mid_norm > 0.5 and amplitude > 0.01

            # Music detection (heuristic: balanced frequency distribution)
            music_detected = amplitude > 0.02 and low_norm > 0.2 and high_norm > 0.2

            # Extract normalized features for Coral TPU
            features = self._extract_features(
                amplitude=amplitude,
                peak=peak,
                low=low_norm,
                mid=mid_norm,
                high=high_norm,
                dominant_freq=dominant_freq
            )

            # Update world state
            self.world_state.update("audio", {
                "available": True,
                "status": "active",
                "timestamp": time.time(),
                "sample_count": self.sample_count,

                # Amplitude (0.0-1.0)
                "amplitude": amplitude,
                "peak": peak,

                # Frequency bands (normalized 0.0-1.0)
                "frequency_bands": {
                    "low": low_norm,    # Bass
                    "mid": mid_norm,    # Midrange (speech)
                    "high": high_norm   # Treble
                },

                # Dominant frequency
                "dominant_frequency": dominant_freq,

                # Detection
                "speech_detected": speech_detected,
                "music_detected": music_detected,
                "silence": amplitude < 0.001,

                # Normalized features for Coral TPU
                "features": features
            })

            self.sample_count += 1

        except Exception as e:
            self.logger.error(f"Audio read error: {e}", exc_info=True)
            self.world_state.update("audio", {
                "available": False,
                "status": "error",
                "error": str(e)
            })

    def _extract_features(self, amplitude, peak, low, mid, high, dominant_freq) -> Dict:
        """
        Extract normalized audio features for Coral TPU model.

        Args:
            amplitude: RMS amplitude (0.0-1.0)
            peak: Peak amplitude (0.0-1.0)
            low, mid, high: Frequency band energy (0.0-1.0)
            dominant_freq: Dominant frequency in Hz

        Returns:
            Dictionary of normalized features (0.0-1.0)
        """
        # Amplitude features (already normalized)
        amplitude_norm = min(1.0, amplitude * 10)  # Scale up quiet sounds
        peak_norm = min(1.0, peak)

        # Frequency band features (already normalized)
        low_norm = low
        mid_norm = mid
        high_norm = high

        # Dominant frequency (normalize to 0-1 for typical range 20-10000 Hz)
        dominant_freq_norm = min(1.0, max(0.0, (dominant_freq - 20) / 9980))

        return {
            "amplitude": amplitude_norm,
            "peak": peak_norm,
            "frequency_low": low_norm,
            "frequency_mid": mid_norm,
            "frequency_high": high_norm,
            "dominant_frequency": dominant_freq_norm,
            "speech_detected": float(mid_norm > 0.5 and amplitude > 0.01),
            "music_detected": float(amplitude > 0.02 and low_norm > 0.2 and high_norm > 0.2),
            "silence": float(amplitude < 0.001)
        }

    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.logger.info("Shutting down Audio Daemon...")

        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
        except:
            pass

        self.logger.info(f"  Total samples: {self.sample_count}")


if __name__ == "__main__":
    # Test audio daemon
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("AUDIO DAEMON TEST")
    print("=" * 70)

    # Create world state
    ws = WorldState()

    # Create audio daemon
    audio = AudioDaemon(ws, update_rate=20.0)

    if not audio.initialize():
        print("✗ Audio input not available")
        sys.exit(1)

    print("\n✓ Audio daemon initialized")
    print("✓ Monitoring audio levels at 20 Hz...")
    print("Press Ctrl+C to quit\n")

    # Run audio loop
    try:
        audio.start()

        while True:
            time.sleep(1)

            # Show current audio status
            status = ws.get("audio")
            if status and status.get("available"):
                amp = status.get("amplitude", 0)
                peak = status.get("peak", 0)
                bands = status.get("frequency_bands", {})
                dominant = status.get("dominant_frequency", 0)

                # Visual amplitude meter
                bar_length = int(amp * 50)
                bar = "█" * bar_length + "░" * (50 - bar_length)

                print(f"\n🎤 Audio Level: [{bar}] {amp:.3f}")
                print(f"   Peak: {peak:.3f}  Dominant: {dominant:.0f} Hz")
                print(f"   Bands - Low: {bands.get('low', 0):.2f}  Mid: {bands.get('mid', 0):.2f}  High: {bands.get('high', 0):.2f}")

                if status.get('speech_detected'):
                    print("   🗣️  Speech detected")
                elif status.get('music_detected'):
                    print("   🎵 Music detected")
                elif status.get('silence'):
                    print("   🔇 Silence")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        audio.stop()
        audio.join(timeout=3)

    print("\n✓ Audio test complete\n")
