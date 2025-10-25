#!/usr/bin/env python3
"""
Serial Port Manager - Production-Grade Port Locking

Prevents conflicts between peripherals (Flipper Zero, Arduino) accessing serial ports.

Features:
- Thread-safe exclusive locking
- Timeout-based acquisition
- Automatic cleanup on disconnect
- Support for both device paths and symlinks
- Context manager interface
"""

import threading
import time
import serial
import logging
from typing import Optional, Dict
from contextlib import contextmanager

logger = logging.getLogger("serial_port_manager")


class SerialPortLock:
    """Thread-safe lock for a single serial port."""

    def __init__(self, port: str):
        self.port = port
        self.lock = threading.Lock()
        self.owner = None  # Thread ID that owns the lock
        self.acquired_at = None
        self.connection = None  # Active serial.Serial connection

    def acquire(self, timeout: float = 5.0, owner: str = None) -> bool:
        """
        Acquire exclusive lock on this port.

        Args:
            timeout: Maximum time to wait for lock (seconds)
            owner: Identifier for the caller (thread name, peripheral name, etc.)

        Returns:
            True if lock acquired, False if timeout
        """
        acquired = self.lock.acquire(timeout=timeout)
        if acquired:
            self.owner = owner or threading.current_thread().name
            self.acquired_at = time.time()
            logger.debug(f"Lock acquired on {self.port} by {self.owner}")
        else:
            logger.warning(f"Failed to acquire lock on {self.port} (timeout={timeout}s)")
        return acquired

    def release(self):
        """Release the lock and close connection if open."""
        if self.connection:
            try:
                self.connection.close()
                logger.debug(f"Closed connection on {self.port}")
            except Exception as e:
                logger.error(f"Error closing connection on {self.port}: {e}")
            finally:
                self.connection = None

        if self.lock.locked():
            owner = self.owner
            self.owner = None
            self.acquired_at = None
            self.lock.release()
            logger.debug(f"Lock released on {self.port} (was owned by {owner})")

    def is_stale(self, max_age: float = 60.0) -> bool:
        """Check if lock has been held too long (potential deadlock)."""
        if self.acquired_at is None:
            return False
        age = time.time() - self.acquired_at
        return age > max_age


class SerialPortManager:
    """
    Production-grade serial port manager with exclusive locking.

    Prevents concurrent access to serial ports by multiple peripherals.
    Automatically handles cleanup and provides context manager interface.

    Example:
        manager = SerialPortManager()

        # Method 1: Context manager (recommended)
        with manager.acquire_port('/dev/flipper', 'FlipperZero') as port:
            port.write(b'status\\n')
            response = port.read(100)

        # Method 2: Manual acquire/release
        if manager.acquire('/dev/arduino_mega', 'Arduino'):
            try:
                port = manager.open('/dev/arduino_mega', 115200)
                port.write(b'discover\\n')
            finally:
                manager.release('/dev/arduino_mega')
    """

    def __init__(self):
        self.ports: Dict[str, SerialPortLock] = {}
        self.global_lock = threading.Lock()  # Protects ports dict

        # Deadlock detection
        self.check_interval = 30.0  # Check for stale locks every 30s
        self.max_lock_age = 60.0    # Force-release locks older than 60s
        self.monitor_thread = None
        self.running = False

        self._start_monitor()

    def _start_monitor(self):
        """Start background thread to detect and break deadlocks."""
        if self.monitor_thread is not None:
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_locks,
            daemon=True,
            name="SerialPortMonitor"
        )
        self.monitor_thread.start()
        logger.info("Serial port monitor started")

    def _monitor_locks(self):
        """Background task to detect and release stale locks."""
        while self.running:
            time.sleep(self.check_interval)

            with self.global_lock:
                for port_name, port_lock in self.ports.items():
                    if port_lock.is_stale(self.max_lock_age):
                        logger.warning(
                            f"Detected stale lock on {port_name} "
                            f"(owner: {port_lock.owner}, age: {time.time() - port_lock.acquired_at:.1f}s)"
                        )
                        logger.warning(f"Force-releasing stale lock on {port_name}")
                        port_lock.release()

    def _get_or_create_lock(self, port: str) -> SerialPortLock:
        """Get existing lock or create new one (thread-safe)."""
        with self.global_lock:
            if port not in self.ports:
                self.ports[port] = SerialPortLock(port)
            return self.ports[port]

    def acquire(self, port: str, owner: str = None, timeout: float = 5.0) -> bool:
        """
        Acquire exclusive lock on port.

        Args:
            port: Port path (e.g., '/dev/flipper', '/dev/ttyACM0')
            owner: Identifier for the caller
            timeout: Maximum time to wait for lock

        Returns:
            True if lock acquired, False otherwise
        """
        port_lock = self._get_or_create_lock(port)
        return port_lock.acquire(timeout=timeout, owner=owner)

    def release(self, port: str):
        """
        Release lock and close connection on port.

        Args:
            port: Port path
        """
        with self.global_lock:
            if port in self.ports:
                self.ports[port].release()

    def open(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 1.0,
        **kwargs
    ) -> Optional[serial.Serial]:
        """
        Open serial connection (lock must be acquired first).

        Args:
            port: Port path
            baudrate: Baud rate
            timeout: Read timeout
            **kwargs: Additional serial.Serial parameters

        Returns:
            serial.Serial object if successful, None otherwise
        """
        with self.global_lock:
            if port not in self.ports:
                logger.error(f"Cannot open {port}: lock not acquired")
                return None

            port_lock = self.ports[port]

            # Check if this thread owns the lock
            current_thread = threading.current_thread().name
            owner = kwargs.pop('owner', None)  # Remove owner from kwargs (not a serial.Serial parameter)
            if port_lock.owner != current_thread and port_lock.owner != owner:
                logger.error(
                    f"Cannot open {port}: owned by {port_lock.owner}, "
                    f"requested by {current_thread}"
                )
                return None

            # Close existing connection if any
            if port_lock.connection:
                try:
                    port_lock.connection.close()
                except:
                    pass

            # Open new connection
            try:
                port_lock.connection = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    timeout=timeout,
                    **kwargs
                )
                logger.info(f"Opened serial connection on {port} at {baudrate} baud")
                return port_lock.connection
            except serial.SerialException as e:
                logger.error(f"Failed to open {port}: {e}")
                return None

    @contextmanager
    def acquire_port(
        self,
        port: str,
        owner: str,
        baudrate: int = 115200,
        timeout: float = 5.0,
        **kwargs
    ):
        """
        Context manager for exclusive port access.

        Example:
            with manager.acquire_port('/dev/flipper', 'Flipper') as port:
                port.write(b'status\\n')
                response = port.read(100)

        Args:
            port: Port path
            owner: Identifier for the caller
            baudrate: Baud rate
            timeout: Lock acquisition timeout
            **kwargs: Additional serial.Serial parameters

        Yields:
            serial.Serial object
        """
        acquired = self.acquire(port, owner=owner, timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Failed to acquire lock on {port}")

        try:
            connection = self.open(port, baudrate=baudrate, owner=owner, **kwargs)
            if connection is None:
                raise IOError(f"Failed to open serial connection on {port}")

            yield connection
        finally:
            self.release(port)

    def list_locked_ports(self) -> Dict[str, str]:
        """
        Get list of currently locked ports.

        Returns:
            Dict mapping port paths to owner names
        """
        with self.global_lock:
            return {
                port: lock.owner
                for port, lock in self.ports.items()
                if lock.owner is not None
            }

    def force_release_all(self):
        """Force-release all locks (emergency use only)."""
        logger.warning("Force-releasing ALL serial port locks")
        with self.global_lock:
            for port_lock in self.ports.values():
                port_lock.release()

    def shutdown(self):
        """Gracefully shutdown the manager."""
        logger.info("Shutting down SerialPortManager")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.force_release_all()


# Global singleton instance
_manager_instance = None
_manager_lock = threading.Lock()


def get_serial_port_manager() -> SerialPortManager:
    """Get global SerialPortManager singleton."""
    global _manager_instance
    if _manager_instance is None:
        with _manager_lock:
            if _manager_instance is None:
                _manager_instance = SerialPortManager()
    return _manager_instance


# Convenience functions
def acquire_port(port: str, owner: str, timeout: float = 5.0) -> bool:
    """Acquire exclusive lock on port."""
    return get_serial_port_manager().acquire(port, owner, timeout)


def release_port(port: str):
    """Release lock on port."""
    get_serial_port_manager().release(port)


def open_port(port: str, baudrate: int = 115200, **kwargs) -> Optional[serial.Serial]:
    """Open serial connection (lock must be acquired first)."""
    return get_serial_port_manager().open(port, baudrate, **kwargs)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=== Serial Port Manager Test ===\n")

    manager = SerialPortManager()

    # Test 1: Context manager (recommended)
    print("Test 1: Context manager interface")
    try:
        with manager.acquire_port('/dev/ttyACM0', 'TestPeripheral', timeout=2.0) as port:
            print(f"  ✓ Acquired and opened /dev/ttyACM0")
            print(f"  Port: {port}")
    except (TimeoutError, IOError) as e:
        print(f"  ✗ {e}")

    print()

    # Test 2: Manual acquire/release
    print("Test 2: Manual acquire/release")
    if manager.acquire('/dev/ttyACM1', 'TestPeripheral2', timeout=2.0):
        print(f"  ✓ Acquired /dev/ttyACM1")
        port = manager.open('/dev/ttyACM1', 115200)
        print(f"  Port: {port}")
        manager.release('/dev/ttyACM1')
        print(f"  ✓ Released /dev/ttyACM1")
    else:
        print(f"  ✗ Failed to acquire /dev/ttyACM1")

    print()

    # Test 3: List locked ports
    print("Test 3: Currently locked ports")
    locked = manager.list_locked_ports()
    if locked:
        for port, owner in locked.items():
            print(f"  • {port}: {owner}")
    else:
        print("  (none)")

    print()
    print("✓ Serial Port Manager tests complete")

    manager.shutdown()
