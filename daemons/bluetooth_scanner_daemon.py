#!/usr/bin/env python3
"""
Bluetooth Scanner Daemon - Real Bluetooth Device Detection

Uses bluetoothctl to scan for Bluetooth devices and extract real signal data.
NO SIMULATED DATA - returns None if no Bluetooth adapter is available.
"""

import logging
import subprocess
import time
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daemon_base import BaseDaemon
from world_state import WorldState

logger = logging.getLogger("BluetoothScanner")


class BluetoothScannerDaemon(BaseDaemon):
    """
    Scans for Bluetooth devices using bluetoothctl.

    Features:
    - Real device detection (no simulated data)
    - RSSI measurement (signal strength)
    - Device type detection (phone, speaker, headset, etc.)
    - LE (Low Energy) and Classic device support
    """

    def __init__(self, world_state: WorldState, update_rate: float = 15.0):
        """
        Initialize Bluetooth scanner.

        Args:
            world_state: Central world state
            update_rate: Scan frequency in seconds
        """
        super().__init__("bluetooth_scanner", world_state, update_rate)

        self.bluetooth_available = False
        self.scan_count = 0
        self.scan_process = None

    def initialize(self) -> bool:
        """Initialize Bluetooth scanner."""
        self.logger.info("Initializing Bluetooth Scanner Daemon...")

        try:
            # Check if bluetoothctl is available
            result = subprocess.run(
                ['which', 'bluetoothctl'],
                capture_output=True,
                timeout=2
            )

            if result.returncode != 0:
                self.logger.warning("bluetoothctl not found - Bluetooth scanning disabled")
                self.bluetooth_available = False
                return False

            # Check if Bluetooth controller exists (FAST FAIL - no retries)
            try:
                result = subprocess.run(
                    ['bluetoothctl', 'show'],
                    capture_output=True,
                    text=True,
                    timeout=2  # Fast timeout - fail quickly if no adapter
                )
            except subprocess.TimeoutExpired:
                self.logger.warning("Bluetooth controller check timeout - no adapter detected")
                self.bluetooth_available = False
                return False

            if result.returncode != 0 or 'Controller' not in result.stdout:
                self.logger.warning("No Bluetooth controller detected - Bluetooth scanning disabled")
                self.bluetooth_available = False
                return False

            # Power on Bluetooth if needed
            subprocess.run(
                ['bluetoothctl', 'power', 'on'],
                capture_output=True,
                timeout=3
            )

            self.bluetooth_available = True
            self.logger.info("✓ Bluetooth Scanner initialized")
            return True

        except Exception as e:
            self.logger.error(f"Bluetooth scanner initialization failed: {e}")
            self.bluetooth_available = False
            return False

    def update(self) -> None:
        """Scan for Bluetooth devices and update world state."""

        if not self.bluetooth_available:
            # No Bluetooth adapter - return None, NO SIMULATED DATA
            self.world_state.update("bluetooth_scanner", {
                "available": False,
                "status": "no_adapter",
                "devices": []
            })
            return

        try:
            # Scan for devices
            devices = self._scan_devices()

            if devices is None:
                # Scan failed - hardware may have been disconnected
                self.world_state.update("bluetooth_scanner", {
                    "available": False,
                    "status": "scan_failed",
                    "devices": []
                })
                return

            # Extract features
            features = self._extract_features(devices)

            # Update world state with REAL data
            self.world_state.update("bluetooth_scanner", {
                "available": True,
                "status": "active",
                "last_scan": time.time(),
                "scan_count": self.scan_count,
                "devices": devices,
                "features": features
            })

            self.scan_count += 1

        except Exception as e:
            self.logger.error(f"Bluetooth scan error: {e}", exc_info=True)
            self.world_state.update("bluetooth_scanner", {
                "available": False,
                "status": "error",
                "error": str(e)
            })

    def _scan_devices(self) -> Optional[List[Dict]]:
        """
        Scan for Bluetooth devices using bluetoothctl.

        Returns:
            List of device dictionaries or None if scan failed
        """
        try:
            # Start scan
            subprocess.run(
                ['bluetoothctl', 'scan', 'on'],
                capture_output=True,
                timeout=2
            )

            # Scan for 10 seconds
            time.sleep(10)

            # Stop scan
            subprocess.run(
                ['bluetoothctl', 'scan', 'off'],
                capture_output=True,
                timeout=2
            )

            # Get discovered devices
            result = subprocess.run(
                ['bluetoothctl', 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.logger.warning("bluetoothctl devices command failed")
                return None

            # Parse devices
            devices = []
            for line in result.stdout.strip().split('\n'):
                if not line.startswith('Device'):
                    continue

                # Parse: Device AA:BB:CC:DD:EE:FF Device Name
                match = re.match(r'Device\s+([0-9A-F:]+)\s+(.*)', line, re.IGNORECASE)
                if not match:
                    continue

                mac = match.group(1)
                name = match.group(2).strip() or "Unknown Device"

                # Get device info (RSSI, type, etc.)
                info = self._get_device_info(mac)

                devices.append({
                    "mac": mac,
                    "name": name,
                    "rssi": info.get("rssi", -999),  # Signal strength
                    "type": info.get("type", "unknown"),
                    "class": info.get("class", "unknown"),
                    "connected": info.get("connected", False)
                })

            return devices

        except subprocess.TimeoutExpired:
            self.logger.error("Bluetooth scan timeout")
            return None
        except Exception as e:
            self.logger.error(f"Bluetooth scan exception: {e}")
            return None

    def _get_device_info(self, mac: str) -> Dict:
        """
        Get detailed information about a Bluetooth device.

        Args:
            mac: Device MAC address

        Returns:
            Dictionary with device info
        """
        try:
            result = subprocess.run(
                ['bluetoothctl', 'info', mac],
                capture_output=True,
                text=True,
                timeout=3
            )

            info = {}

            # Parse output
            for line in result.stdout.split('\n'):
                line = line.strip()

                # RSSI (signal strength)
                if 'RSSI:' in line:
                    try:
                        rssi = int(line.split(':')[1].strip())
                        info['rssi'] = rssi
                    except:
                        pass

                # Device class/type
                if 'Icon:' in line:
                    icon = line.split(':')[1].strip()
                    info['type'] = icon  # phone, computer, audio-card, etc.

                # Device class
                if 'Class:' in line:
                    device_class = line.split(':')[1].strip()
                    info['class'] = device_class

                # Connection status
                if 'Connected:' in line:
                    connected = 'yes' in line.lower()
                    info['connected'] = connected

            return info

        except Exception as e:
            self.logger.debug(f"Could not get info for {mac}: {e}")
            return {}

    def _extract_features(self, devices: List[Dict]) -> Dict:
        """
        Extract Bluetooth features for Coral TPU model.

        Args:
            devices: List of detected devices

        Returns:
            Dictionary of normalized features (0.0-1.0)
        """
        if not devices:
            return {
                "devices_count": 0.0,
                "devices_le": 0.0,
                "devices_classic": 0.0,
                "avg_rssi": 0.0,
                "max_rssi": 0.0,
                "phones_count": 0.0,
                "audio_devices": 0.0,
                "computers": 0.0,
                "connected_devices": 0.0,
                "unknown_devices": 0.0
            }

        # RSSI (signal strength) - typically -100 to -30 dBm
        rssi_values = [d["rssi"] for d in devices if d["rssi"] > -100]
        avg_rssi = sum(rssi_values) / len(rssi_values) if rssi_values else -100
        max_rssi = max(rssi_values) if rssi_values else -100

        # Normalize RSSI: -100 dBm = 0.0, -30 dBm = 1.0
        avg_rssi_norm = max((avg_rssi + 100) / 70, 0.0)
        max_rssi_norm = max((max_rssi + 100) / 70, 0.0)

        # Count device types
        phones = sum(1 for d in devices if 'phone' in d['type'].lower())
        audio = sum(1 for d in devices if 'audio' in d['type'].lower() or 'headset' in d['type'].lower())
        computers = sum(1 for d in devices if 'computer' in d['type'].lower())
        connected = sum(1 for d in devices if d['connected'])
        unknown = sum(1 for d in devices if d['type'] == 'unknown')

        return {
            "devices_count": min(len(devices) / 10.0, 1.0),  # Normalize to 10 devices max
            "devices_le": 0.5,  # TODO: Distinguish LE vs Classic
            "devices_classic": 0.5,
            "avg_rssi": avg_rssi_norm,
            "max_rssi": max_rssi_norm,
            "phones_count": min(phones / 5.0, 1.0),
            "audio_devices": min(audio / 3.0, 1.0),
            "computers": min(computers / 2.0, 1.0),
            "connected_devices": min(connected / 3.0, 1.0),
            "unknown_devices": min(unknown / 5.0, 1.0)
        }

    def cleanup(self) -> None:
        """Clean up Bluetooth scanner resources."""
        self.logger.info("Shutting down Bluetooth Scanner Daemon...")

        try:
            # Stop any ongoing scan
            subprocess.run(
                ['bluetoothctl', 'scan', 'off'],
                capture_output=True,
                timeout=2
            )
        except:
            pass

        self.logger.info(f"  Total scans performed: {self.scan_count}")


if __name__ == "__main__":
    # Test Bluetooth scanner
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("BLUETOOTH SCANNER DAEMON TEST")
    print("=" * 70)

    # Create world state
    ws = WorldState()

    # Create Bluetooth scanner
    scanner = BluetoothScannerDaemon(ws, update_rate=15.0)

    if not scanner.initialize():
        print("✗ Bluetooth scanner not available (no adapter or bluetoothctl)")
        sys.exit(1)

    print("\n✓ Bluetooth Scanner initialized")
    print("✓ Scanning for devices every 15 seconds...")
    print("Press Ctrl+C to quit\n")

    # Run scanning loop
    try:
        scanner.start()

        while True:
            time.sleep(3)

            # Show current Bluetooth status
            status = ws.get("bluetooth_scanner")
            if status and status.get("available"):
                devices = status.get("devices", [])
                features = status.get("features", {})

                print(f"\n📱 Found {len(devices)} Bluetooth devices:")
                for i, dev in enumerate(devices[:5], 1):  # Show first 5
                    rssi = dev['rssi']
                    signal_bars = "▂▄▆█"[min(max(int((rssi + 100) / 17.5), 0), 3)] if rssi > -100 else "·"
                    device_type = {"phone": "📱", "audio-card": "🎧", "computer": "💻"}.get(dev['type'], "📡")
                    print(f"  {i}. {signal_bars} {device_type} {dev['name'][:30]:30} {rssi:4} dBm")

                print(f"\n📊 Features:")
                print(f"  Phones: {int(features.get('phones_count', 0) * 5)}")
                print(f"  Audio devices: {int(features.get('audio_devices', 0) * 3)}")
                print(f"  Avg RSSI: {features.get('avg_rssi', 0)*100:.0f}%")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        scanner.stop()
        scanner.join(timeout=3)

    print("\n✓ Bluetooth Scanner test complete\n")
