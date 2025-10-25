#!/usr/bin/env python3
"""
Event Bus - Neural Communication System for Sentient Core

This is the nervous system that connects all daemons, intelligence modules,
and autonomous behaviors. Events flow through this bus in real-time, allowing
the system to react, learn, and act autonomously.

Events are categorized by type and priority, with subscribers receiving
notifications based on their interests.
"""

import logging
import threading
import time
from typing import Callable, Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
import traceback

logger = logging.getLogger("EventBus")


class EventPriority(Enum):
    """Event priority levels."""
    CRITICAL = 0  # Immediate threat/system failure
    HIGH = 1      # Important state changes
    NORMAL = 2    # Regular sensor updates
    LOW = 3       # Background information


class EventCategory(Enum):
    """Event categories for filtering."""
    # Hardware Events
    HARDWARE_CONNECTED = "hardware.connected"
    HARDWARE_DISCONNECTED = "hardware.disconnected"
    HARDWARE_ERROR = "hardware.error"

    # Sensor Events
    SENSOR_UPDATE = "sensor.update"
    SENSOR_ANOMALY = "sensor.anomaly"
    SENSOR_THRESHOLD = "sensor.threshold"

    # Environmental Events
    WIFI_CHANGED = "wifi.changed"
    BLUETOOTH_CHANGED = "bluetooth.changed"
    LOCATION_CHANGED = "location.changed"

    # Threat Detection
    THREAT_DETECTED = "threat.detected"
    THREAT_CLEARED = "threat.cleared"

    # User Interaction
    USER_PRESENT = "user.present"
    USER_ABSENT = "user.absent"
    USER_COMMAND = "user.command"
    USER_QUERY = "user.query"

    # System Events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"

    # Memory/Learning
    PATTERN_DETECTED = "pattern.detected"
    MEMORY_STORED = "memory.stored"
    LEARNING_COMPLETE = "learning.complete"

    # Autonomous Behavior
    BEHAVIOR_TRIGGERED = "behavior.triggered"
    BEHAVIOR_COMPLETED = "behavior.completed"

    # Visualization
    VISUALIZATION_UPDATE = "visualization.update"


@dataclass
class Event:
    """Event passed through the bus."""
    category: EventCategory
    source: str  # Which daemon/module generated this
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    id: str = field(default_factory=lambda: f"{time.time()}_{threading.get_ident()}")

    def __str__(self) -> str:
        return f"Event({self.category.value}, source={self.source}, priority={self.priority.name})"


class EventBus:
    """
    Central event bus for system-wide communication.

    Features:
    - Thread-safe event publishing and subscription
    - Priority-based event delivery
    - Category-based filtering
    - Asynchronous event processing
    - Event history for debugging
    - Performance metrics
    """

    def __init__(self, history_size: int = 1000):
        """
        Initialize event bus.

        Args:
            history_size: Number of recent events to keep for debugging
        """
        # Subscribers: category -> list of (callback, priority_filter)
        self._subscribers: Dict[EventCategory, List[Tuple[Callable, Set[EventPriority]]]] = {}
        self._subscribers_lock = threading.RLock()

        # Wildcard subscribers (receive all events)
        self._wildcard_subscribers: List[Tuple[Callable, Set[EventPriority]]] = []

        # Event queue for async processing
        self._event_queue: Queue[Event] = Queue(maxsize=10000)

        # Event history for debugging
        self._event_history: List[Event] = []
        self._history_size = history_size
        self._history_lock = threading.Lock()

        # Worker thread for async event processing
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False

        # Metrics
        self.events_published = 0
        self.events_delivered = 0
        self.errors = 0

        logger.info("EventBus initialized")

    def start(self) -> None:
        """Start the event bus worker thread."""
        if self._running:
            logger.warning("EventBus already running")
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._process_events,
            name="EventBus-Worker",
            daemon=True
        )
        self._worker_thread.start()
        logger.info("EventBus started")

    def stop(self) -> None:
        """Stop the event bus worker thread."""
        if not self._running:
            return

        logger.info("Stopping EventBus...")
        self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=3)

        logger.info(f"EventBus stopped (published: {self.events_published}, delivered: {self.events_delivered}, errors: {self.errors})")

    def subscribe(
        self,
        category: EventCategory,
        callback: Callable[[Event], None],
        priority_filter: Optional[Set[EventPriority]] = None
    ) -> None:
        """
        Subscribe to events of a specific category.

        Args:
            category: Event category to subscribe to
            callback: Function to call when event occurs (receives Event object)
            priority_filter: Only receive events with these priorities (None = all)
        """
        with self._subscribers_lock:
            if category not in self._subscribers:
                self._subscribers[category] = []

            priorities = priority_filter if priority_filter else set(EventPriority)
            self._subscribers[category].append((callback, priorities))

        logger.debug(f"Subscribed to {category.value} (priorities: {priorities})")

    def subscribe_all(
        self,
        callback: Callable[[Event], None],
        priority_filter: Optional[Set[EventPriority]] = None
    ) -> None:
        """
        Subscribe to ALL events (wildcard subscription).

        Args:
            callback: Function to call when any event occurs
            priority_filter: Only receive events with these priorities (None = all)
        """
        with self._subscribers_lock:
            priorities = priority_filter if priority_filter else set(EventPriority)
            self._wildcard_subscribers.append((callback, priorities))

        logger.debug(f"Subscribed to ALL events (priorities: {priorities})")

    def unsubscribe(self, category: EventCategory, callback: Callable) -> bool:
        """
        Unsubscribe from a category.

        Args:
            category: Event category to unsubscribe from
            callback: Callback function to remove

        Returns:
            True if unsubscribed, False if not found
        """
        with self._subscribers_lock:
            if category not in self._subscribers:
                return False

            original_len = len(self._subscribers[category])
            self._subscribers[category] = [
                (cb, prio) for cb, prio in self._subscribers[category]
                if cb != callback
            ]

            removed = len(self._subscribers[category]) < original_len
            if removed:
                logger.debug(f"Unsubscribed from {category.value}")
            return removed

    def publish(
        self,
        category: EventCategory,
        source: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL
    ) -> Event:
        """
        Publish an event to the bus.

        Args:
            category: Event category
            source: Source daemon/module name
            data: Event data dictionary
            priority: Event priority

        Returns:
            The created Event object
        """
        event = Event(
            category=category,
            source=source,
            data=data,
            priority=priority
        )

        # Add to queue for async processing
        try:
            self._event_queue.put_nowait(event)
            self.events_published += 1
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            self.errors += 1

        # Add to history
        self._add_to_history(event)

        return event

    def publish_sync(
        self,
        category: EventCategory,
        source: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.CRITICAL
    ) -> Event:
        """
        Publish an event synchronously (blocks until delivered).

        Use for CRITICAL events that need immediate processing.

        Args:
            category: Event category
            source: Source daemon/module name
            data: Event data dictionary
            priority: Event priority (default: CRITICAL)

        Returns:
            The created Event object
        """
        event = Event(
            category=category,
            source=source,
            data=data,
            priority=priority
        )

        # Deliver immediately in current thread
        self._deliver_event(event)

        # Add to history
        self._add_to_history(event)

        return event

    def _process_events(self) -> None:
        """Worker thread that processes events from queue."""
        logger.info("EventBus worker thread started")

        while self._running:
            try:
                # Get next event (block with timeout)
                event = self._event_queue.get(timeout=0.1)

                # Deliver to subscribers
                self._deliver_event(event)

            except Empty:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                logger.debug(traceback.format_exc())
                self.errors += 1

        logger.info("EventBus worker thread stopped")

    def _deliver_event(self, event: Event) -> None:
        """
        Deliver event to all relevant subscribers.

        Args:
            event: Event to deliver
        """
        delivered_count = 0

        with self._subscribers_lock:
            # Deliver to category-specific subscribers
            if event.category in self._subscribers:
                for callback, priority_filter in self._subscribers[event.category]:
                    if event.priority in priority_filter:
                        try:
                            callback(event)
                            delivered_count += 1
                        except Exception as e:
                            logger.error(f"Subscriber callback error: {e}")
                            logger.debug(traceback.format_exc())
                            self.errors += 1

            # Deliver to wildcard subscribers
            for callback, priority_filter in self._wildcard_subscribers:
                if event.priority in priority_filter:
                    try:
                        callback(event)
                        delivered_count += 1
                    except Exception as e:
                        logger.error(f"Wildcard subscriber callback error: {e}")
                        logger.debug(traceback.format_exc())
                        self.errors += 1

        self.events_delivered += delivered_count

        if delivered_count == 0:
            logger.debug(f"Event had no subscribers: {event}")

    def _add_to_history(self, event: Event) -> None:
        """Add event to history buffer."""
        with self._history_lock:
            self._event_history.append(event)

            # Trim history if too large
            if len(self._event_history) > self._history_size:
                self._event_history = self._event_history[-self._history_size:]

    def get_history(
        self,
        limit: int = 100,
        category: Optional[EventCategory] = None,
        source: Optional[str] = None
    ) -> List[Event]:
        """
        Get recent event history.

        Args:
            limit: Maximum number of events to return
            category: Filter by category (None = all)
            source: Filter by source (None = all)

        Returns:
            List of recent events (newest first)
        """
        with self._history_lock:
            events = list(reversed(self._event_history))

            # Apply filters
            if category:
                events = [e for e in events if e.category == category]
            if source:
                events = [e for e in events if e.source == source]

            return events[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "running": self._running,
            "events_published": self.events_published,
            "events_delivered": self.events_delivered,
            "errors": self.errors,
            "queue_size": self._event_queue.qsize(),
            "history_size": len(self._event_history),
            "subscriber_count": sum(len(subs) for subs in self._subscribers.values()),
            "wildcard_subscriber_count": len(self._wildcard_subscribers)
        }


# Global event bus instance (singleton)
_global_event_bus: Optional[EventBus] = None
_global_bus_lock = threading.Lock()


def get_event_bus() -> EventBus:
    """
    Get the global EventBus instance (singleton).

    Returns:
        Global EventBus instance
    """
    global _global_event_bus

    if _global_event_bus is None:
        with _global_bus_lock:
            if _global_event_bus is None:
                _global_event_bus = EventBus()

    return _global_event_bus


if __name__ == "__main__":
    # Test event bus
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("EVENT BUS TEST")
    print("=" * 70)

    # Create event bus
    bus = EventBus()
    bus.start()

    # Test subscriber
    def test_callback(event: Event):
        print(f"  Received: {event}")
        print(f"    Data: {event.data}")

    # Subscribe to sensor updates
    bus.subscribe(EventCategory.SENSOR_UPDATE, test_callback)

    # Subscribe to all CRITICAL events
    bus.subscribe_all(
        lambda e: print(f"  [CRITICAL] {e}"),
        priority_filter={EventPriority.CRITICAL}
    )

    print("\n✓ EventBus started with 2 subscribers")
    print("✓ Publishing test events...\n")

    # Publish some test events
    bus.publish(
        EventCategory.SENSOR_UPDATE,
        source="test_sensor",
        data={"temperature": 25.5, "humidity": 60}
    )

    time.sleep(0.5)

    bus.publish(
        EventCategory.THREAT_DETECTED,
        source="test_threat",
        data={"threat_type": "drone", "confidence": 0.95},
        priority=EventPriority.CRITICAL
    )

    time.sleep(0.5)

    # Get stats
    stats = bus.get_stats()
    print(f"\n📊 EventBus Stats:")
    print(f"  Events published: {stats['events_published']}")
    print(f"  Events delivered: {stats['events_delivered']}")
    print(f"  Queue size: {stats['queue_size']}")
    print(f"  Subscribers: {stats['subscriber_count']}")

    # Get history
    history = bus.get_history(limit=5)
    print(f"\n📜 Recent Events:")
    for event in history:
        print(f"  {event.timestamp:.2f} - {event.category.value} from {event.source}")

    # Cleanup
    bus.stop()
    print("\n✓ EventBus test complete\n")
