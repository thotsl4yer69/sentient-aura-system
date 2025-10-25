#!/usr/bin/env python3
"""
Sentient Core - Base Daemon Class
Foundation for all sensor and hardware management daemons.
"""

import threading
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional

from world_state import WorldState


class BaseDaemon(ABC, threading.Thread):
    """
    Base class for all daemon threads.
    
    Each daemon is responsible for managing one aspect of the hardware
    (vision, audio, sensors, etc.) and continuously updating the WorldState.
    """
    
    def __init__(self, name: str, world_state: WorldState, update_rate: float):
        """
        Initialize the daemon.
        
        Args:
            name: Daemon name (e.g., 'visiond', 'audiod')
            world_state: Reference to the central WorldState
            update_rate: Update frequency in Hz
        """
        super().__init__(name=name, daemon=True)
        
        self.daemon_name = name
        self.world_state = world_state
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate if update_rate > 0 else 1.0
        
        self._stop_event = threading.Event()
        self._daemon_initialized = False
        self._error_count = 0
        self._max_errors = 10
        
        # Setup logging
        self.logger = logging.getLogger(name)
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize hardware and resources.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update(self) -> None:
        """
        Perform one update cycle.
        
        This method should:
        1. Read from hardware
        2. Process data
        3. Update the WorldState
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources before shutdown.
        """
        pass
    
    def run(self) -> None:
        """
        Main daemon loop (called by threading.Thread.start()).
        """
        self.logger.info(f"{self.daemon_name} starting...")
        
        # Initialize hardware
        try:
            self._daemon_initialized = self.initialize()
            if not self._daemon_initialized:
                self.logger.error(f"{self.daemon_name} initialization failed")
                return
        except Exception as e:
            self.logger.error(f"{self.daemon_name} initialization error: {e}")
            return
        
        self.logger.info(f"{self.daemon_name} initialized successfully")
        
        # Register with world state
        self.world_state.register_daemon(self.daemon_name)
        
        # Main loop
        while not self._stop_event.is_set():
            loop_start = time.time()
            
            try:
                self.update()
                self._error_count = 0  # Reset error count on success
                
            except Exception as e:
                self._error_count += 1
                self.logger.error(f"{self.daemon_name} update error: {e}")
                
                if self._error_count >= self._max_errors:
                    self.logger.critical(
                        f"{self.daemon_name} exceeded maximum errors, shutting down"
                    )
                    break
            
            # Sleep to maintain update rate
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.update_interval - elapsed)
            
            if sleep_time > 0:
                self._stop_event.wait(sleep_time)
        
        # Cleanup
        self.logger.info(f"{self.daemon_name} shutting down...")
        try:
            self.cleanup()
        except Exception as e:
            self.logger.error(f"{self.daemon_name} cleanup error: {e}")
        
        # Unregister from world state
        self.world_state.unregister_daemon(self.daemon_name)
        self.logger.info(f"{self.daemon_name} stopped")
    
    def stop(self) -> None:
        """Signal the daemon to stop."""
        self.logger.info(f"{self.daemon_name} stop requested")
        self._stop_event.set()
    
    def is_running(self) -> bool:
        """Check if daemon is running."""
        return self.is_alive() and not self._stop_event.is_set()
    
    def is_initialized(self) -> bool:
        """Check if daemon initialized successfully."""
        return self._daemon_initialized

