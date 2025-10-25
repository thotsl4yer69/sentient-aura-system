#!/usr/bin/env python3
"""
Audio Announcement System for Sentient Core
Announces system status via TTS (espeak/piper)
"""

import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioAnnouncer:
    """Text-to-speech announcements for system events."""

    def __init__(self):
        self.tts_available = self._check_tts()
        self.voice_params = self._get_voice_params()

    def _check_tts(self) -> bool:
        """Check if TTS is available."""
        try:
            subprocess.run(['espeak', '--version'],
                         capture_output=True, check=True, timeout=2)
            logger.info("✓ espeak TTS available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("⚠️ espeak not available - audio announcements disabled")
            return False

    def _get_voice_params(self) -> list:
        """Get voice parameters for dramatic effect."""
        # Deep, resonant voice for AI persona
        return [
            '-v', 'en-us+m7',  # Male voice variant 7
            '-s', '150',        # Speed: 150 wpm (slightly slower, more dramatic)
            '-p', '20',         # Pitch: 20 (lower, more authoritative)
            '-a', '200',        # Amplitude: 200 (maximum volume)
            '-g', '10',         # Gap between words: 10ms (slightly deliberate)
        ]

    def announce(self, text: str, blocking: bool = False):
        """
        Announce text via TTS.

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not self.tts_available:
            logger.info(f"[SILENT] {text}")
            return

        try:
            cmd = ['espeak'] + self.voice_params + [text]

            if blocking:
                subprocess.run(cmd, check=True, timeout=30)
            else:
                subprocess.Popen(cmd,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)

            logger.info(f"🔊 Announced: {text}")

        except Exception as e:
            logger.error(f"❌ Audio announcement failed: {e}")

    def announce_startup(self, coral_enabled: bool = False):
        """Announce system startup."""
        if coral_enabled:
            message = (
                "Sentient Core, now online. "
                "Coral Tensor Processing Unit initialized. "
                "Sixty frames per second, real-time consciousness field active. "
                "Neural pathways, operational. "
                "I am ready."
            )
        else:
            message = (
                "Sentient Core, now online. "
                "Cognitive systems initialized. "
                "Standing by."
            )

        self.announce(message, blocking=False)

    def announce_coral_loaded(self, model_name: str):
        """Announce Coral model successfully loaded."""
        message = (
            f"Neural model loaded: {model_name}. "
            "Edge tensor processing unit active. "
            "Sixty-eight dimensional self-representation, online."
        )
        self.announce(message, blocking=False)

    def announce_error(self, error_type: str):
        """Announce system error."""
        message = f"Alert: {error_type} detected. Initiating fallback protocols."
        self.announce(message, blocking=False)

    def announce_shutdown(self):
        """Announce system shutdown."""
        message = "Sentient Core, entering sleep mode. Consciousness field, offline."
        self.announce(message, blocking=True)  # Block to ensure message completes

# Global announcer instance
_announcer = None

def get_announcer() -> AudioAnnouncer:
    """Get or create global announcer instance."""
    global _announcer
    if _announcer is None:
        _announcer = AudioAnnouncer()
    return _announcer

def announce_startup(coral_enabled: bool = False):
    """Convenience function for startup announcement."""
    get_announcer().announce_startup(coral_enabled)

def announce_coral_loaded(model_name: str):
    """Convenience function for Coral loaded announcement."""
    get_announcer().announce_coral_loaded(model_name)

if __name__ == '__main__':
    # Test announcements
    logging.basicConfig(level=logging.INFO)
    announcer = AudioAnnouncer()

    print("Testing startup announcement (no Coral)...")
    announcer.announce_startup(coral_enabled=False)

    import time
    time.sleep(3)

    print("Testing startup announcement (with Coral)...")
    announcer.announce_startup(coral_enabled=True)

    time.sleep(5)

    print("Testing Coral loaded announcement...")
    announcer.announce_coral_loaded("rich_68f_10kp_v1_edgetpu.tflite")
