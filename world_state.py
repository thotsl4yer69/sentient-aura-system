#!/usr/bin/env python3
"""
Sentient Core - World State
Thread-safe central data structure holding all sensor data and system state.
"""

import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional
from collections import deque
import copy

from sentient_aura.config import MAX_HISTORY_SIZE, WORLD_STATE_TTL


class WorldState:
    """
    Thread-safe world state manager.
    
    This is the central nervous system of the Sentient Core. All sensor data
    flows into this structure, and the consciousness loop reads from it.
    """
    
    def __init__(self):
        """Initialize the world state with default values."""
        self._lock = threading.RLock()
        self._state = {
            "timestamp": time.time(),
            "system": {
                "name": "Sentient Core v3.2",
                "uptime": 0,
                "status": "initializing",
                "active_daemons": []
            },
            "location": {
                "latitude": None,
                "longitude": None,
                "altitude": None,
                "fix_quality": 0,
                "satellites": 0
            },
            "vision": {
                "rgb_frame": None,
                "frame_timestamp": None,
                "detected_objects": [],
                "motion_detected": False,
                "motion_contours": [],
                "faces_detected": []
            },
            "audio": {
                "ambient_noise_level": 0.0,
                "last_keyword_spotted": None,
                "last_command": None,
                "sound_direction": None,
                "is_listening": False
            },
            "environment": {
                "temperature": None,
                "humidity": None,
                "pressure": None,
                "gas_resistance": None,
                "oxidising": None,
                "reducing": None,
                "nh3": None,
                "light_level": None,
                "proximity": None
            },
            "power": {
                "battery_charge": None,
                "battery_voltage": None,
                "is_charging": False,
                "power_input_present": False,
                "status": "unknown",
                "estimated_runtime": None
            },
            "ai": {
                "current_models": [],
                "inference_count": 0,
                "average_inference_time": 0.0,
                "last_inference": None
            },
            "decisions": {
                "last_action": None,
                "last_action_timestamp": None,
                "active_goals": [],
                "alerts": []
            }
        }
        
        # Historical data buffers
        self._history = {
            "temperature": deque(maxlen=MAX_HISTORY_SIZE),
            "humidity": deque(maxlen=MAX_HISTORY_SIZE),
            "pressure": deque(maxlen=MAX_HISTORY_SIZE),
            "battery_charge": deque(maxlen=MAX_HISTORY_SIZE),
            "motion_events": deque(maxlen=MAX_HISTORY_SIZE),
            "object_detections": deque(maxlen=MAX_HISTORY_SIZE),
            "voice_commands": deque(maxlen=MAX_HISTORY_SIZE)
        }
        
        self._start_time = time.time()
    
    def update(self, category: str, data: Dict[str, Any]) -> None:
        """
        Update a category of the world state.
        
        Args:
            category: The top-level category (e.g., 'vision', 'audio')
            data: Dictionary of values to update
        """
        with self._lock:
            if category not in self._state:
                self._state[category] = {}
            
            self._state[category].update(data)
            self._state["timestamp"] = time.time()
            
            # Update system uptime
            self._state["system"]["uptime"] = time.time() - self._start_time

    def update_nested(self, path: str, value: Any) -> None:
        """
        Update a nested key in the world state.

        Args:
            path: Dot-separated path to the key (e.g., 'arduino.peripherals.led')
            value: The value to set
        """
        with self._lock:
            keys = path.split('.')
            current_level = self._state
            for key in keys[:-1]:
                if key not in current_level:
                    current_level[key] = {}
                current_level = current_level[key]
            current_level[keys[-1]] = value
            self._state["timestamp"] = time.time()

    def get_nested(self, path: str) -> Any:
        """
        Get a nested value from the world state.

        Args:
            path: Dot-separated path to the key (e.g., 'arduino.peripherals.led.value')

        Returns:
            The value at the path, or None if not found
        """
        with self._lock:
            keys = path.split('.')
            current_level = self._state
            for key in keys:
                if isinstance(current_level, dict) and key in current_level:
                    current_level = current_level[key]
                else:
                    return None
            return copy.deepcopy(current_level)

    def get(self, category: Optional[str] = None, key: Optional[str] = None) -> Any:
        """
        Get data from the world state.
        
        Args:
            category: The category to retrieve (None = entire state)
            key: Specific key within category (None = entire category)
            
        Returns:
            The requested data
        """
        with self._lock:
            if category is None:
                return copy.deepcopy(self._state)
            
            if category not in self._state:
                return None
            
            if key is None:
                return copy.deepcopy(self._state[category])
            
            return copy.deepcopy(self._state[category].get(key))
    
    def get_snapshot(self) -> Dict[str, Any]:
        """
        Get a complete, thread-safe snapshot of the current world state.
        
        Returns:
            Deep copy of the entire state
        """
        with self._lock:
            return copy.deepcopy(self._state)
    
    def add_to_history(self, buffer_name: str, data: Any) -> None:
        """
        Add data to a historical buffer.
        
        Args:
            buffer_name: Name of the history buffer
            data: Data to append (will be timestamped)
        """
        with self._lock:
            if buffer_name in self._history:
                self._history[buffer_name].append({
                    "timestamp": time.time(),
                    "data": data
                })
    
    def get_history(self, buffer_name: str, limit: Optional[int] = None) -> list:
        """
        Get historical data from a buffer.
        
        Args:
            buffer_name: Name of the history buffer
            limit: Maximum number of recent entries to return
            
        Returns:
            List of historical entries
        """
        with self._lock:
            if buffer_name not in self._history:
                return []
            
            history = list(self._history[buffer_name])
            
            if limit:
                return history[-limit:]
            
            return history
    
    def register_daemon(self, daemon_name: str) -> None:
        """Register a daemon as active."""
        with self._lock:
            if daemon_name not in self._state["system"]["active_daemons"]:
                self._state["system"]["active_daemons"].append(daemon_name)
    
    def unregister_daemon(self, daemon_name: str) -> None:
        """Unregister a daemon."""
        with self._lock:
            if daemon_name in self._state["system"]["active_daemons"]:
                self._state["system"]["active_daemons"].remove(daemon_name)
    
    def set_system_status(self, status: str) -> None:
        """Set the overall system status."""
        with self._lock:
            self._state["system"]["status"] = status
            self._state["timestamp"] = time.time()
    
    def add_alert(self, alert_type: str, message: str, severity: str = "info") -> None:
        """
        Add an alert to the decision queue.
        
        Args:
            alert_type: Type of alert (e.g., 'motion', 'low_battery')
            message: Human-readable alert message
            severity: 'info', 'warning', 'critical'
        """
        with self._lock:
            alert = {
                "type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": time.time()
            }
            self._state["decisions"]["alerts"].append(alert)
            
            # Keep only last 100 alerts
            if len(self._state["decisions"]["alerts"]) > 100:
                self._state["decisions"]["alerts"] = self._state["decisions"]["alerts"][-100:]
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 10) -> list:
        """
        Get recent alerts.
        
        Args:
            severity: Filter by severity level
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        with self._lock:
            alerts = self._state["decisions"]["alerts"]
            
            if severity:
                alerts = [a for a in alerts if a["severity"] == severity]
            
            return alerts[-limit:]
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        with self._lock:
            self._state["decisions"]["alerts"] = []
    
    def __repr__(self) -> str:
        """String representation of the world state."""
        with self._lock:
            return (
                f"WorldState(timestamp={self._state['timestamp']}, "
                f"status={self._state['system']['status']}, "
                f"active_daemons={len(self._state['system']['active_daemons'])})"
            )

