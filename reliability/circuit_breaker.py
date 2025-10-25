#!/usr/bin/env python3
"""
Circuit Breaker Pattern - Production Reliability

Protects critical components (Coral TPU, peripherals) from cascading failures
with automatic error recovery and exponential backoff.

States:
- CLOSED: Normal operation (all requests pass through)
- OPEN: Too many failures, requests fail fast without trying
- HALF_OPEN: Testing if service recovered

Features:
- Configurable failure threshold
- Exponential backoff
- Automatic recovery detection
- Thread-safe state management
- Comprehensive metrics
"""

import time
import threading
import logging
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("circuit_breaker")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"         # Normal operation
    OPEN = "open"             # Failing, reject requests
    HALF_OPEN = "half_open"   # Testing recovery


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0  # Calls rejected while OPEN
    state_changes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None


class CircuitBreaker:
    """
    Production circuit breaker for protecting critical operations.

    Example:
        # Create circuit breaker for Coral TPU operations
        coral_breaker = CircuitBreaker(
            name="CoralTPU",
            failure_threshold=3,
            recovery_timeout=30.0,
            expected_exception=RuntimeError
        )

        # Use with decorator
        @coral_breaker
        def coral_inference(data):
            return interpreter.invoke(data)

        # Or use directly
        try:
            result = coral_breaker.call(coral_inference, data)
        except CircuitBreakerOpen:
            logger.error("Coral TPU circuit open - using fallback")
            result = fallback_inference(data)
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for this circuit
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery (exponential backoff)
            expected_exception: Exception type that triggers circuit
            success_threshold: Number of successes in HALF_OPEN before closing circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.base_recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None
        self.backoff_multiplier = 1.0  # Exponential backoff multiplier

        self.lock = threading.Lock()
        self.metrics = CircuitBreakerMetrics()

        logger.info(
            f"Circuit breaker '{name}' initialized "
            f"(threshold={failure_threshold}, timeout={recovery_timeout}s)"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result if successful

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Original exception if call fails
        """
        with self.lock:
            self.metrics.total_calls += 1

            # Check current state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.metrics.rejected_calls += 1
                    raise CircuitBreakerOpen(
                        f"Circuit '{self.name}' is OPEN "
                        f"(next attempt in {self._time_until_retry():.1f}s)"
                    )

        # Execute the protected function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure(e)
            raise

    def _on_success(self):
        """Handle successful call."""
        with self.lock:
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info(
                    f"Circuit '{self.name}' HALF_OPEN success "
                    f"({self.success_count}/{self.success_threshold})"
                )

                if self.success_count >= self.success_threshold:
                    self._transition_to_closed()
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                if self.failure_count > 0:
                    logger.debug(f"Circuit '{self.name}' failure count reset")
                    self.failure_count = 0

    def _on_failure(self, exception: Exception):
        """Handle failed call."""
        with self.lock:
            self.failure_count += 1
            self.metrics.failed_calls += 1
            self.last_failure_time = time.time()
            self.metrics.last_failure_time = self.last_failure_time

            logger.warning(
                f"Circuit '{self.name}' failure "
                f"({self.failure_count}/{self.failure_threshold}): {exception}"
            )

            if self.state == CircuitState.HALF_OPEN:
                # Failed during recovery test - go back to OPEN
                logger.error(f"Circuit '{self.name}' recovery test failed")
                self._transition_to_open()
            elif self.failure_count >= self.failure_threshold:
                self._transition_to_open()

    def _transition_to_closed(self):
        """Transition to CLOSED state (normal operation)."""
        logger.info(f"Circuit '{self.name}' → CLOSED (recovered)")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.backoff_multiplier = 1.0  # Reset backoff
        self.metrics.state_changes += 1

    def _transition_to_open(self):
        """Transition to OPEN state (failing, reject calls)."""
        logger.error(
            f"Circuit '{self.name}' → OPEN "
            f"(threshold reached: {self.failure_count} failures)"
        )
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        self.success_count = 0

        # Exponential backoff: double the timeout each time
        self.backoff_multiplier = min(self.backoff_multiplier * 2, 16.0)  # Cap at 16x

        self.metrics.state_changes += 1

        logger.info(
            f"Circuit '{self.name}' will attempt recovery in "
            f"{self._get_recovery_timeout():.1f}s (backoff: {self.backoff_multiplier}x)"
        )

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state (testing recovery)."""
        logger.info(f"Circuit '{self.name}' → HALF_OPEN (testing recovery)")
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.metrics.state_changes += 1

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.opened_at is None:
            return False

        elapsed = time.time() - self.opened_at
        recovery_timeout = self._get_recovery_timeout()
        return elapsed >= recovery_timeout

    def _get_recovery_timeout(self) -> float:
        """Get current recovery timeout with exponential backoff."""
        return self.base_recovery_timeout * self.backoff_multiplier

    def _time_until_retry(self) -> float:
        """Get time remaining until next retry attempt."""
        if self.opened_at is None:
            return 0.0

        elapsed = time.time() - self.opened_at
        recovery_timeout = self._get_recovery_timeout()
        return max(0.0, recovery_timeout - elapsed)

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics."""
        return self.metrics

    def reset(self):
        """Manually reset circuit to CLOSED state."""
        with self.lock:
            logger.info(f"Circuit '{self.name}' manually reset to CLOSED")
            self._transition_to_closed()

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator interface for circuit breaker.

        Example:
            @circuit_breaker
            def protected_function():
                return risky_operation()
        """
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper

    def __str__(self) -> str:
        """String representation of circuit breaker state."""
        return (
            f"CircuitBreaker(name='{self.name}', "
            f"state={self.state.value}, "
            f"failures={self.failure_count}/{self.failure_threshold}, "
            f"successes={self.metrics.successful_calls}, "
            f"rejected={self.metrics.rejected_calls})"
        )


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=== Circuit Breaker Test ===\n")

    # Create circuit breaker
    breaker = CircuitBreaker(
        name="TestService",
        failure_threshold=3,
        recovery_timeout=5.0
    )

    # Test function that fails sometimes
    call_count = 0
    def unreliable_function():
        global call_count
        call_count += 1
        if call_count <= 4:
            raise RuntimeError(f"Simulated failure #{call_count}")
        return f"Success (call #{call_count})"

    # Test 1: Trigger circuit to open
    print("Test 1: Trigger circuit to open (3 failures)")
    for i in range(5):
        try:
            result = breaker.call(unreliable_function)
            print(f"  Call {i+1}: {result}")
        except CircuitBreakerOpen as e:
            print(f"  Call {i+1}: REJECTED - {e}")
        except RuntimeError as e:
            print(f"  Call {i+1}: FAILED - {e}")
        time.sleep(0.5)

    print(f"\n{breaker}\n")

    # Test 2: Wait for recovery
    print("Test 2: Wait for recovery timeout (5s)...")
    time.sleep(5.5)

    # Test 3: Circuit should be HALF_OPEN, allow recovery
    print("\nTest 3: Recovery attempt (should succeed)")
    for i in range(3):
        try:
            result = breaker.call(unreliable_function)
            print(f"  Recovery call {i+1}: {result}")
        except Exception as e:
            print(f"  Recovery call {i+1}: {e}")
        time.sleep(0.5)

    print(f"\n{breaker}\n")

    # Show final metrics
    metrics = breaker.get_metrics()
    print("Final Metrics:")
    print(f"  Total calls: {metrics.total_calls}")
    print(f"  Successful: {metrics.successful_calls}")
    print(f"  Failed: {metrics.failed_calls}")
    print(f"  Rejected: {metrics.rejected_calls}")
    print(f"  State changes: {metrics.state_changes}")
    print()

    print("✓ Circuit Breaker tests complete")
