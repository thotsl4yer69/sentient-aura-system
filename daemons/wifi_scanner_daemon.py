#!/usr/bin/env python3
"""
WiFi Scanner Daemon - Real WiFi Network Detection

Uses nmcli to scan for WiFi networks and extract real signal data.
NO SIMULATED DATA - returns None if no WiFi adapter is available.
"""

import logging
import subprocess
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daemon_base import BaseDaemon
from world_state import WorldState

logger = logging.getLogger("WiFiScanner")


class WiFiScannerDaemon(BaseDaemon):
    """
    Scans for WiFi networks using nmcli.

    Features:
    - Real network detection (no simulated data)
    - Signal strength measurement
    - Security protocol detection
    - Band detection (2.4GHz/5GHz)
    - Network congestion analysis
    """

    def __init__(self, world_state: WorldState, update_rate: float = 10.0):
        """
        Initialize WiFi scanner.

        Args:
            world_state: Central world state
            update_rate: Scan frequency in seconds
        """
        super().__init__("wifi_scanner", world_state, update_rate)

        self.wifi_available = False
        self.last_scan_time = 0
        self.scan_count = 0

    def initialize(self) -> bool:
        """Initialize WiFi scanner."""
        self.logger.info("Initializing WiFi Scanner Daemon...")

        try:
            # Check if nmcli is available
            result = subprocess.run(
                ['which', 'nmcli'],
                capture_output=True,
                timeout=2
            )

            if result.returncode != 0:
                self.logger.warning("nmcli not found - WiFi scanning disabled")
                self.wifi_available = False
                return False

            # Check if WiFi adapter exists
            result = subprocess.run(
                ['nmcli', 'device', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Look for wifi device
            self.wifi_available = 'wifi' in result.stdout.lower()

            if not self.wifi_available:
                self.logger.warning("No WiFi adapter detected - WiFi scanning disabled")
                return False

            self.logger.info("✓ WiFi Scanner initialized")
            return True

        except Exception as e:
            self.logger.error(f"WiFi scanner initialization failed: {e}")
            self.wifi_available = False
            return False

    def update(self) -> None:
        """Scan for WiFi networks and update world state."""

        if not self.wifi_available:
            # No WiFi adapter - return None, NO SIMULATED DATA
            self.world_state.update("wifi_scanner", {
                "available": False,
                "status": "no_adapter",
                "networks": []
            })
            return

        try:
            # Scan for networks
            networks = self._scan_networks()

            if networks is None:
                # Scan failed - hardware may have been disconnected
                self.world_state.update("wifi_scanner", {
                    "available": False,
                    "status": "scan_failed",
                    "networks": []
                })
                return

            # Extract features
            features = self._extract_features(networks)

            # Update world state with REAL data
            self.world_state.update("wifi_scanner", {
                "available": True,
                "status": "active",
                "last_scan": time.time(),
                "scan_count": self.scan_count,
                "networks": networks,
                "features": features
            })

            self.scan_count += 1

        except Exception as e:
            self.logger.error(f"WiFi scan error: {e}", exc_info=True)
            self.world_state.update("wifi_scanner", {
                "available": False,
                "status": "error",
                "error": str(e)
            })

    def _scan_networks(self) -> Optional[List[Dict]]:
        """
        Scan for WiFi networks using nmcli.

        Returns:
            List of network dictionaries or None if scan failed
        """
        try:
            # Rescan networks
            subprocess.run(
                ['nmcli', 'device', 'wifi', 'rescan'],
                capture_output=True,
                timeout=10
            )

            # Wait a moment for scan to complete
            time.sleep(0.5)

            # Get network list
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,FREQ,SECURITY,BSSID', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.logger.warning("nmcli scan failed")
                return None

            # Parse output
            networks = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split(':')
                if len(parts) < 5:
                    continue

                ssid = parts[0]
                signal = int(parts[1]) if parts[1] else 0
                freq = int(parts[2]) if parts[2] else 0
                security = parts[3]
                bssid = parts[4]

                # Determine band
                band = "5GHz" if freq > 3000 else "2.4GHz"

                networks.append({
                    "ssid": ssid,
                    "signal": signal,  # 0-100
                    "frequency": freq,  # MHz
                    "band": band,
                    "security": security,
                    "bssid": bssid
                })

            return networks

        except subprocess.TimeoutExpired:
            self.logger.error("WiFi scan timeout")
            return None
        except Exception as e:
            self.logger.error(f"WiFi scan exception: {e}")
            return None

    def _extract_features(self, networks: List[Dict]) -> Dict:
        """
        Extract WiFi features for Coral TPU model.

        Args:
            networks: List of detected networks

        Returns:
            Dictionary of normalized features (0.0-1.0)
        """
        if not networks:
            return {
                "networks_count": 0.0,
                "networks_2_4ghz": 0.0,
                "networks_5ghz": 0.0,
                "avg_signal_strength": 0.0,
                "max_signal_strength": 0.0,
                "open_networks": 0.0,
                "encrypted_networks": 0.0,
                "congestion_2_4ghz": 0.0,
                "congestion_5ghz": 0.0,
                "hidden_networks": 0.0,
                "unique_vendors": 0.0,
                "probe_requests": 0.0
            }

        # Count by band
        networks_2_4 = sum(1 for n in networks if n["band"] == "2.4GHz")
        networks_5 = sum(1 for n in networks if n["band"] == "5GHz")

        # Signal strength
        signals = [n["signal"] for n in networks if n["signal"] > 0]
        avg_signal = sum(signals) / len(signals) if signals else 0
        max_signal = max(signals) if signals else 0

        # Security
        open_networks = sum(1 for n in networks if not n["security"] or n["security"] == "--")
        encrypted_networks = len(networks) - open_networks

        # Hidden networks (empty SSID)
        hidden = sum(1 for n in networks if not n["ssid"] or n["ssid"] == "")

        return {
            "networks_count": min(len(networks) / 20.0, 1.0),  # Normalize to 20 networks max
            "networks_2_4ghz": min(networks_2_4 / 15.0, 1.0),
            "networks_5ghz": min(networks_5 / 10.0, 1.0),
            "avg_signal_strength": avg_signal / 100.0,  # Already 0-100
            "max_signal_strength": max_signal / 100.0,
            "open_networks": min(open_networks / 5.0, 1.0),
            "encrypted_networks": min(encrypted_networks / 15.0, 1.0),
            "congestion_2_4ghz": min(networks_2_4 / 10.0, 1.0),  # >10 = congested
            "congestion_5ghz": min(networks_5 / 8.0, 1.0),
            "hidden_networks": min(hidden / 3.0, 1.0),
            "unique_vendors": 0.5,  # TODO: Extract from BSSID OUI
            "probe_requests": 0.0   # TODO: Requires monitor mode
        }

    def cleanup(self) -> None:
        """Clean up WiFi scanner resources."""
        self.logger.info("Shutting down WiFi Scanner Daemon...")
        self.logger.info(f"  Total scans performed: {self.scan_count}")


if __name__ == "__main__":
    # Test WiFi scanner
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("WIFI SCANNER DAEMON TEST")
    print("=" * 70)

    # Create world state
    ws = WorldState()

    # Create WiFi scanner
    scanner = WiFiScannerDaemon(ws, update_rate=5.0)

    if not scanner.initialize():
        print("✗ WiFi scanner not available (no adapter or nmcli)")
        sys.exit(1)

    print("\n✓ WiFi Scanner initialized")
    print("✓ Scanning for networks every 5 seconds...")
    print("Press Ctrl+C to quit\n")

    # Run scanning loop
    try:
        scanner.start()

        while True:
            time.sleep(2)

            # Show current WiFi status
            status = ws.get("wifi_scanner")
            if status and status.get("available"):
                networks = status.get("networks", [])
                features = status.get("features", {})

                print(f"\n📡 Found {len(networks)} WiFi networks:")
                for i, net in enumerate(networks[:5], 1):  # Show first 5
                    signal_bars = "▂▄▆█"[min(int(net['signal'] / 25), 3)]
                    security = "🔒" if net['security'] and net['security'] != "--" else "🔓"
                    print(f"  {i}. {signal_bars} {security} {net['ssid'][:30]:30} {net['signal']:3}% {net['band']}")

                print(f"\n📊 Features:")
                print(f"  2.4GHz congestion: {features.get('congestion_2_4ghz', 0)*100:.0f}%")
                print(f"  5GHz congestion: {features.get('congestion_5ghz', 0)*100:.0f}%")
                print(f"  Avg signal: {features.get('avg_signal_strength', 0)*100:.0f}%")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        scanner.stop()
        scanner.join(timeout=3)

    print("\n✓ WiFi Scanner test complete\n")
