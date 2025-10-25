#!/usr/bin/env python3
"""
Real Sensor Data Recorder - Learning from Reality

This module captures REAL sensor data and converts it into training data
for the Coral TPU model. Unlike synthetic data, this teaches the model
what the ACTUAL environment looks like.

The system records:
- WiFi network patterns (real SSIDs, signal strengths, congestion)
- Bluetooth device patterns (real devices, RSSI values)
- Hardware state changes (real connect/disconnect events)
- Environmental correlations (real sensor readings)
- Temporal patterns (actual usage times, idle periods)

This data is then used to:
1. Augment synthetic training data with real observations
2. Retrain the Coral model weekly with improved accuracy
3. Personalize visualizations to the actual environment
4. Detect true anomalies (not just synthetic threats)
"""

import logging
import time
import threading
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np

from world_state import WorldState
from core.event_bus import EventBus, Event, EventCategory, EventPriority

logger = logging.getLogger("RealSensorRecorder")


@dataclass
class SensorSnapshot:
    """A single snapshot of all sensor readings at a point in time."""
    timestamp: float
    wifi_networks: int
    wifi_2_4ghz: int
    wifi_5ghz: int
    wifi_avg_signal: float
    wifi_max_signal: float
    wifi_open: int
    bluetooth_devices: int
    bluetooth_phones: int
    bluetooth_audio: int
    bluetooth_avg_rssi: float
    hardware_connected: int
    hardware_categories: str  # JSON string
    user_present: bool
    threat_level: float
    label: str  # "normal", "threat", "anomaly", "learning"


class RealSensorRecorder:
    """
    Records real sensor data for training the Coral TPU model.

    This is the bridge between your live sensor data and the AI model.
    Every 10 seconds, it captures the current state of all sensors and
    stores it as a training example.

    Over time, this builds a dataset of YOUR actual environment, allowing
    the model to learn what normal looks like for YOU specifically.
    """

    def __init__(
        self,
        world_state: WorldState,
        event_bus: EventBus,
        db_path: str = "coral_training/real_sensor_data.db",
        recording_interval: float = 10.0
    ):
        """
        Initialize sensor recorder.

        Args:
            world_state: Central world state
            event_bus: Event bus for notifications
            db_path: Path to SQLite database for recorded data
            recording_interval: Seconds between recordings
        """
        self.world_state = world_state
        self.event_bus = event_bus
        self.recording_interval = recording_interval

        # Database setup
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

        # Worker thread
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False

        # Statistics
        self.snapshots_recorded = 0
        self.last_recording_time = 0.0

        # Current threat level (updated by events)
        self.current_threat_level = 0.0
        self.current_label = "normal"

        # Subscribe to events
        self._setup_event_subscriptions()

        logger.info(f"Real Sensor Recorder initialized (db: {self.db_path})")

    def _initialize_database(self) -> None:
        """Create database schema for sensor recordings."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Sensor snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                wifi_networks INTEGER,
                wifi_2_4ghz INTEGER,
                wifi_5ghz INTEGER,
                wifi_avg_signal REAL,
                wifi_max_signal REAL,
                wifi_open INTEGER,
                bluetooth_devices INTEGER,
                bluetooth_phones INTEGER,
                bluetooth_audio INTEGER,
                bluetooth_avg_rssi REAL,
                hardware_connected INTEGER,
                hardware_categories TEXT,
                user_present INTEGER,
                threat_level REAL,
                label TEXT
            )
        """)

        # Index for time-based queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp
            ON sensor_snapshots(timestamp DESC)
        """)

        # Index for label-based queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_label
            ON sensor_snapshots(label)
        """)

        conn.commit()
        conn.close()

        logger.info("Sensor recording database initialized")

    def _setup_event_subscriptions(self) -> None:
        """Subscribe to relevant events."""
        # Threat detection
        self.event_bus.subscribe(
            EventCategory.THREAT_DETECTED,
            self._on_threat_detected
        )
        self.event_bus.subscribe(
            EventCategory.THREAT_CLEARED,
            self._on_threat_cleared
        )

        logger.debug("Event subscriptions configured")

    def start(self) -> None:
        """Start recording sensor data."""
        if self._running:
            logger.warning("Sensor recorder already running")
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._recording_loop,
            name="SensorRecorder-Worker",
            daemon=True
        )
        self._worker_thread.start()

        logger.info(f"Sensor recorder started (interval: {self.recording_interval}s)")

    def stop(self) -> None:
        """Stop recording sensor data."""
        if not self._running:
            return

        logger.info("Stopping sensor recorder...")
        self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=3)

        logger.info(f"Sensor recorder stopped (recorded: {self.snapshots_recorded} snapshots)")

    def _recording_loop(self) -> None:
        """Main loop that records sensor data."""
        logger.info("Sensor recording loop started")

        while self._running:
            try:
                # Record current sensor state
                snapshot = self._capture_snapshot()
                self._store_snapshot(snapshot)

                self.snapshots_recorded += 1
                self.last_recording_time = time.time()

                # Log progress periodically
                if self.snapshots_recorded % 100 == 0:
                    logger.info(f"Recorded {self.snapshots_recorded} sensor snapshots")

                # Sleep until next recording
                time.sleep(self.recording_interval)

            except Exception as e:
                logger.error(f"Recording error: {e}", exc_info=True)
                time.sleep(5.0)

        logger.info("Sensor recording loop stopped")

    def _capture_snapshot(self) -> SensorSnapshot:
        """
        Capture current state of all sensors.

        Returns:
            SensorSnapshot with current values
        """
        # WiFi data
        wifi_data = self.world_state.get("wifi_scanner") or {}
        wifi_features = wifi_data.get("features", {})
        wifi_networks = wifi_data.get("networks", [])

        # Bluetooth data
        bt_data = self.world_state.get("bluetooth_scanner") or {}
        bt_features = bt_data.get("features", {})
        bt_devices = bt_data.get("devices", [])

        # Hardware data
        hw_data = self.world_state.get("hardware_monitor") or {}
        hw_categories = hw_data.get("categories", {})

        # User presence (if available)
        user_present = False  # TODO: Integrate with user detection

        return SensorSnapshot(
            timestamp=time.time(),
            wifi_networks=len(wifi_networks),
            wifi_2_4ghz=int(wifi_features.get("networks_2_4ghz", 0) * 15),
            wifi_5ghz=int(wifi_features.get("networks_5ghz", 0) * 10),
            wifi_avg_signal=wifi_features.get("avg_signal_strength", 0.0),
            wifi_max_signal=wifi_features.get("max_signal_strength", 0.0),
            wifi_open=int(wifi_features.get("open_networks", 0) * 5),
            bluetooth_devices=len(bt_devices),
            bluetooth_phones=int(bt_features.get("phones_count", 0) * 5),
            bluetooth_audio=int(bt_features.get("audio_devices", 0) * 3),
            bluetooth_avg_rssi=bt_features.get("avg_rssi", 0.0),
            hardware_connected=hw_data.get("available_capabilities", 0),
            hardware_categories=json.dumps(hw_categories),
            user_present=user_present,
            threat_level=self.current_threat_level,
            label=self.current_label
        )

    def _store_snapshot(self, snapshot: SensorSnapshot) -> None:
        """
        Store snapshot in database.

        Args:
            snapshot: Snapshot to store
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sensor_snapshots (
                timestamp, wifi_networks, wifi_2_4ghz, wifi_5ghz,
                wifi_avg_signal, wifi_max_signal, wifi_open,
                bluetooth_devices, bluetooth_phones, bluetooth_audio,
                bluetooth_avg_rssi, hardware_connected, hardware_categories,
                user_present, threat_level, label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.timestamp,
            snapshot.wifi_networks,
            snapshot.wifi_2_4ghz,
            snapshot.wifi_5ghz,
            snapshot.wifi_avg_signal,
            snapshot.wifi_max_signal,
            snapshot.wifi_open,
            snapshot.bluetooth_devices,
            snapshot.bluetooth_phones,
            snapshot.bluetooth_audio,
            snapshot.bluetooth_avg_rssi,
            snapshot.hardware_connected,
            snapshot.hardware_categories,
            int(snapshot.user_present),
            snapshot.threat_level,
            snapshot.label
        ))

        conn.commit()
        conn.close()

    def _on_threat_detected(self, event: Event) -> None:
        """Handle threat detection event."""
        self.current_threat_level = event.data.get("confidence", 1.0)
        self.current_label = "threat"
        logger.info(f"Threat detected - labeling future snapshots as 'threat'")

    def _on_threat_cleared(self, event: Event) -> None:
        """Handle threat cleared event."""
        self.current_threat_level = 0.0
        self.current_label = "normal"
        logger.info(f"Threat cleared - labeling future snapshots as 'normal'")

    def export_training_data(
        self,
        output_path: str,
        limit: Optional[int] = None,
        balance_labels: bool = True
    ) -> int:
        """
        Export recorded data as training examples for Coral TPU.

        Args:
            output_path: Path to output CSV file
            limit: Maximum number of examples (None = all)
            balance_labels: Balance examples across labels

        Returns:
            Number of examples exported
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get snapshots
        query = "SELECT * FROM sensor_snapshots ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            logger.warning("No sensor data to export")
            return 0

        # Convert to training format
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV header
        with open(output, 'w') as f:
            f.write("timestamp,wifi_networks,wifi_2_4ghz,wifi_5ghz,wifi_avg_signal,")
            f.write("wifi_max_signal,wifi_open,bluetooth_devices,bluetooth_phones,")
            f.write("bluetooth_audio,bluetooth_avg_rssi,hardware_connected,")
            f.write("user_present,threat_level,label\n")

            # Write data rows
            for row in rows:
                f.write(f"{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},")
                f.write(f"{row[6]},{row[7]},{row[8]},{row[9]},{row[10]},")
                f.write(f"{row[11]},{row[12]},{row[14]},{row[15]},{row[16]}\n")

        conn.close()

        logger.info(f"Exported {len(rows)} training examples to {output}")
        return len(rows)

    def get_statistics(self) -> Dict[str, Any]:
        """Get recording statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Total snapshots
        cursor.execute("SELECT COUNT(*) FROM sensor_snapshots")
        total = cursor.fetchone()[0]

        # Snapshots by label
        cursor.execute("SELECT label, COUNT(*) FROM sensor_snapshots GROUP BY label")
        by_label = {row[0]: row[1] for row in cursor.fetchall()}

        # Time range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sensor_snapshots")
        min_time, max_time = cursor.fetchone()

        conn.close()

        return {
            "total_snapshots": total,
            "by_label": by_label,
            "time_range_hours": (max_time - min_time) / 3600 if min_time and max_time else 0,
            "recording_interval": self.recording_interval,
            "snapshots_recorded": self.snapshots_recorded
        }


if __name__ == "__main__":
    # Test sensor recorder
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("REAL SENSOR RECORDER TEST")
    print("=" * 70)

    from core.event_bus import get_event_bus

    # Create dependencies
    ws = WorldState()
    bus = get_event_bus()
    bus.start()

    # Create recorder
    recorder = RealSensorRecorder(ws, bus, recording_interval=2.0)
    recorder.start()

    print("\n✓ Sensor recorder started (recording every 2 seconds)")
    print("  Recording real sensor data...")
    print("  Press Ctrl+C to stop\n")

    try:
        for i in range(10):
            time.sleep(2)
            stats = recorder.get_statistics()
            print(f"  Snapshots: {stats['snapshots_recorded']}, Labels: {stats['by_label']}")

    except KeyboardInterrupt:
        pass

    # Export data
    print("\n📦 Exporting training data...")
    count = recorder.export_training_data("test_training_data.csv")
    print(f"  Exported {count} examples")

    # Cleanup
    recorder.stop()
    bus.stop()

    print("\n✓ Test complete\n")
