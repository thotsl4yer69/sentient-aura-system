#!/usr/bin/env python3
"""
Sentient Aura Supervisor
Monitors the main Sentient Aura process and automatically restarts it if it crashes.

Mechanism:
- Launches sentient_aura_main.py as a subprocess
- Monitors /tmp/aura.heartbeat file
- If heartbeat hasn't updated in 10 seconds, assumes crash and restarts
- Logs all restart events
- Graceful shutdown on Ctrl+C
"""

import subprocess
import time
import os
import signal
import sys
import logging
from datetime import datetime

# Configuration
HEARTBEAT_FILE = "/tmp/aura.heartbeat"
HEARTBEAT_TIMEOUT = 10.0  # seconds - restart if no update
CHECK_INTERVAL = 2.0      # seconds - how often to check
MAIN_SCRIPT = os.path.join(os.path.dirname(__file__), "sentient_aura_main.py")
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs/supervisor.log")

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("supervisor")


class SentientAuraSupervisor:
    """
    Process supervisor with heartbeat monitoring.

    Ensures Sentient Aura is always running by monitoring heartbeat
    and restarting if process crashes or hangs.
    """

    def __init__(self):
        self.process = None
        self.running = False
        self.restart_count = 0
        self.start_time = time.time()

    def read_heartbeat(self):
        """
        Read the last heartbeat timestamp.

        Returns:
            float: Timestamp from heartbeat file, or None if can't read
        """
        try:
            if os.path.exists(HEARTBEAT_FILE):
                with open(HEARTBEAT_FILE, 'r') as f:
                    timestamp = float(f.read().strip())
                    return timestamp
            return None
        except Exception as e:
            logger.debug(f"Error reading heartbeat: {e}")
            return None

    def is_process_alive(self):
        """
        Check if the main process is alive and healthy.

        Returns:
            bool: True if process is running and heartbeat is fresh
        """
        # Check if subprocess is still running
        if self.process is None or self.process.poll() is not None:
            return False

        # Check heartbeat freshness
        last_heartbeat = self.read_heartbeat()
        if last_heartbeat is None:
            # No heartbeat file yet - give it time during startup
            # If process started less than 15 seconds ago, consider it alive
            if time.time() - self.start_time < 15.0:
                return True
            else:
                logger.warning("No heartbeat file found after 15 seconds")
                return False

        # Check if heartbeat is fresh
        age = time.time() - last_heartbeat
        if age > HEARTBEAT_TIMEOUT:
            logger.warning(f"Heartbeat is stale! Age: {age:.1f}s (timeout: {HEARTBEAT_TIMEOUT}s)")
            return False

        return True

    def start_process(self):
        """Start the main Sentient Aura process."""
        logger.info("=" * 70)
        logger.info(f"Starting Sentient Aura (restart #{self.restart_count})")
        logger.info("=" * 70)

        try:
            # Remove old heartbeat file
            if os.path.exists(HEARTBEAT_FILE):
                os.remove(HEARTBEAT_FILE)
                logger.info("Removed stale heartbeat file")

            # Start the main process
            self.process = subprocess.Popen(
                [sys.executable, MAIN_SCRIPT, "--no-voice-input", "--headless"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )

            self.start_time = time.time()
            self.restart_count += 1

            logger.info(f"✓ Process started (PID: {self.process.pid})")
            logger.info(f"  Command: {sys.executable} {MAIN_SCRIPT}")
            logger.info(f"  Heartbeat file: {HEARTBEAT_FILE}")
            logger.info(f"  Monitoring interval: {CHECK_INTERVAL}s")
            logger.info(f"  Heartbeat timeout: {HEARTBEAT_TIMEOUT}s")

            return True

        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            return False

    def stop_process(self):
        """Stop the main process gracefully."""
        if self.process is None:
            return

        logger.info(f"Stopping process (PID: {self.process.pid})...")

        try:
            # Try graceful shutdown first (SIGINT = Ctrl+C)
            self.process.send_signal(signal.SIGINT)

            # Wait up to 10 seconds for graceful shutdown
            try:
                self.process.wait(timeout=10)
                logger.info("✓ Process stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop
                logger.warning("Process did not stop gracefully, forcing kill...")
                self.process.kill()
                self.process.wait()
                logger.info("✓ Process killed")

        except Exception as e:
            logger.error(f"Error stopping process: {e}")

        self.process = None

    def restart_process(self):
        """Restart the main process."""
        logger.warning("=" * 70)
        logger.warning("PROCESS RESTART REQUIRED")
        logger.warning("=" * 70)

        # Stop current process
        self.stop_process()

        # Wait a moment before restarting
        time.sleep(2)

        # Start new process
        return self.start_process()

    def run(self):
        """Main supervisor loop."""
        logger.info("=" * 70)
        logger.info("SENTIENT AURA SUPERVISOR")
        logger.info("=" * 70)
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)

        self.running = True

        # Start initial process
        if not self.start_process():
            logger.error("Failed to start initial process!")
            return 1

        # Monitoring loop
        try:
            while self.running:
                # Check if process is alive and healthy
                if not self.is_process_alive():
                    logger.error("Process is not healthy!")

                    # Check if process exited
                    if self.process.poll() is not None:
                        returncode = self.process.returncode
                        logger.error(f"Process exited with code: {returncode}")

                        # Read any final output
                        try:
                            stdout, stderr = self.process.communicate(timeout=1)
                            if stdout:
                                logger.info(f"Final stdout:\n{stdout}")
                            if stderr:
                                logger.error(f"Final stderr:\n{stderr}")
                        except:
                            pass

                    # Restart the process
                    if not self.restart_process():
                        logger.critical("Failed to restart process! Giving up.")
                        return 1

                # Sleep before next check
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user...")

        finally:
            # Clean shutdown
            logger.info("Supervisor shutting down...")
            self.stop_process()

            # Remove heartbeat file
            if os.path.exists(HEARTBEAT_FILE):
                try:
                    os.remove(HEARTBEAT_FILE)
                    logger.info("Heartbeat file removed")
                except:
                    pass

            logger.info("=" * 70)
            logger.info("SUPERVISOR SHUTDOWN COMPLETE")
            logger.info(f"Total restarts: {self.restart_count - 1}")
            logger.info(f"Total uptime: {time.time() - self.start_time:.1f}s")
            logger.info("=" * 70)

        return 0


def main():
    """Main entry point."""
    supervisor = SentientAuraSupervisor()

    # Handle signals
    def signal_handler(sig, frame):
        logger.info(f"\nReceived signal {sig}")
        supervisor.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run supervisor
    return supervisor.run()


if __name__ == "__main__":
    sys.exit(main())
