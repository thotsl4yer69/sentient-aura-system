#!/usr/bin/env python3
"""
Sentient Core - Hardware Discovery Engine
Automatically detects and catalogs all available hardware capabilities.
"""

import logging
import subprocess
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Project paths - portable across systems
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')


@dataclass
class HardwareCapability:
    """Represents a discovered hardware capability."""
    name: str
    category: str  # vision, audio, environment, power, communication, location, etc.
    available: bool
    confidence: float  # 0.0-1.0, how certain we are this hardware exists
    interface: str  # i2c, usb, csi, gpio, etc.
    address: Optional[str] = None  # I2C address, USB device path, etc.
    metadata: Dict = field(default_factory=dict)


class HardwareDiscovery:
    """
    Automatically discovers all available hardware.
    
    This is the foundation of adaptive AI - the system learns what it has
    and configures itself accordingly.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("hardware_discovery")
        self.capabilities: Dict[str, HardwareCapability] = {}
    
    def discover_all(self) -> Dict[str, HardwareCapability]:
        """
        Scan for all hardware capabilities.
        
        Returns:
            Dictionary of discovered capabilities
        """
        self.logger.info("=" * 70)
        self.logger.info("HARDWARE DISCOVERY ENGINE")
        self.logger.info("=" * 70)
        
        # Discover each category
        self._discover_vision()
        self._discover_audio()
        self._discover_environment()
        self._discover_power()
        self._discover_communication()
        self._discover_sensors()  # Motion sensors (IMU, etc.)
        self._discover_location()
        self._discover_compute()
        self._discover_arduino()
        
        # Summary
        available = [c for c in self.capabilities.values() if c.available]
        self.logger.info("=" * 70)
        self.logger.info(f"DISCOVERY COMPLETE: {len(available)}/{len(self.capabilities)} capabilities available")
        self.logger.info("=" * 70)
        
        return self.capabilities
    
    def _discover_vision(self):
        """Discover vision capabilities."""
        self.logger.info("Scanning for vision hardware...")

        # Camera (CSI/USB)
        camera_available = self._check_camera()
        self.capabilities['camera_rgb'] = HardwareCapability(
            name="RGB Camera",
            category="vision",
            available=camera_available,
            confidence=1.0 if camera_available else 0.0,
            interface="csi",
            metadata={"resolution": "640x480", "fps": 30}
        )

        # Thermal camera (I2C)
        thermal_available = self._check_i2c_device(0x2A)  # FLIR Lepton address
        self.capabilities['camera_thermal'] = HardwareCapability(
            name="Thermal Camera",
            category="vision",
            available=thermal_available,
            confidence=0.8 if thermal_available else 0.0,
            interface="i2c",
            address="0x2A"
        )

        # Depth camera (USB)
        depth_available = self._check_usb_device("8086", "0B07")  # Intel RealSense
        self.capabilities['camera_depth'] = HardwareCapability(
            name="Depth Camera",
            category="vision",
            available=depth_available,
            confidence=1.0 if depth_available else 0.0,
            interface="usb",
            metadata={"type": "Intel RealSense"}
        )

        # Vision Daemon (object detection and tracking)
        # Check if camera is available OR explicitly enabled via config
        vision_configured = os.path.exists(os.path.join(CONFIG_DIR, "vision_daemon.enabled")) or \
                          os.environ.get("ENABLE_VISION_DAEMON", "false").lower() == "true"

        # Vision daemon available if camera exists OR explicitly configured (for simulation)
        vision_available = camera_available or vision_configured

        self.capabilities['vision_daemon'] = HardwareCapability(
            name="Vision Daemon (Object Detection)",
            category="vision",
            available=vision_available,
            confidence=0.9 if vision_available else 0.0,
            interface="camera",
            metadata={
                "drone_detection": True,
                "object_tracking": True,
                "simulation_mode": not camera_available and vision_configured
            }
        )
    
    def _discover_audio(self):
        """Discover audio capabilities."""
        self.logger.info("Scanning for audio hardware...")
        
        # ReSpeaker (I2C)
        respeaker_available = self._check_i2c_device(0x35)  # ReSpeaker address
        self.capabilities['microphone_array'] = HardwareCapability(
            name="Microphone Array",
            category="audio",
            available=respeaker_available,
            confidence=0.9 if respeaker_available else 0.0,
            interface="i2c",
            address="0x35",
            metadata={"channels": 2 if respeaker_available else 0}
        )
        
        # Generic audio input
        audio_available = self._check_audio_device()
        self.capabilities['audio_input'] = HardwareCapability(
            name="Audio Input",
            category="audio",
            available=audio_available,
            confidence=0.7 if audio_available else 0.0,
            interface="alsa"
        )
    
    def _discover_environment(self):
        """Discover environmental sensors."""
        self.logger.info("Scanning for environmental sensors...")
        
        # BME280 (temperature, humidity, pressure)
        bme280_available = self._check_i2c_device(0x76) or self._check_i2c_device(0x77)
        self.capabilities['sensor_bme280'] = HardwareCapability(
            name="BME280 Environmental Sensor",
            category="environment",
            available=bme280_available,
            confidence=1.0 if bme280_available else 0.0,
            interface="i2c",
            address="0x76 or 0x77",
            metadata={"measures": ["temperature", "humidity", "pressure"]}
        )
        
        # Gas sensor (MICS6814)
        gas_available = self._check_i2c_device(0x04)  # Enviro+ gas sensor
        self.capabilities['sensor_gas'] = HardwareCapability(
            name="Gas Sensor",
            category="environment",
            available=gas_available,
            confidence=0.8 if gas_available else 0.0,
            interface="i2c",
            address="0x04",
            metadata={"measures": ["oxidising", "reducing", "nh3"]}
        )
        
        # Light sensor (LTR559)
        light_available = self._check_i2c_device(0x23)
        self.capabilities['sensor_light'] = HardwareCapability(
            name="Light Sensor",
            category="environment",
            available=light_available,
            confidence=0.8 if light_available else 0.0,
            interface="i2c",
            address="0x23",
            metadata={"measures": ["light", "proximity"]}
        )
    
    def _discover_power(self):
        """Discover power management hardware."""
        self.logger.info("Scanning for power management...")
        
        # PiJuice
        pijuice_available = self._check_i2c_device(0x14)
        self.capabilities['power_pijuice'] = HardwareCapability(
            name="PiJuice UPS",
            category="power",
            available=pijuice_available,
            confidence=1.0 if pijuice_available else 0.0,
            interface="i2c",
            address="0x14",
            metadata={"battery": True, "ups": True}
        )
    
    def _discover_communication(self):
        """Discover communication hardware."""
        self.logger.info("Scanning for communication devices...")
        
        # Flipper Zero (USB)
        # Check for both known product IDs (5740 and 5741)
        flipper_available = (self._check_usb_device("0483", "5740") or
                           self._check_usb_device("0483", "5741"))
        self.capabilities['comm_flipper'] = HardwareCapability(
            name="Flipper Zero",
            category="communication",
            available=flipper_available,
            confidence=1.0 if flipper_available else 0.0,
            interface="usb",
            metadata={"rf": True, "nfc": True, "infrared": True}
        )

        # Prototype Sensor Board (GPIO + I2C + SPI)
        # Check if GPIO is available and prototype board is configured
        gpio_available = self._check_gpio_available()
        # Check for prototype board config file or environment variable
        proto_configured = os.path.exists(os.path.join(CONFIG_DIR, "prototype_board.enabled")) or \
                          os.environ.get("ENABLE_PROTOTYPE_BOARD", "false").lower() == "true"

        # If no explicit config, assume prototype board is available if GPIO is available
        proto_available = gpio_available or proto_configured

        self.capabilities['sensor_prototype_board'] = HardwareCapability(
            name="Prototype Sensor Board",
            category="sensors",
            available=proto_available,
            confidence=0.9 if proto_available else 0.0,
            interface="gpio+i2c+spi",
            metadata={
                "pir": True,
                "microphone": True,
                "environment": True,
                "simulation_mode": True  # Runs in simulation if no hardware
            }
        )
        
        # LoRaWAN (SPI)
        lora_available = self._check_spi_device()
        self.capabilities['comm_lora'] = HardwareCapability(
            name="LoRaWAN Radio",
            category="communication",
            available=lora_available,
            confidence=0.5 if lora_available else 0.0,
            interface="spi"
        )
        
        # 4G/LTE modem (USB)
        lte_available = self._check_usb_device("1c9e", "9b05")  # Waveshare SIM7600
        self.capabilities['comm_lte'] = HardwareCapability(
            name="4G LTE Modem",
            category="communication",
            available=lte_available,
            confidence=1.0 if lte_available else 0.0,
            interface="usb"
        )
    
    def _discover_location(self):
        """Discover location/navigation hardware."""
        self.logger.info("Scanning for location hardware...")

        # GPS (I2C or UART)
        # NOTE: I2C 0x10 conflicts with BNO055 IMU - GPS is lower priority
        # Only detect as GPS if IMU is not already detected
        gps_available = False  # Disabled - I2C 0x10 is BNO055 IMU
        self.capabilities['location_gps'] = HardwareCapability(
            name="GPS Module",
            category="location",
            available=gps_available,
            confidence=0.0,
            interface="i2c",
            address="0x10 (conflicts with BNO055 - disabled)"
        )
        
        # LIDAR (USB)
        lidar_available = self._check_usb_device("10c4", "ea60")  # RPLIDAR
        self.capabilities['location_lidar'] = HardwareCapability(
            name="LIDAR Scanner",
            category="location",
            available=lidar_available,
            confidence=1.0 if lidar_available else 0.0,
            interface="usb",
            metadata={"range": "12m", "resolution": "360deg"}
        )
    
    def _discover_sensors(self):
        """Discover motion and orientation sensors."""
        self.logger.info("Scanning for motion sensors...")

        # BNO055 IMU (9-DOF sensor: accelerometer, gyroscope, magnetometer)
        bno055_available = self._check_i2c_device(0x28) or self._check_i2c_device(0x29)
        if not bno055_available:
            # Also check 0x10 (alternate address used by some BNO055 boards)
            bno055_available = self._check_i2c_device(0x10)

        self.capabilities['sensor_bno055'] = HardwareCapability(
            name="BNO055 9-DOF IMU",
            category="sensors",
            available=bno055_available,
            confidence=0.9 if bno055_available else 0.0,
            interface="i2c",
            address="0x28, 0x29, or 0x10",
            metadata={
                "accelerometer": True,
                "gyroscope": True,
                "magnetometer": True,
                "fusion": True  # Hardware sensor fusion
            }
        )

    def _discover_compute(self):
        """Discover AI acceleration hardware."""
        self.logger.info("Scanning for AI accelerators...")
        
        # Google Coral Edge TPU
        coral_available = self._check_usb_device("1a6e", "089a") or self._check_usb_device("18d1", "9302")
        self.capabilities['compute_coral'] = HardwareCapability(
            name="Google Coral Edge TPU",
            category="compute",
            available=coral_available,
            confidence=1.0 if coral_available else 0.0,
            interface="usb",
            metadata={"tops": 4}
        )
        
        # Raspberry Pi AI HAT
        ai_hat_available = self._check_pcie_device()
        self.capabilities['compute_ai_hat'] = HardwareCapability(
            name="Raspberry Pi AI HAT+",
            category="compute",
            available=ai_hat_available,
            confidence=0.7 if ai_hat_available else 0.0,
            interface="pcie",
            metadata={"tops": 26}
        )

    def _discover_arduino(self):
        """Discover Arduino boards."""
        self.logger.info("Scanning for Arduino...")

        arduino_available, arduino_path = self._check_arduino()
        self.capabilities['arduino'] = HardwareCapability(
            name="Arduino",
            category="controller",
            available=arduino_available,
            confidence=1.0 if arduino_available else 0.0,
            interface="usb",
            address=arduino_path,
            metadata={"mcu": "atmega328p"} # A common Arduino MCU
        )
    
    # Hardware detection methods
    
    def _check_camera(self) -> bool:
        """Check if camera is available."""
        try:
            result = subprocess.run(
                ["libcamera-hello", "--list-cameras"],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = "Available cameras" in result.stdout
            if available:
                self.logger.info("  ✓ RGB Camera detected")
            return available
        except:
            return False
    
    def _check_i2c_device(self, address: int) -> bool:
        """Check if I2C device exists at address."""
        try:
            result = subprocess.run(
                ["i2cdetect", "-y", "1"],
                capture_output=True,
                text=True,
                timeout=2
            )
            hex_addr = f"{address:02x}"
            available = hex_addr in result.stdout
            if available:
                self.logger.info(f"  ✓ I2C device at 0x{hex_addr}")
            return available
        except:
            return False
    
    def _check_usb_device(self, vendor_id: str, product_id: str) -> bool:
        """Check if USB device exists."""
        try:
            result = subprocess.run(
                ["lsusb"],
                capture_output=True,
                text=True,
                timeout=2
            )
            device_id = f"{vendor_id}:{product_id}"
            available = device_id in result.stdout
            if available:
                self.logger.info(f"  ✓ USB device {device_id}")
            return available
        except:
            return False
    
    def _check_spi_device(self) -> bool:
        """Check if SPI devices exist."""
        return os.path.exists("/dev/spidev0.0") or os.path.exists("/dev/spidev0.1")
    
    def _check_pcie_device(self) -> bool:
        """Check if Raspberry Pi AI HAT+ is installed."""
        try:
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                timeout=2
            )
            # AI HAT+ uses Hailo-8/8L neural processor
            # Look for "Hailo" in lspci output
            return "Hailo" in result.stdout or "Neural" in result.stdout
        except:
            return False
    
    def _check_audio_device(self) -> bool:
        """Check if audio input device exists."""
        try:
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return "card" in result.stdout
        except:
            return False

    def _check_arduino(self) -> (bool, Optional[str]):
        """Check if an Arduino is connected."""
        for device in ["/dev/ttyACM0", "/dev/ttyUSB0"]:
            if os.path.exists(device):
                self.logger.info(f"  ✓ Arduino detected at {device}")
                return True, device
        return False, None

    def _check_gpio_available(self) -> bool:
        """Check if GPIO interface is available (Raspberry Pi)."""
        # Check for GPIO sysfs interface
        if os.path.exists("/sys/class/gpio"):
            return True
        # Check for gpiochip devices
        if os.path.exists("/dev/gpiochip0"):
            return True
        # Check if we can import RPi.GPIO
        try:
            import RPi.GPIO
            return True
        except ImportError:
            pass
        # On any Raspberry Pi, assume GPIO is available
        return os.path.exists("/proc/device-tree/model")

    def get_capabilities_by_category(self, category: str) -> List[HardwareCapability]:
        """Get all available capabilities in a category."""
        return [
            cap for cap in self.capabilities.values()
            if cap.category == category and cap.available
        ]
    
    def has_capability(self, name: str) -> bool:
        """Check if a specific capability is available."""
        return name in self.capabilities and self.capabilities[name].available
    
    def get_capability_score(self) -> Dict[str, float]:
        """
        Calculate capability scores by category.
        
        Returns:
            Dictionary of category -> score (0.0-1.0)
        """
        categories = ["vision", "audio", "environment", "power", "communication", "location", "compute"]
        scores = {}
        
        for category in categories:
            caps = [c for c in self.capabilities.values() if c.category == category]
            if not caps:
                scores[category] = 0.0
            else:
                available = [c for c in caps if c.available]
                scores[category] = len(available) / len(caps)
        
        return scores
    
    def generate_report(self) -> str:
        """Generate a human-readable capability report."""
        report = []
        report.append("=" * 70)
        report.append("HARDWARE CAPABILITY REPORT")
        report.append("=" * 70)
        
        categories = ["vision", "audio", "environment", "power", "communication", "location", "compute"]
        
        for category in categories:
            caps = [c for c in self.capabilities.values() if c.category == category]
            available = [c for c in caps if c.available]
            
            report.append(f"\n{category.upper()}: {len(available)}/{len(caps)} available")
            
            for cap in caps:
                status = "✓" if cap.available else "✗"
                report.append(f"  {status} {cap.name}")
                if cap.available and cap.metadata:
                    for key, value in cap.metadata.items():
                        report.append(f"      {key}: {value}")
        
        report.append("\n" + "=" * 70)
        scores = self.get_capability_score()
        report.append("CAPABILITY SCORES")
        report.append("=" * 70)
        for category, score in scores.items():
            bar = "█" * int(score * 20)
            report.append(f"{category:15s} [{bar:20s}] {score:.0%}")
        
        report.append("=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test the discovery engine
    logging.basicConfig(level=logging.INFO)
    
    discovery = HardwareDiscovery()
    capabilities = discovery.discover_all()
    
    print(discovery.generate_report())

