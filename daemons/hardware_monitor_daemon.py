#!/usr/bin/env python3
"""
Hardware Monitor Daemon - Real-time Hardware Detection

Continuously monitors hardware connections and automatically:
- Starts daemons when hardware is plugged in
- Stops daemons when hardware is disconnected
- Updates WorldState with real-time hardware availability
- Ensures NO SIMULATED DATA - only real sensor readings

This is the foundation of true adaptive AI - the system responds
to the physical world in real-time.
"""

import logging
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daemon_base import BaseDaemon
from world_state import WorldState
from hardware_discovery import HardwareDiscovery, HardwareCapability

logger = logging.getLogger("HardwareMonitor")


class HardwareMonitorDaemon(BaseDaemon):
    """
    Monitors hardware in real-time and manages daemon lifecycle.

    Features:
    - Hot-plug detection for USB, I2C, serial devices
    - Automatic daemon start/stop based on hardware availability
    - No simulated data - only reports actual hardware state
    - Graceful degradation when hardware is disconnected
    """

    def __init__(
        self,
        world_state: WorldState,
        daemon_manager=None,
        update_rate: float = 5.0  # Check every 5 seconds
    ):
        """
        Initialize hardware monitor.

        Args:
            world_state: Central world state
            daemon_manager: AdaptiveDaemonManager instance (optional)
            update_rate: Hardware check frequency in seconds
        """
        super().__init__("hardware_monitor", world_state, update_rate)

        self.daemon_manager = daemon_manager
        self.discovery = HardwareDiscovery()

        # Track hardware state
        self.previous_capabilities: Dict[str, HardwareCapability] = {}
        self.current_capabilities: Dict[str, HardwareCapability] = {}

        # Track which daemons we've started
        self.managed_daemons: Dict[str, object] = {}  # hw_name -> daemon instance

        # Hardware change callbacks
        self.on_connect_callbacks: Dict[str, callable] = {}
        self.on_disconnect_callbacks: Dict[str, callable] = {}

    def initialize(self) -> bool:
        """Initialize hardware monitor."""
        self.logger.info("=" * 70)
        self.logger.info("HARDWARE MONITOR DAEMON - Initializing")
        self.logger.info("=" * 70)

        try:
            # Initial hardware scan
            self.current_capabilities = self.discovery.discover_all()
            self.previous_capabilities = self.current_capabilities.copy()

            # Update world state with initial hardware status
            self._update_hardware_status()

            self.logger.info("✓ Hardware Monitor initialized")
            self.logger.info(f"  Monitoring {len(self.current_capabilities)} hardware capabilities")
            self.logger.info(f"  Update rate: {self.update_rate}s")

            return True

        except Exception as e:
            self.logger.error(f"Hardware monitor initialization failed: {e}", exc_info=True)
            return False

    def update(self) -> None:
        """
        Main update loop - check for hardware changes.

        Runs every update_rate seconds to detect:
        - New hardware connected
        - Hardware disconnected
        - Hardware state changes
        """
        try:
            # Re-scan all hardware
            self.current_capabilities = self.discovery.discover_all()

            # Detect changes
            self._detect_hardware_changes()

            # Update world state
            self._update_hardware_status()

            # Store current state for next comparison
            self.previous_capabilities = self.current_capabilities.copy()

        except Exception as e:
            self.logger.error(f"Hardware monitor update error: {e}", exc_info=True)

    def _detect_hardware_changes(self) -> None:
        """Detect hardware connection/disconnection events."""

        for hw_name, capability in self.current_capabilities.items():
            previous = self.previous_capabilities.get(hw_name)

            # Hardware CONNECTED (newly available)
            if capability.available and (not previous or not previous.available):
                self._handle_hardware_connected(hw_name, capability)

            # Hardware DISCONNECTED (no longer available)
            elif not capability.available and previous and previous.available:
                self._handle_hardware_disconnected(hw_name, capability)

            # Hardware state CHANGED (still connected but properties changed)
            elif capability.available and previous and previous.available:
                if capability.metadata != previous.metadata:
                    self._handle_hardware_changed(hw_name, capability, previous)

    def _handle_hardware_connected(self, hw_name: str, capability: HardwareCapability) -> None:
        """
        Handle hardware connection event.

        Args:
            hw_name: Hardware identifier
            capability: Hardware capability details
        """
        self.logger.info("=" * 70)
        self.logger.info(f"🔌 HARDWARE CONNECTED: {capability.name}")
        self.logger.info("=" * 70)
        self.logger.info(f"  Category: {capability.category}")
        self.logger.info(f"  Interface: {capability.interface}")
        if capability.address:
            self.logger.info(f"  Address: {capability.address}")
        self.logger.info(f"  Confidence: {capability.confidence*100:.0f}%")

        # Update world state immediately
        self.world_state.update(f"hardware.{hw_name}", {
            "available": True,
            "status": "connected",
            "connected_at": time.time(),
            "name": capability.name,
            "category": capability.category,
            "interface": capability.interface,
            "metadata": capability.metadata
        })

        # Call custom connection callback if registered
        if hw_name in self.on_connect_callbacks:
            try:
                self.on_connect_callbacks[hw_name](capability)
            except Exception as e:
                self.logger.error(f"Connection callback error for {hw_name}: {e}")

        # TODO: Auto-start appropriate daemon
        # This would require daemon_manager integration
        # For now, just log the event
        self.logger.info(f"  Note: Auto-start daemon for {hw_name} not yet implemented")

    def _handle_hardware_disconnected(self, hw_name: str, capability: HardwareCapability) -> None:
        """
        Handle hardware disconnection event.

        Args:
            hw_name: Hardware identifier
            capability: Hardware capability details (previous state)
        """
        self.logger.warning("=" * 70)
        self.logger.warning(f"⚠️  HARDWARE DISCONNECTED: {capability.name}")
        self.logger.warning("=" * 70)
        self.logger.warning(f"  Category: {capability.category}")
        self.logger.warning(f"  Interface: {capability.interface}")

        # Update world state immediately
        self.world_state.update(f"hardware.{hw_name}", {
            "available": False,
            "status": "disconnected",
            "disconnected_at": time.time(),
            "name": capability.name,
            "category": capability.category
        })

        # Call custom disconnection callback if registered
        if hw_name in self.on_disconnect_callbacks:
            try:
                self.on_disconnect_callbacks[hw_name](capability)
            except Exception as e:
                self.logger.error(f"Disconnection callback error for {hw_name}: {e}")

        # TODO: Auto-stop appropriate daemon
        # For now, just log the event
        self.logger.warning(f"  Note: Auto-stop daemon for {hw_name} not yet implemented")

    def _handle_hardware_changed(
        self,
        hw_name: str,
        new_capability: HardwareCapability,
        old_capability: HardwareCapability
    ) -> None:
        """
        Handle hardware state change (still connected but properties changed).

        Args:
            hw_name: Hardware identifier
            new_capability: New hardware state
            old_capability: Previous hardware state
        """
        self.logger.debug(f"Hardware state changed: {new_capability.name}")

        # Update world state with new metadata
        self.world_state.update(f"hardware.{hw_name}.metadata", new_capability.metadata)

    def _update_hardware_status(self) -> None:
        """Update world state with current hardware availability summary."""

        # Count available hardware by category
        categories = {}
        for hw_name, capability in self.current_capabilities.items():
            if capability.available:
                category = capability.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(capability.name)

        # Update world state with summary
        self.world_state.update("hardware_monitor", {
            "status": "active",
            "last_scan": time.time(),
            "total_capabilities": len(self.current_capabilities),
            "available_capabilities": sum(1 for c in self.current_capabilities.values() if c.available),
            "categories": categories
        })

    def register_connect_callback(self, hw_name: str, callback: callable) -> None:
        """
        Register a callback to be called when hardware connects.

        Args:
            hw_name: Hardware identifier to watch
            callback: Function to call with (capability) argument
        """
        self.on_connect_callbacks[hw_name] = callback
        self.logger.info(f"Registered connection callback for: {hw_name}")

    def register_disconnect_callback(self, hw_name: str, callback: callable) -> None:
        """
        Register a callback to be called when hardware disconnects.

        Args:
            hw_name: Hardware identifier to watch
            callback: Function to call with (capability) argument
        """
        self.on_disconnect_callbacks[hw_name] = callback
        self.logger.info(f"Registered disconnection callback for: {hw_name}")

    def is_hardware_available(self, hw_name: str) -> bool:
        """
        Check if specific hardware is currently available.

        Args:
            hw_name: Hardware identifier

        Returns:
            True if hardware is available
        """
        capability = self.current_capabilities.get(hw_name)
        return capability.available if capability else False

    def get_hardware_info(self, hw_name: str) -> Optional[Dict]:
        """
        Get detailed information about specific hardware.

        Args:
            hw_name: Hardware identifier

        Returns:
            Dictionary with hardware details or None if not found
        """
        capability = self.current_capabilities.get(hw_name)
        if not capability:
            return None

        return {
            "name": capability.name,
            "category": capability.category,
            "available": capability.available,
            "confidence": capability.confidence,
            "interface": capability.interface,
            "address": capability.address,
            "metadata": capability.metadata
        }

    def cleanup(self) -> None:
        """Clean up hardware monitor resources."""
        self.logger.info("Shutting down Hardware Monitor Daemon...")

        # Clear callbacks
        self.on_connect_callbacks.clear()
        self.on_disconnect_callbacks.clear()

        self.logger.info("✓ Hardware Monitor shutdown complete")


if __name__ == "__main__":
    # Test hardware monitor
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("HARDWARE MONITOR DAEMON TEST")
    print("=" * 70)

    # Create world state
    ws = WorldState()

    # Create hardware monitor
    monitor = HardwareMonitorDaemon(ws, update_rate=3.0)

    if not monitor.initialize():
        print("✗ Initialization failed")
        sys.exit(1)

    print("\n✓ Hardware Monitor initialized")
    print("✓ Monitoring for hardware changes...")
    print("\nTry plugging/unplugging USB devices!")
    print("Press Ctrl+C to quit\n")

    # Run monitoring loop
    try:
        monitor.start()

        while True:
            time.sleep(1)

            # Show current hardware status
            status = ws.get("hardware_monitor")
            if status:
                available = status.get("available_capabilities", 0)
                total = status.get("total_capabilities", 0)
                print(f"\rHardware: {available}/{total} available", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        monitor.stop()
        monitor.join(timeout=3)

    print("\n✓ Hardware Monitor test complete\n")
