#!/usr/bin/env python3
"""
Sentient Core - Adaptive Daemon Manager
Automatically creates and manages daemons based on discovered hardware.
"""

import logging
from typing import List, Dict, Type, Optional
from hardware_discovery import HardwareDiscovery, HardwareCapability
from world_state import WorldState
from daemon_base import BaseDaemon

class AdaptiveDaemonManager:
    """
    Intelligently spawns daemons based on available hardware.
    
    This is the key to adaptive AI - the system configures itself
    based on what it discovers, not what we tell it.
    """
    
    def __init__(self, world_state: WorldState):
        self.logger = logging.getLogger("adaptive_daemon_manager")
        self.world_state = world_state
        self.discovery = HardwareDiscovery()
        self.daemons: List[BaseDaemon] = []
        self.capabilities: Dict[str, HardwareCapability] = {}
    
    def discover_and_configure(self) -> List[BaseDaemon]:
        """
        Discover hardware and create appropriate daemons.
        
        Returns:
            List of configured daemons ready to start
        """
        self.logger.info("=" * 70)
        self.logger.info("ADAPTIVE DAEMON MANAGER")
        self.logger.info("=" * 70)
        
        # Step 1: Discover all hardware
        self.capabilities = self.discovery.discover_all()

        # Step 2: Print capability report
        print(self.discovery.generate_report())

        # Step 3: Debug - Show all detected capabilities
        self.logger.info("\n" + "=" * 70)
        self.logger.info("DETECTED CAPABILITIES (Debug)")
        self.logger.info("=" * 70)
        for cap_name, cap in self.capabilities.items():
            if cap.available:
                self.logger.info(f"  ✓ {cap_name}: {cap.name} @ {cap.interface} {cap.address or ''}")
        self.logger.info("=" * 70)

        # Step 4: Update WorldState with capabilities
        self._update_world_state_capabilities()

        # Step 5: Create daemons based on capabilities
        self._create_vision_daemons()
        self._create_audio_daemons()
        self._create_environment_daemons()
        self._create_power_daemons()
        self._create_communication_daemons()
        self._create_sensor_daemons()
        self._create_location_daemons()
        self._create_arduino_daemon()
        
        self.logger.info("=" * 70)
        self.logger.info(f"CONFIGURED {len(self.daemons)} DAEMONS")
        self.logger.info("=" * 70)
        
        return self.daemons
    
    def _create_vision_daemons(self):
        """Create vision daemons based on available cameras."""
        if self.discovery.has_capability('vision_daemon'):
            self.logger.info("Creating VisionDaemon (Object Detection & Tracking)")
            try:
                from daemons.vision_daemon import VisionDaemon
                daemon = VisionDaemon(self.world_state, update_rate=10.0)
                if daemon.initialize():
                    self.daemons.append(daemon)
                    self.logger.info("  ✓ Vision daemon configured (drone detection enabled)")
                else:
                    self.logger.error("  ✗ Vision daemon initialization failed")
            except ImportError as e:
                self.logger.warning(f"VisionDaemon not available: {e}")

        # if self.discovery.has_capability('camera_thermal'):
        #     self.logger.info("Creating ThermalDaemon (FLIR Lepton)")
        #     # Future: ThermalDaemon implementation
        #     self.logger.info("  (ThermalDaemon not yet implemented)")

        # if self.discovery.has_capability('camera_depth'):
        #     self.logger.info("Creating DepthDaemon (RealSense)")
        #     # Future: DepthDaemon implementation
        #     self.logger.info("  (DepthDaemon not yet implemented)")
    
    def _create_audio_daemons(self):
        """Create audio daemons based on available microphones."""
        # Audio Daemon - Create if any audio input is available
        if self.discovery.has_capability('microphone_array') or self.discovery.has_capability('audio_input'):
            audio_type = "ReSpeaker Array" if self.discovery.has_capability('microphone_array') else "Generic Input"
            self.logger.info(f"Creating AudioDaemon ({audio_type})")
            try:
                from daemons.audio_daemon import AudioDaemon
                daemon = AudioDaemon(self.world_state, update_rate=20.0)
                if daemon.initialize():
                    self.daemons.append(daemon)
                    self.logger.info("  ✓ Audio daemon configured (level monitoring + frequency analysis)")
                else:
                    self.logger.warning("  ⚠ Audio daemon not available (no input device or PyAudio)")
            except ImportError as e:
                self.logger.warning(f"AudioDaemon not available: {e}")
    
    def _create_environment_daemons(self):
        """Create environment daemons based on available sensors."""
        has_env_sensors = (
            self.discovery.has_capability('sensor_bme280') or
            self.discovery.has_capability('sensor_gas') or
            self.discovery.has_capability('sensor_light')
        )
        
        if has_env_sensors:
            self.logger.info("Creating EnvironmentDaemon")
            try:
                from daemons.environment_daemon import EnvironmentDaemon
                daemon = EnvironmentDaemon(self.world_state)
                if daemon.initialize():
                    self.daemons.append(daemon)
                else:
                    self.logger.error("  ✗ Environment daemon initialization failed")
            except ImportError as e:
                self.logger.warning(f"EnvironmentDaemon not available: {e}")
    
    def _create_power_daemons(self):
        """Create power management daemon if UPS available."""
        if self.discovery.has_capability('power_pijuice'):
            self.logger.info("Creating PowerDaemon (PiJuice)")
            try:
                from daemons.power_daemon import PowerDaemon
                daemon = PowerDaemon(self.world_state)
                if daemon.initialize():
                    self.daemons.append(daemon)
                else:
                    self.logger.error("  ✗ Power daemon initialization failed")
            except ImportError as e:
                self.logger.warning(f"PowerDaemon not available: {e}")
    
    def _create_communication_daemons(self):
        """Create communication daemons."""
        if self.discovery.has_capability('comm_flipper'):
            self.logger.info("Creating FlipperDaemon (RF Drone Defense)")
            try:
                from flipper_daemon import FlipperDaemon
                daemon = FlipperDaemon(self.world_state, update_rate=2.0)
                if daemon.initialize():
                    self.daemons.append(daemon)
                    self.logger.info("  ✓ Flipper Zero RF defense system configured")
                else:
                    self.logger.error("  ✗ Flipper daemon initialization failed")
            except ImportError as e:
                self.logger.warning(f"FlipperDaemon not available: {e}")

        # WiFi Scanner Daemon - Always attempt to create
        self.logger.info("Creating WiFiScannerDaemon (Network Detection)")
        try:
            from daemons.wifi_scanner_daemon import WiFiScannerDaemon
            daemon = WiFiScannerDaemon(self.world_state, update_rate=10.0)
            if daemon.initialize():
                self.daemons.append(daemon)
                self.logger.info("  ✓ WiFi scanner configured")
            else:
                self.logger.warning("  ⚠ WiFi scanner not available (no adapter/nmcli)")
        except ImportError as e:
            self.logger.warning(f"WiFiScannerDaemon not available: {e}")

        # Bluetooth Scanner Daemon - Always attempt to create
        self.logger.info("Creating BluetoothScannerDaemon (Device Detection)")
        try:
            from daemons.bluetooth_scanner_daemon import BluetoothScannerDaemon
            daemon = BluetoothScannerDaemon(self.world_state, update_rate=15.0)
            if daemon.initialize():
                self.daemons.append(daemon)
                self.logger.info("  ✓ Bluetooth scanner configured")
            else:
                self.logger.warning("  ⚠ Bluetooth scanner not available (no adapter/bluetoothctl)")
        except ImportError as e:
            self.logger.warning(f"BluetoothScannerDaemon not available: {e}")

        # if self.discovery.has_capability('comm_lora'):
        #     self.logger.info("Creating LoRaDaemon (Long-range Comms)")
        #     # Future: LoRaDaemon
        #     self.logger.info("  (LoRaDaemon not yet implemented)")

        # if self.discovery.has_capability('comm_lte'):
        #     self.logger.info("Creating LTEDaemon (Cellular)")
        #     # Future: LTEDaemon
        #     self.logger.info("  (LTEDaemon not yet implemented)")

    def _create_sensor_daemons(self):
        """Create sensor daemons for multi-sensor boards."""
        # BNO055 IMU Daemon - Create if sensor detected
        if self.discovery.has_capability('sensor_bno055'):
            self.logger.info("Creating IMUDaemon (BNO055 9-DOF Motion Sensor)")
            try:
                from daemons.imu_daemon import IMUDaemon
                daemon = IMUDaemon(self.world_state, update_rate=10.0)
                if daemon.initialize():
                    self.daemons.append(daemon)
                    self.logger.info("  ✓ IMU daemon configured (orientation + motion tracking)")
                else:
                    self.logger.warning("  ⚠ IMU daemon not available (sensor initialization failed)")
            except ImportError as e:
                self.logger.warning(f"IMUDaemon not available: {e}")

        # Hardware Monitor Daemon - Always create to enable hot-plug detection
        self.logger.info("Creating HardwareMonitorDaemon (Hot-Plug Detection)")
        try:
            from daemons.hardware_monitor_daemon import HardwareMonitorDaemon
            daemon = HardwareMonitorDaemon(
                self.world_state,
                daemon_manager=self,  # Pass self for daemon lifecycle management
                update_rate=5.0
            )
            if daemon.initialize():
                self.daemons.append(daemon)
                self.logger.info("  ✓ Hardware monitor configured (real-time device detection)")
            else:
                self.logger.error("  ✗ Hardware monitor initialization failed")
        except ImportError as e:
            self.logger.warning(f"HardwareMonitorDaemon not available: {e}")

        # if self.discovery.has_capability('sensor_prototype_board'):
        #     self.logger.info("Creating PrototypeBoardDaemon (Multi-Sensor GPIO Board)")
        #     try:
        #         from daemons.prototype_board_daemon import PrototypeBoardDaemon
        #         daemon = PrototypeBoardDaemon(self.world_state, update_rate=1.0)
        #         if daemon.initialize():
        #             self.daemons.append(daemon)
        #             self.logger.info("  ✓ Prototype sensor board configured (PIR + Mic + Environment)")
        #         else:
        #             self.logger.error("  ✗ Prototype board daemon initialization failed")
        #     except ImportError as e:
        #         self.logger.warning(f"PrototypeBoardDaemon not available: {e}")

    def _create_location_daemons(self):
        """Create location/navigation daemons."""
        # if self.discovery.has_capability('location_gps'):
        #     self.logger.info("Creating GPSDaemon")
        #     # Future: GPSDaemon
        #     self.logger.info("  (GPSDaemon not yet implemented)")
        # 
        # if self.discovery.has_capability('location_lidar'):
        #     self.logger.info("Creating LIDARDaemon")
        #     # Future: LIDARDaemon for 3D mapping
        #     self.logger.info("  (LIDARDaemon not yet implemented)")

    def _create_arduino_daemon(self):
        """Create Arduino daemon if an Arduino is detected."""
        if self.discovery.has_capability('arduino'):
            self.logger.info("Creating ArduinoDaemon")
            try:
                from arduino_daemon import ArduinoDaemon
                daemon = ArduinoDaemon(self.world_state, update_rate=1.0, debug=True)
                if daemon.initialize():
                    self.daemons.append(daemon)
                    self.logger.info("  ✓ Arduino daemon configured")
                else:
                    self.logger.error("  ✗ Arduino daemon initialization failed")
            except ImportError as e:
                self.logger.warning(f"ArduinoDaemon not available: {e}")
    
    def _update_world_state_capabilities(self):
        """Update WorldState with discovered capabilities."""
        capability_data = {
            "total_capabilities": len(self.capabilities),
            "available_capabilities": len([c for c in self.capabilities.values() if c.available]),
            "scores": self.discovery.get_capability_score(),
            "vision": self.discovery.has_capability('camera_rgb'),
            "vision_daemon": self.discovery.has_capability('vision_daemon'),
            "audio": self.discovery.has_capability('microphone_array') or self.discovery.has_capability('audio_input'),
            "environment": self.discovery.has_capability('sensor_bme280'),
            "power": self.discovery.has_capability('power_pijuice'),
            "ai_accelerator": self.discovery.has_capability('compute_coral') or self.discovery.has_capability('compute_ai_hat'),
            "rf_detection": self.discovery.has_capability('comm_flipper'),
            "thermal_vision": self.discovery.has_capability('camera_thermal'),
            "depth_vision": self.discovery.has_capability('camera_depth'),
            "gps": self.discovery.has_capability('location_gps'),
            "lidar": self.discovery.has_capability('location_lidar'),
            "prototype_board": self.discovery.has_capability('sensor_prototype_board'),
            "arduino": self.discovery.has_capability('arduino')
        }

        self.world_state.update("capabilities", capability_data)
        self.logger.info("WorldState updated with hardware capabilities")
    
    def get_daemons(self) -> List[BaseDaemon]:
        """Get list of configured daemons."""
        return self.daemons
    
    def get_capability_summary(self) -> Dict:
        """Get summary of system capabilities."""
        return {
            "total_daemons": len(self.daemons),
            "daemon_names": [d.daemon_name for d in self.daemons],
            "capabilities": self.discovery.get_capability_score(),
            "hardware_available": {
                name: cap.available
                for name, cap in self.capabilities.items()
            }
        }

    def get_daemon(self, name: str) -> Optional[BaseDaemon]:
        """Get a daemon by name."""
        for daemon in self.daemons:
            if daemon.daemon_name == name:
                return daemon
        return None

    def restart_daemon(self, name: str) -> bool:
        """Safely restart a daemon."""
        daemon = self.get_daemon(name)
        if daemon:
            self.logger.warning(f"Restarting daemon: {name}")
            daemon.stop()
            daemon.join(timeout=5)
            # Re-initialize the daemon for a clean restart (assuming BaseDaemon supports this)
            daemon.__init__(self.world_state) 
            daemon.start()
            return daemon.is_running()
        self.logger.error(f"Daemon not found: {name}")
        return False