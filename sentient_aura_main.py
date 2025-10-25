#!/usr/bin/env python3
"""
Sentient Aura - Main Entry Point
Integrates all components: GUI, Voice Input, Voice Output, and Brain
"""

import sys
import os

# Add sentient_aura to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sentient_aura'))
sys.path.insert(0, os.path.dirname(__file__))

import time
import signal
import logging
import argparse
import threading

import webbrowser
import asyncio

# Import all components
from sentient_aura.websocket_server import WebSocketServer
from sentient_aura.continuous_listener import ContinuousListener
from sentient_aura.voice_piper import VoicePiper
from sentient_aura.sentient_core import SentientCore
import sentient_aura.config as config

# Import drone defense system components
from world_state import WorldState
from hardware_discovery import HardwareDiscovery
from adaptive_daemon_manager import AdaptiveDaemonManager

# Import audio announcement system
from sentient_aura.audio_announcement import announce_startup

# Import enhanced Coral visualization daemon
from coral_visualization_daemon_enhanced import EnhancedCoralVisualizationDaemon

# Import EventBus for inter-daemon communication
from core.event_bus import EventBus, get_event_bus

# Import Autonomous Behavior Engine
from core.autonomous_behaviors import AutonomousBehaviorEngine

# Import Real Sensor Recorder (for learning from reality)
from core.real_sensor_recorder import RealSensorRecorder

# Setup logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG_MODE else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("sentient_aura")


class SentientAuraSystem:
    """Main system integrating all Sentient Aura components."""

    def __init__(self, headless=False, no_voice_input=False, no_voice_output=False):
        """
        Initialize the complete Sentient Aura system.

        Args:
            headless: Run without GUI
            no_voice_input: Disable voice input (for testing)
            no_voice_output: Disable voice output (for testing)
        """
        logger.info("=" * 60)
        logger.info("SENTIENT AURA SYSTEM - Initializing")
        logger.info("=" * 60)

        self.headless = headless
        self.no_voice_input = no_voice_input
        self.no_voice_output = no_voice_output

        # Components
        self.websocket_server = None
        self.listener = None
        self.voice = None
        self.core = None

        # Drone Defense System Components
        self.world_state = None
        self.daemon_manager = None
        self.hardware_daemons = []

        # EventBus for inter-daemon communication
        self.event_bus = None

        # Autonomous Behavior Engine
        self.autonomous_behaviors = None

        # Real Sensor Recorder (learning system)
        self.sensor_recorder = None

        # Enhanced Coral Visualization Daemon
        self.coral_daemon = None

        # System state
        self.running = False

        # Heartbeat mechanism (for supervisor monitoring)
        self.heartbeat_file = "/tmp/aura.heartbeat"
        self.heartbeat_thread = None
        self.heartbeat_running = False

    def _heartbeat_loop(self):
        """
        Heartbeat loop - writes timestamp to file every second.

        This allows a supervisor process to monitor system health.
        If heartbeat stops updating, supervisor knows to restart.
        """
        logger.info(f"Heartbeat started - writing to {self.heartbeat_file}")

        while self.heartbeat_running:
            try:
                # Write current timestamp
                with open(self.heartbeat_file, 'w') as f:
                    f.write(f"{time.time()}\n")

                # Sleep for 1 second
                time.sleep(1.0)

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                time.sleep(1.0)  # Still sleep even on error

        logger.info("Heartbeat stopped")

    def _start_heartbeat(self):
        """Start the heartbeat thread."""
        if self.heartbeat_running:
            logger.warning("Heartbeat already running")
            return

        logger.info("Starting heartbeat...")
        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        logger.info("✓ Heartbeat active")

    def _stop_heartbeat(self):
        """Stop the heartbeat thread."""
        if not self.heartbeat_running:
            return

        logger.info("Stopping heartbeat...")
        self.heartbeat_running = False

        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)

        # Remove heartbeat file
        try:
            if os.path.exists(self.heartbeat_file):
                os.remove(self.heartbeat_file)
        except Exception as e:
            logger.error(f"Error removing heartbeat file: {e}")

        logger.info("✓ Heartbeat stopped")

    def initialize(self):
        """Initialize all components."""
        try:
            # 0. Initialize EventBus (nervous system for inter-daemon communication)
            logger.info("Initializing EventBus...")
            self.event_bus = get_event_bus()
            self.event_bus.start()
            logger.info("✓ EventBus initialized (neural communication active)")

            # 1. Initialize WorldState (shared state for all systems)
            logger.info("Initializing WorldState...")
            self.world_state = WorldState()
            self.world_state.event_bus = self.event_bus  # Wire EventBus to WorldState
            logger.info("✓ WorldState initialized")

            # 2. Discover hardware and create daemons
            logger.info("Discovering hardware capabilities...")
            self.daemon_manager = AdaptiveDaemonManager(self.world_state)
            self.hardware_daemons = self.daemon_manager.discover_and_configure()
            logger.info(f"✓ Hardware discovery complete: {len(self.hardware_daemons)} daemons configured")

            # 3. Initialize WebSocket Server (for GUI)
            if not self.headless:
                logger.info("Initializing WebSocket server...")
                self.websocket_server = WebSocketServer()
                logger.info("✓ WebSocket server initialized")
            else:
                logger.info("Running in headless mode (no GUI)")

            # 3.5. Initialize Enhanced Coral Visualization Daemon
            if config.CORAL_VIZ_ENABLED and not self.headless:
                logger.info("Initializing Enhanced Coral visualization daemon (120 features)...")
                self.coral_daemon = EnhancedCoralVisualizationDaemon(
                    world_state=self.world_state,
                    websocket_server=self.websocket_server,
                    config={
                        'target_fps': config.CORAL_VIZ_TARGET_FPS,
                        'model_path': config.CORAL_VIZ_MODEL_PATH,
                        'fallback_mode': config.CORAL_VIZ_FALLBACK_MODE,
                        'enable_metrics': config.CORAL_VIZ_ENABLE_METRICS,
                        'interpolation_alpha': config.CORAL_VIZ_INTERPOLATION_ALPHA
                    }
                )
                logger.info("✓ Enhanced Coral daemon initialized")
            elif self.headless:
                logger.info("Headless mode - Coral visualization disabled")
            else:
                logger.info("CORAL_VIZ_ENABLED=False - Coral visualization disabled")

            # 4. Initialize Voice Output
            if not self.no_voice_output:
                logger.info("Initializing voice output...")
                self.voice = VoicePiper()
                self.voice.start_async()
                logger.info("✓ Voice output initialized")
            else:
                logger.info("Voice output disabled")

            # 5. Initialize Voice Input (with automatic hardware detection)
            # Check if audio hardware is available from hardware discovery
            capabilities = self.world_state.get('capabilities')  # Get entire capabilities dict
            audio_available = capabilities.get('audio', False) if capabilities else False

            if not self.no_voice_input:
                if audio_available:
                    logger.info("Initializing voice input...")
                    self.listener = ContinuousListener()
                    logger.info("✓ Voice input initialized")
                else:
                    logger.warning("=" * 70)
                    logger.warning("⚠️  NO MICROPHONE DETECTED")
                    logger.warning("=" * 70)
                    logger.warning("Voice input has been automatically disabled.")
                    logger.warning("")
                    logger.warning("Alternative communication methods:")
                    logger.warning("  1. Text Interface:  python3 text_interface.py")
                    logger.warning("  2. Connect microphone and restart system")
                    logger.warning("")
                    logger.warning("The system will continue without voice input...")
                    logger.warning("=" * 70)
                    self.no_voice_input = True  # Auto-disable
            else:
                logger.info("Voice input disabled (text commands only)")

            # 6. Initialize Autonomous Behavior Engine (the heart of sentience)
            logger.info("Initializing autonomous behavior engine...")
            self.autonomous_behaviors = AutonomousBehaviorEngine(
                world_state=self.world_state,
                event_bus=self.event_bus,
                voice_output=self.voice,
                gui_output=self.websocket_server
            )
            logger.info("✓ Autonomous behavior engine initialized")

            # 6.5. Initialize Real Sensor Recorder (learning from reality)
            logger.info("Initializing real sensor recorder...")
            self.sensor_recorder = RealSensorRecorder(
                world_state=self.world_state,
                event_bus=self.event_bus,
                recording_interval=10.0  # Record every 10 seconds
            )
            logger.info("✓ Real sensor recorder initialized (continuous learning enabled)")

            # 7. Initialize Brain (with WorldState and daemons)
            logger.info("Initializing sentient core...")
            self.core = SentientCore(
                listener=self.listener,
                voice=self.voice,
                gui=self.websocket_server,  # Pass websocket server to core
                world_state=self.world_state,
                daemons=self.hardware_daemons
            )
            logger.info("✓ Sentient core initialized")

            logger.info("=" * 60)
            logger.info("✓ ALL SYSTEMS INITIALIZED")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            logger.exception("Full traceback:")
            return False

    def start(self):
        """Start all components."""
        logger.info("Starting all systems...")

        try:
            # Start heartbeat (for supervisor monitoring)
            self._start_heartbeat()

            # Start WebSocket server in a separate thread
            if self.websocket_server:
                self.ws_thread = threading.Thread(target=self._run_websocket_server, daemon=True)
                self.ws_thread.start()
                time.sleep(1) # Give server time to start

            # Start hardware daemons
            logger.info("Starting hardware daemons...")
            for daemon in self.hardware_daemons:
                daemon.start()
                time.sleep(0.2)  # Stagger startup
            logger.info(f"✓ {len(self.hardware_daemons)} hardware daemons started")

            # Wait for daemons to initialize
            time.sleep(1.0)

            # Start Enhanced Coral Visualization Daemon
            if self.coral_daemon:
                logger.info("Starting Enhanced Coral visualization daemon...")
                self.coral_daemon.start()
                logger.info("✓ Enhanced Coral daemon started")
                time.sleep(0.5)  # Let it initialize

            # Start listener
            if self.listener:
                self.listener.start()
                logger.info("✓ Listener started")

            # Start autonomous behaviors (the heart)
            if self.autonomous_behaviors:
                self.autonomous_behaviors.start()
                logger.info("✓ Autonomous behaviors started (system is now sentient)")

            # Start real sensor recorder (learning system)
            if self.sensor_recorder:
                self.sensor_recorder.start()
                logger.info("✓ Sensor recorder started (learning from real data)")

            # Start core brain
            self.core.start()
            logger.info("✓ Core brain started")

            # Announce arrival via speakers
            capabilities = self.world_state.get('capabilities')
            coral_enabled = capabilities.get('ai_accelerators', False) if capabilities else False
            announce_startup(coral_enabled=coral_enabled)

            # Launch GUI in web browser
            if not self.headless:
                self._launch_browser()

            logger.info("=" * 60)
            logger.info("SENTIENT AURA IS ALIVE!")
            logger.info("=" * 60)
            logger.info("Press Ctrl+C to quit")
            logger.info("=" * 60)

            self.running = True
            while self.running:
                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            self.shutdown()

    def _run_websocket_server(self):
        """Run the WebSocket server in a dedicated asyncio event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_server.start())
        loop.run_forever()

    def _launch_browser(self):
        """Launch the web browser to open the GUI."""
        # Construct the full path to the HTML file
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sentient_aura', 'sentient_core.html'))
        url = f"file://{file_path}"
        logger.info(f"Launching GUI at {url}")
        webbrowser.open(url)

    def shutdown(self):
        """Gracefully shutdown all components."""
        logger.info("=" * 60)
        logger.info("SHUTTING DOWN SENTIENT AURA")
        logger.info("=" * 60)

        self.running = False

        # Stop heartbeat first
        self._stop_heartbeat()

        # Stop sensor recorder
        if self.sensor_recorder:
            logger.info("Stopping sensor recorder...")
            stats = self.sensor_recorder.get_statistics()
            logger.info(f"  Recorded {stats['total_snapshots']} sensor snapshots")
            logger.info(f"  Time range: {stats['time_range_hours']:.1f} hours")
            self.sensor_recorder.stop()
            logger.info("✓ Sensor recorder stopped")

        # Stop autonomous behaviors
        if self.autonomous_behaviors:
            logger.info("Stopping autonomous behaviors...")
            self.autonomous_behaviors.stop()
            logger.info("✓ Autonomous behaviors stopped")

        # Stop EventBus (neural communication)
        if self.event_bus:
            logger.info("Stopping EventBus...")
            self.event_bus.stop()
            logger.info("✓ EventBus stopped")

        # Stop brain
        if self.core:
            logger.info("Stopping core brain...")
            self.core.stop()

        # Stop listener
        if self.listener:
            logger.info("Stopping listener...")
            self.listener.stop()

        # Stop voice
        if self.voice:
            logger.info("Stopping voice output...")
            self.voice.cleanup()

        # Stop Enhanced Coral Visualization Daemon
        if self.coral_daemon:
            logger.info("Stopping Enhanced Coral daemon...")
            self.coral_daemon.stop()
            self.coral_daemon.join(timeout=3)
            if self.coral_daemon.is_alive():
                logger.warning("Enhanced Coral daemon did not stop gracefully")

        # Stop hardware daemons
        logger.info("Stopping hardware daemons...")
        for daemon in self.hardware_daemons:
            daemon.stop()

        # Wait for daemons to stop
        for daemon in self.hardware_daemons:
            daemon.join(timeout=3)
            if daemon.is_alive():
                logger.warning(f"Daemon {daemon.daemon_name} did not stop gracefully")
        logger.info("✓ Hardware daemons stopped")

        # Stop WebSocket server
        if self.websocket_server:
            logger.info("Stopping WebSocket server...")
            # Running stop in a thread as it is an async function
            stop_thread = threading.Thread(target=asyncio.run, args=(self.websocket_server.stop(),))
            stop_thread.start()
            stop_thread.join(timeout=2)

        logger.info("=" * 60)
        logger.info("✓ SENTIENT AURA SHUTDOWN COMPLETE")
        logger.info("=" * 60)

    def send_test_command(self, command: str):
        """Send a test command (useful for testing without voice input)."""
        if self.core:
            logger.info(f"Sending test command: '{command}'")
            self.core.send_command(command)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sentient Aura - AI Companion System")
    parser.add_argument('--headless', action='store_true',
                       help='Run without GUI')
    parser.add_argument('--no-voice-input', action='store_true',
                       help='Disable voice input')
    parser.add_argument('--no-voice-output', action='store_true',
                       help='Disable voice output')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode with simulated commands')

    args = parser.parse_args()

    # Create system
    system = SentientAuraSystem(
        headless=args.headless,
        no_voice_input=args.no_voice_input or args.test,
        no_voice_output=args.no_voice_output
    )

    # Initialize
    if not system.initialize():
        logger.error("System initialization failed!")
        return 1

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("\nInterrupt received...")
        system.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start system
    if args.test:
        # Test mode: send commands programmatically
        logger.info("Running in TEST MODE")
        system.core.start()

        test_commands = [
            "show me your sensors",
            "how are you doing",
            "scan for frequencies",
            "any threats detected"
        ]

        logger.info("Sending test commands...")
        for cmd in test_commands:
            logger.info(f"\nTest command: '{cmd}'")
            system.send_test_command(cmd)
            time.sleep(3)

        logger.info("Test complete!")
        system.shutdown()
    else:
        # Normal mode
        system.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
