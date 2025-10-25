#!/usr/bin/env python3
"""
IMU Daemon - BNO055 9-DOF Inertial Measurement Unit

Provides orientation, acceleration, and motion data from BNO055 sensor.
"""

import logging
import time
import sys
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daemon_base import BaseDaemon
from world_state import WorldState

logger = logging.getLogger("IMU")


class IMUDaemon(BaseDaemon):
    """
    BNO055 IMU Daemon - 9-DOF motion and orientation sensing.

    Features:
    - 3-axis accelerometer (measures acceleration and gravity)
    - 3-axis gyroscope (measures angular velocity)
    - 3-axis magnetometer (measures magnetic field)
    - Hardware sensor fusion (quaternion, Euler angles)
    - Calibration status monitoring
    """

    def __init__(self, world_state: WorldState, update_rate: float = 10.0):
        """
        Initialize IMU daemon.

        Args:
            world_state: Central world state
            update_rate: Update frequency in Hz
        """
        super().__init__("imu", world_state, update_rate)

        self.sensor = None
        self.sensor_available = False
        self.sample_count = 0

        # Calibration tracking
        self.calibration_status = {
            'system': 0,
            'gyro': 0,
            'accel': 0,
            'mag': 0
        }

    def initialize(self) -> bool:
        """Initialize BNO055 sensor."""
        self.logger.info("Initializing BNO055 IMU Daemon...")

        try:
            # Try to import Adafruit BNO055 library
            import board
            import busio
            import adafruit_bno055

            # Create I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)

            # Try to create BNO055 sensor
            # BNO055 can be at 0x28 (default) or 0x29 (alternate) or 0x10 (some boards)
            for address in [0x28, 0x29, 0x10]:
                try:
                    self.sensor = adafruit_bno055.BNO055_I2C(i2c, address=address)
                    self.logger.info(f"✓ BNO055 IMU found at address 0x{address:02x}")
                    self.sensor_available = True
                    break
                except Exception as e:
                    self.logger.debug(f"BNO055 not found at 0x{address:02x}: {e}")
                    continue

            if not self.sensor_available:
                self.logger.warning("BNO055 IMU not found at any I2C address")
                return False

            # Configure sensor mode (NDOF = 9-DOF fusion mode)
            # This enables all sensors and hardware fusion
            # self.sensor.mode = adafruit_bno055.NDOF_MODE  # Already default

            self.logger.info("✓ IMU Daemon initialized (9-DOF fusion mode)")
            return True

        except ImportError as e:
            self.logger.warning(f"BNO055 library not available: {e}")
            self.logger.info("Install with: pip3 install adafruit-circuitpython-bno055")
            self.sensor_available = False
            return False
        except Exception as e:
            self.logger.error(f"IMU initialization failed: {e}")
            self.sensor_available = False
            return False

    def update(self) -> None:
        """Read IMU data and update world state."""

        if not self.sensor_available or self.sensor is None:
            # No sensor - return empty data
            self.world_state.update("imu", {
                "available": False,
                "status": "no_sensor"
            })
            return

        try:
            # Read orientation (Euler angles)
            euler = self.sensor.euler
            heading = euler[0] if euler[0] is not None else 0.0
            roll = euler[1] if euler[1] is not None else 0.0
            pitch = euler[2] if euler[2] is not None else 0.0

            # Read quaternion (for 3D rotation)
            quat = self.sensor.quaternion
            qw = quat[0] if quat and quat[0] is not None else 1.0
            qx = quat[1] if quat and quat[1] is not None else 0.0
            qy = quat[2] if quat and quat[2] is not None else 0.0
            qz = quat[3] if quat and quat[3] is not None else 0.0

            # Read linear acceleration (gravity removed)
            linear_accel = self.sensor.linear_acceleration
            ax = linear_accel[0] if linear_accel[0] is not None else 0.0
            ay = linear_accel[1] if linear_accel[1] is not None else 0.0
            az = linear_accel[2] if linear_accel[2] is not None else 0.0

            # Read gravity vector
            gravity = self.sensor.gravity
            gx = gravity[0] if gravity[0] is not None else 0.0
            gy = gravity[1] if gravity[1] is not None else 0.0
            gz = gravity[2] if gravity[2] is not None else 0.0

            # Read gyroscope (angular velocity in rad/s)
            gyro = self.sensor.gyro
            gx_rate = gyro[0] if gyro[0] is not None else 0.0
            gy_rate = gyro[1] if gyro[1] is not None else 0.0
            gz_rate = gyro[2] if gyro[2] is not None else 0.0

            # Read magnetometer (magnetic field in µT)
            mag = self.sensor.magnetic
            mx = mag[0] if mag[0] is not None else 0.0
            my = mag[1] if mag[1] is not None else 0.0
            mz = mag[2] if mag[2] is not None else 0.0

            # Read calibration status
            cal = self.sensor.calibration_status
            self.calibration_status = {
                'system': cal[0] if cal[0] is not None else 0,
                'gyro': cal[1] if cal[1] is not None else 0,
                'accel': cal[2] if cal[2] is not None else 0,
                'mag': cal[3] if cal[3] is not None else 0
            }

            # Detect motion
            accel_magnitude = (ax**2 + ay**2 + az**2)**0.5
            motion_detected = accel_magnitude > 0.5  # m/s² threshold

            # Detect rotation
            gyro_magnitude = (gx_rate**2 + gy_rate**2 + gz_rate**2)**0.5
            rotation_detected = gyro_magnitude > 0.1  # rad/s threshold

            # Extract normalized features for Coral TPU
            features = self._extract_features(
                euler=(heading, roll, pitch),
                linear_accel=(ax, ay, az),
                gyro=(gx_rate, gy_rate, gz_rate),
                motion_magnitude=accel_magnitude,
                rotation_magnitude=gyro_magnitude
            )

            # Update world state
            self.world_state.update("imu", {
                "available": True,
                "status": "active",
                "timestamp": time.time(),
                "sample_count": self.sample_count,

                # Orientation (Euler angles)
                "euler": {
                    "heading": heading,  # 0-360 degrees (yaw)
                    "roll": roll,        # -180 to 180 degrees
                    "pitch": pitch       # -90 to 90 degrees
                },

                # Quaternion (for 3D rotation)
                "quaternion": {
                    "w": qw,
                    "x": qx,
                    "y": qy,
                    "z": qz
                },

                # Linear acceleration (m/s², gravity removed)
                "linear_acceleration": {
                    "x": ax,
                    "y": ay,
                    "z": az,
                    "magnitude": accel_magnitude
                },

                # Gravity vector
                "gravity": {
                    "x": gx,
                    "y": gy,
                    "z": gz
                },

                # Gyroscope (rad/s)
                "gyro": {
                    "x": gx_rate,
                    "y": gy_rate,
                    "z": gz_rate,
                    "magnitude": gyro_magnitude
                },

                # Magnetometer (µT)
                "magnetometer": {
                    "x": mx,
                    "y": my,
                    "z": mz
                },

                # Motion detection
                "motion_detected": motion_detected,
                "rotation_detected": rotation_detected,

                # Calibration status (0-3, 3 = fully calibrated)
                "calibration": self.calibration_status,
                "calibrated": all(v >= 2 for v in self.calibration_status.values()),

                # Normalized features for Coral TPU
                "features": features
            })

            self.sample_count += 1

        except Exception as e:
            self.logger.error(f"IMU read error: {e}", exc_info=True)
            self.world_state.update("imu", {
                "available": False,
                "status": "error",
                "error": str(e)
            })

    def _extract_features(self, euler, linear_accel, gyro, motion_magnitude, rotation_magnitude) -> Dict:
        """
        Extract normalized IMU features for Coral TPU model.

        Args:
            euler: (heading, roll, pitch) in degrees
            linear_accel: (x, y, z) in m/s²
            gyro: (x, y, z) in rad/s
            motion_magnitude: scalar acceleration in m/s²
            rotation_magnitude: scalar angular velocity in rad/s

        Returns:
            Dictionary of normalized features (0.0-1.0)
        """
        heading, roll, pitch = euler
        ax, ay, az = linear_accel
        gx, gy, gz = gyro

        # Normalize orientation (0-1)
        heading_norm = (heading % 360) / 360.0
        roll_norm = (roll + 180) / 360.0  # -180 to 180 → 0 to 1
        pitch_norm = (pitch + 90) / 180.0  # -90 to 90 → 0 to 1

        # Normalize acceleration (typical range: -10 to +10 m/s²)
        ax_norm = max(0.0, min(1.0, (ax + 10) / 20))
        ay_norm = max(0.0, min(1.0, (ay + 10) / 20))
        az_norm = max(0.0, min(1.0, (az + 10) / 20))
        accel_magnitude_norm = min(1.0, motion_magnitude / 10.0)

        # Normalize gyro (typical range: -5 to +5 rad/s)
        gx_norm = max(0.0, min(1.0, (gx + 5) / 10))
        gy_norm = max(0.0, min(1.0, (gy + 5) / 10))
        gz_norm = max(0.0, min(1.0, (gz + 5) / 10))
        gyro_magnitude_norm = min(1.0, rotation_magnitude / 5.0)

        return {
            "heading": heading_norm,
            "roll": roll_norm,
            "pitch": pitch_norm,
            "accel_x": ax_norm,
            "accel_y": ay_norm,
            "accel_z": az_norm,
            "accel_magnitude": accel_magnitude_norm,
            "gyro_x": gx_norm,
            "gyro_y": gy_norm,
            "gyro_z": gz_norm,
            "gyro_magnitude": gyro_magnitude_norm,
            "motion_detected": float(motion_magnitude > 0.5),
            "rotation_detected": float(rotation_magnitude > 0.1),
            "calibrated": float(all(v >= 2 for v in self.calibration_status.values()))
        }

    def cleanup(self) -> None:
        """Clean up IMU resources."""
        self.logger.info("Shutting down IMU Daemon...")
        self.logger.info(f"  Total samples: {self.sample_count}")


if __name__ == "__main__":
    # Test IMU daemon
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("IMU DAEMON TEST")
    print("=" * 70)

    # Create world state
    ws = WorldState()

    # Create IMU daemon
    imu = IMUDaemon(ws, update_rate=10.0)

    if not imu.initialize():
        print("✗ IMU not available")
        sys.exit(1)

    print("\n✓ IMU initialized")
    print("✓ Reading sensor data at 10 Hz...")
    print("Press Ctrl+C to quit\n")

    # Run IMU loop
    try:
        imu.start()

        while True:
            time.sleep(2)

            # Show current IMU status
            status = ws.get("imu")
            if status and status.get("available"):
                euler = status.get("euler", {})
                accel = status.get("linear_acceleration", {})
                cal = status.get("calibration", {})

                print(f"\n📐 Orientation:")
                print(f"  Heading: {euler.get('heading', 0):7.2f}°  Roll: {euler.get('roll', 0):7.2f}°  Pitch: {euler.get('pitch', 0):7.2f}°")
                print(f"\n📊 Linear Acceleration:")
                print(f"  X: {accel.get('x', 0):6.2f} m/s²  Y: {accel.get('y', 0):6.2f} m/s²  Z: {accel.get('z', 0):6.2f} m/s²")
                print(f"  Magnitude: {accel.get('magnitude', 0):6.2f} m/s²  Motion: {'YES' if status.get('motion_detected') else 'no'}")
                print(f"\n🎯 Calibration: Sys={cal.get('system', 0)} Gyro={cal.get('gyro', 0)} Accel={cal.get('accel', 0)} Mag={cal.get('mag', 0)} (3=calibrated)")

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        imu.stop()
        imu.join(timeout=3)

    print("\n✓ IMU test complete\n")
