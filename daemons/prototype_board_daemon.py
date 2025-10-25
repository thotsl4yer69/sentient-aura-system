#!/usr/bin/env python3
"""
Prototype Sensor Board Daemon
Unified daemon managing multiple GPIO sensors on Raspberry Pi.

Demonstrates modularity of event-driven architecture by seamlessly
integrating a new hardware module with multiple sensor types.

Sensors:
- PIR Motion Sensor (GPIO input)
- Microphone Level Sensor (ADC analog input)
- Environment Sensor (I2C temperature/humidity)
"""

import time
import logging
from typing import List, Optional, Dict, Any
from threading import Lock

from world_state import WorldState
from sensor_events import SensorEvent, EventType, ThreatLevel
from daemon_base import BaseDaemon

logger = logging.getLogger("prototype_board")

# GPIO Configuration (simulation mode for testing without hardware)
SIMULATION_MODE = True  # Set to False when real hardware is connected

# GPIO Pin Assignments
PIR_PIN = 17        # GPIO17 for PIR motion sensor
MIC_PIN = 0         # ADC Channel 0 for microphone
ENV_I2C_ADDR = 0x76 # I2C address for BME280 sensor

# Thresholds
MIC_THRESHOLD = 800        # Acoustic spike threshold (0-1023)
PIR_COOLDOWN = 5.0         # Seconds between PIR detections
TEMP_ALERT_THRESHOLD = 30  # Temperature alert threshold (°C)


class PrototypeBoardDaemon(BaseDaemon):
    """
    Unified daemon for prototype sensor board.

    Manages multiple sensors and generates standardized SensorEvents
    for consumption by the consciousness loop.
    """

    def __init__(self, world_state: WorldState, update_rate: float = 1.0):
        super().__init__("prototype_board", world_state, update_rate)

        # Sensor state tracking
        self.last_pir_detection = 0.0
        self.last_mic_level = 0
        self.last_env_reading = {"temperature": 0, "humidity": 0}
        self.loop_count = 0

        # Event queue for sensor events
        self.sensor_events: List[SensorEvent] = []
        self.events_lock = Lock()

        # Hardware interfaces
        self.gpio_initialized = False
        self.adc_initialized = False
        self.i2c_initialized = False

        logger.info(f"PrototypeBoardDaemon initialized (simulation={SIMULATION_MODE})")

    def initialize(self) -> bool:
        """
        Initialize GPIO hardware interfaces.

        Returns:
            True if initialization successful
        """
        logger.info("Initializing prototype sensor board hardware...")

        if SIMULATION_MODE:
            logger.info("  Running in SIMULATION mode (no hardware required)")
            self.gpio_initialized = True
            self.adc_initialized = True
            self.i2c_initialized = True
            return True

        # Real hardware initialization
        try:
            # Try modern gpiod library first (for Raspberry Pi 5/500+)
            try:
                import gpiod
                self.gpio_chip = gpiod.Chip('gpiochip4')  # Pi 5 uses gpiochip4
                self.pir_line = self.gpio_chip.get_line(PIR_PIN)
                self.pir_line.request(consumer="prototype_board", type=gpiod.LINE_REQ_DIR_IN)
                self.gpio_initialized = True
                self.gpio_mode = 'gpiod'
                logger.info(f"  ✓ GPIO initialized via gpiod (PIR on pin {PIR_PIN})")
            except:
                # Fallback to RPi.GPIO for older Pi models
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(PIR_PIN, GPIO.IN)
                self.gpio_initialized = True
                self.gpio_mode = 'RPi.GPIO'
                logger.info(f"  ✓ GPIO initialized via RPi.GPIO (PIR on pin {PIR_PIN})")
        except Exception as e:
            logger.error(f"  ✗ GPIO initialization failed: {e}")
            logger.info("  ℹ Consider running in SIMULATION_MODE or installing gpiod library")
            self.gpio_initialized = False
            self.gpio_mode = None

        try:
            # Initialize ADC for microphone (MCP3008 via SPI)
            import spidev
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 1350000
            self.adc_initialized = True
            logger.info("  ✓ ADC initialized (MCP3008 via SPI)")
        except Exception as e:
            logger.warning(f"  ⚠ ADC initialization failed: {e}")
            # Non-critical - continue without microphone

        try:
            # Initialize I2C for environment sensor (BME280)
            import smbus2
            # Try common I2C bus numbers (Raspberry Pi 5 uses bus 13/14, older models use 1)
            bus_found = False
            for bus_num in [1, 13, 14]:
                try:
                    self.i2c_bus = smbus2.SMBus(bus_num)
                    # Test I2C connection
                    self.i2c_bus.read_byte_data(ENV_I2C_ADDR, 0xD0)
                    self.i2c_initialized = True
                    bus_found = True
                    logger.info(f"  ✓ I2C initialized (BME280 at 0x{ENV_I2C_ADDR:02X} on bus {bus_num})")
                    break
                except:
                    continue
            if not bus_found:
                raise Exception("No I2C bus with BME280 found")
        except Exception as e:
            logger.warning(f"  ⚠ I2C initialization failed: {e}")
            # Non-critical - continue without environment sensor

        return self.gpio_initialized  # At minimum, GPIO must work

    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        logger.info("Cleaning up prototype board hardware...")

        if not SIMULATION_MODE and self.gpio_initialized:
            try:
                if self.gpio_mode == 'gpiod':
                    # Clean up gpiod resources
                    if hasattr(self, 'pir_line'):
                        self.pir_line.release()
                    if hasattr(self, 'gpio_chip'):
                        self.gpio_chip.close()
                    logger.info("  ✓ GPIO (gpiod) cleaned up")
                elif self.gpio_mode == 'RPi.GPIO':
                    # Clean up RPi.GPIO resources
                    import RPi.GPIO as GPIO
                    GPIO.cleanup()
                    logger.info("  ✓ GPIO (RPi.GPIO) cleaned up")
            except Exception as e:
                logger.error(f"  ✗ GPIO cleanup failed: {e}")

        if self.adc_initialized and hasattr(self, 'spi'):
            try:
                self.spi.close()
                logger.info("  ✓ SPI cleaned up")
            except Exception as e:
                logger.error(f"  ✗ SPI cleanup failed: {e}")

    def read_pir_motion_sensor(self) -> Optional[SensorEvent]:
        """
        Read PIR motion sensor.

        Generates Motion_Detected event when motion is detected,
        with cooldown to prevent spam.

        Returns:
            SensorEvent if motion detected, None otherwise
        """
        if not self.gpio_initialized:
            return None

        current_time = time.time()

        # Check cooldown
        if current_time - self.last_pir_detection < PIR_COOLDOWN:
            return None

        # Read PIR state
        if SIMULATION_MODE:
            # Simulate occasional motion detection (5% chance)
            import random
            motion_detected = random.random() < 0.05
        else:
            if self.gpio_mode == 'gpiod':
                # Read using gpiod library
                motion_detected = self.pir_line.get_value() == 1
            elif self.gpio_mode == 'RPi.GPIO':
                # Read using RPi.GPIO library
                import RPi.GPIO as GPIO
                motion_detected = GPIO.input(PIR_PIN) == GPIO.HIGH
            else:
                return None

        if motion_detected:
            self.last_pir_detection = current_time

            logger.info("🚶 PIR: Motion detected")

            # Generate standardized event
            event = SensorEvent(
                source="Proto-PIR",
                event_type=EventType.MOTION_DETECTED,
                data={
                    "state": "detected",
                    "sensor_type": "passive_infrared",
                    "gpio_pin": PIR_PIN
                },
                threat_level=ThreatLevel.LOW,  # Motion alone is not a threat
                threat_description="Motion detected by PIR sensor",
                confidence=0.85  # PIR sensors have some false positives
            )

            return event

        return None

    def read_microphone_level(self) -> Optional[SensorEvent]:
        """
        Read microphone level from ADC.

        Generates Acoustic_Spike event if sound level exceeds threshold.

        Returns:
            SensorEvent if acoustic spike detected, None otherwise
        """
        if not self.adc_initialized:
            return None

        # Read analog value from ADC
        if SIMULATION_MODE:
            # Simulate microphone reading (baseline + occasional spikes)
            import random
            baseline = 400
            spike = random.random() < 0.03  # 3% chance of spike
            mic_level = baseline + (random.randint(400, 600) if spike else random.randint(-50, 50))
        else:
            # Read from MCP3008 ADC
            adc_data = self.spi.xfer2([1, (8 + MIC_PIN) << 4, 0])
            mic_level = ((adc_data[1] & 3) << 8) + adc_data[2]

        self.last_mic_level = mic_level

        # Check for acoustic spike
        if mic_level > MIC_THRESHOLD:
            logger.info(f"🔊 Microphone: Acoustic spike detected (level={mic_level})")

            # Determine threat level based on intensity
            if mic_level > 950:
                threat_level = ThreatLevel.MEDIUM
                threat_desc = f"LOUD acoustic event detected (level={mic_level})"
            else:
                threat_level = ThreatLevel.LOW
                threat_desc = f"Acoustic spike detected (level={mic_level})"

            # Generate standardized event
            event = SensorEvent(
                source="Proto-Mic",
                event_type=EventType.OBJECT_DETECTED,  # Using OBJECT_DETECTED for acoustic
                data={
                    "level": mic_level,
                    "threshold": MIC_THRESHOLD,
                    "sensor_type": "analog_microphone",
                    "adc_channel": MIC_PIN
                },
                threat_level=threat_level,
                threat_description=threat_desc,
                confidence=0.6  # Analog mics have moderate accuracy
            )

            return event

        return None

    def read_environment_sensor(self) -> Optional[SensorEvent]:
        """
        Read temperature and humidity from environment sensor.

        Generates periodic Environment_Reading events and alerts
        for abnormal conditions.

        Returns:
            SensorEvent with environmental data
        """
        if not self.i2c_initialized:
            return None

        # Read environmental data
        if SIMULATION_MODE:
            # Simulate realistic environmental readings
            import random
            temperature = 20 + random.gauss(2, 1)  # 20°C ± 2°C
            humidity = 45 + random.gauss(5, 3)     # 45% ± 5%
            pressure = 1013 + random.gauss(5, 2)   # 1013 hPa ± 5 hPa
        else:
            # Read from BME280 sensor via I2C
            # This is simplified - real BME280 requires calibration
            try:
                raw_temp = self.i2c_bus.read_word_data(ENV_I2C_ADDR, 0xFA)
                raw_hum = self.i2c_bus.read_word_data(ENV_I2C_ADDR, 0xFD)
                # Convert raw values (would need calibration in production)
                temperature = raw_temp / 100.0
                humidity = raw_hum / 100.0
                pressure = 1013.0  # Placeholder
            except Exception as e:
                logger.error(f"Environment sensor read failed: {e}")
                return None

        self.last_env_reading = {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure
        }

        # Determine if conditions are abnormal
        threat_level = ThreatLevel.NONE
        threat_desc = None

        if temperature > TEMP_ALERT_THRESHOLD:
            threat_level = ThreatLevel.LOW
            threat_desc = f"Elevated temperature detected ({temperature:.1f}°C)"

        if temperature < 5:
            threat_level = ThreatLevel.LOW
            threat_desc = f"Low temperature detected ({temperature:.1f}°C)"

        # Generate standardized event
        event = SensorEvent(
            source="Proto-Enviro",
            event_type=EventType.TEMPERATURE_ANOMALY if threat_level != ThreatLevel.NONE else EventType.RF_SIGNAL,  # Reusing existing types
            data={
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "pressure": round(pressure, 1),
                "sensor_type": "bme280",
                "i2c_address": f"0x{ENV_I2C_ADDR:02X}"
            },
            threat_level=threat_level,
            threat_description=threat_desc,
            confidence=0.95  # Environmental sensors are very accurate
        )

        return event

    def get_sensor_events(self) -> List[SensorEvent]:
        """
        Get all pending sensor events and clear queue.

        Returns:
            List of SensorEvents from all sensors
        """
        with self.events_lock:
            events = self.sensor_events.copy()
            self.sensor_events.clear()
            return events

    def get_status(self) -> Dict[str, Any]:
        """
        Get daemon status and sensor readings.

        Returns:
            Status dictionary
        """
        return {
            "daemon": "prototype_board",
            "running": self.is_running(),
            "simulation_mode": SIMULATION_MODE,
            "sensors": {
                "pir": {
                    "enabled": self.gpio_initialized,
                    "last_detection": self.last_pir_detection,
                    "pin": PIR_PIN
                },
                "microphone": {
                    "enabled": self.adc_initialized,
                    "last_level": self.last_mic_level,
                    "threshold": MIC_THRESHOLD
                },
                "environment": {
                    "enabled": self.i2c_initialized,
                    "last_reading": self.last_env_reading
                }
            },
            "event_queue_size": len(self.sensor_events)
        }

    def update(self) -> None:
        """
        Main daemon update - read all sensors and generate events.

        This is called by BaseDaemon's thread at update_rate frequency.
        """
        self.loop_count += 1

        # Read PIR motion sensor
        pir_event = self.read_pir_motion_sensor()
        if pir_event:
            with self.events_lock:
                self.sensor_events.append(pir_event)

            # Log to world state
            self.world_state.add_alert(
                "pir_motion",
                "Motion detected by PIR sensor",
                severity="info"
            )

        # Read microphone level
        mic_event = self.read_microphone_level()
        if mic_event:
            with self.events_lock:
                self.sensor_events.append(mic_event)

            # Log to world state
            self.world_state.add_alert(
                "acoustic_spike",
                f"Acoustic spike: {self.last_mic_level}",
                severity="info" if mic_event.threat_level == ThreatLevel.LOW else "warning"
            )

        # Read environment sensor (less frequently - every 10 cycles)
        if self.loop_count % 10 == 0:
            env_event = self.read_environment_sensor()
            if env_event:
                with self.events_lock:
                    self.sensor_events.append(env_event)

                # Update world state with environmental data
                self.world_state.update_environment({
                    "temperature_c": self.last_env_reading["temperature"],
                    "humidity_percent": self.last_env_reading["humidity"],
                    "pressure_hpa": self.last_env_reading.get("pressure", 0)
                })


# Standalone testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 70)
    print("PROTOTYPE SENSOR BOARD DAEMON - TEST")
    print("=" * 70)

    # Initialize world state
    ws = WorldState()

    # Create daemon
    daemon = PrototypeBoardDaemon(ws, update_rate=2.0)

    # Initialize hardware
    if daemon.initialize():
        print("✓ Hardware initialized")

        # Start daemon
        daemon.start()
        print("✓ Daemon started")

        # Run for 30 seconds
        try:
            for i in range(30):
                time.sleep(1)

                # Check for events
                events = daemon.get_sensor_events()
                if events:
                    print(f"\n[{i}s] Events detected:")
                    for event in events:
                        print(f"  - {event}")

                # Show status every 5 seconds
                if i % 5 == 0:
                    status = daemon.get_status()
                    print(f"\n[{i}s] Status:")
                    print(f"  PIR: {status['sensors']['pir']['enabled']}")
                    print(f"  Mic: Level={status['sensors']['microphone']['last_level']}")
                    print(f"  Env: {status['sensors']['environment']['last_reading']}")

        except KeyboardInterrupt:
            print("\n\nShutting down...")

        # Stop daemon
        daemon.stop()
        daemon.join(timeout=5)
        print("✓ Daemon stopped")

    else:
        print("✗ Hardware initialization failed")

    print("\n" + "=" * 70)
