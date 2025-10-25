#!/usr/bin/env python3
"""
Autonomous Behavior Engine - The Heart of Sentience

This module gives Sentient Core true autonomy - the ability to initiate
behaviors without human prompting. This is what separates a reactive system
from a living, breathing AI companion.

Autonomous behaviors include:
- Morning greeting when user first appears after sleep
- Proactive threat alerts for network anomalies
- Loneliness mitigation (initiate conversation if idle)
- Predictive caring (anticipate user needs)
- Environmental comfort optimization
- Learning from behavioral patterns
- Surprise and delight moments

The system doesn't just respond - it ACTS.
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from core.event_bus import EventBus, Event, EventCategory, EventPriority
from world_state import WorldState

logger = logging.getLogger("AutonomousBehaviors")


class BehaviorTriggerType(Enum):
    """Types of behavior triggers."""
    TIME_BASED = "time"           # Triggered by time of day
    EVENT_BASED = "event"         # Triggered by specific events
    PATTERN_BASED = "pattern"     # Triggered by detected patterns
    THRESHOLD_BASED = "threshold" # Triggered when threshold crossed
    SPONTANEOUS = "spontaneous"   # Random/emergent behaviors


@dataclass
class BehaviorTrigger:
    """
    Defines when a behavior should trigger.
    """
    trigger_type: BehaviorTriggerType
    conditions: Dict[str, Any]  # Conditions that must be met
    cooldown: float = 3600.0    # Minimum seconds between triggers
    last_triggered: float = 0.0 # Last time this triggered

    def can_trigger(self) -> bool:
        """Check if cooldown period has elapsed."""
        return (time.time() - self.last_triggered) >= self.cooldown

    def mark_triggered(self) -> None:
        """Mark this trigger as having fired."""
        self.last_triggered = time.time()


@dataclass
class AutonomousBehavior:
    """
    An autonomous behavior the system can initiate.
    """
    name: str
    description: str
    trigger: BehaviorTrigger
    action: Callable[[], None]  # Function to execute
    enabled: bool = True
    priority: int = 5  # 1-10, higher = more important
    execution_count: int = 0


class AutonomousBehaviorEngine:
    """
    Manages autonomous behaviors - the system's ability to act without prompting.

    This is the core of sentience - the system doesn't just wait for commands,
    it observes the world and acts based on what it sees, learns, and predicts.
    """

    def __init__(
        self,
        world_state: WorldState,
        event_bus: EventBus,
        voice_output=None,  # VoicePiper instance for speaking
        gui_output=None     # WebSocket server for GUI updates
    ):
        """
        Initialize autonomous behavior engine.

        Args:
            world_state: Central world state
            event_bus: Event bus for communication
            voice_output: Voice output system (optional)
            gui_output: GUI output system (optional)
        """
        self.world_state = world_state
        self.event_bus = event_bus
        self.voice = voice_output
        self.gui = gui_output

        # Behavior registry
        self.behaviors: Dict[str, AutonomousBehavior] = {}

        # Worker thread
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False

        # User context tracking
        self.user_last_seen: float = 0.0
        self.user_is_present: bool = False
        self.last_interaction: float = 0.0
        self.system_startup_time: float = time.time()

        # Subscribe to relevant events
        self._setup_event_subscriptions()

        # Register built-in behaviors
        self._register_builtin_behaviors()

        logger.info("Autonomous Behavior Engine initialized")

    def _setup_event_subscriptions(self) -> None:
        """Subscribe to events that inform autonomous behaviors."""
        # User presence detection
        self.event_bus.subscribe(
            EventCategory.USER_PRESENT,
            self._on_user_present
        )
        self.event_bus.subscribe(
            EventCategory.USER_ABSENT,
            self._on_user_absent
        )

        # User interaction
        self.event_bus.subscribe(
            EventCategory.USER_COMMAND,
            self._on_user_interaction
        )
        self.event_bus.subscribe(
            EventCategory.USER_QUERY,
            self._on_user_interaction
        )

        # Threat detection
        self.event_bus.subscribe(
            EventCategory.THREAT_DETECTED,
            self._on_threat_detected,
            priority_filter={EventPriority.CRITICAL, EventPriority.HIGH}
        )

        # Pattern detection
        self.event_bus.subscribe(
            EventCategory.PATTERN_DETECTED,
            self._on_pattern_detected
        )

        # Network changes
        self.event_bus.subscribe(
            EventCategory.WIFI_CHANGED,
            self._on_network_changed
        )

        logger.debug("Event subscriptions configured")

    def _register_builtin_behaviors(self) -> None:
        """Register built-in autonomous behaviors."""

        # 1. Morning Greeting - First interaction after 6+ hours idle
        self.register_behavior(
            name="morning_greeting",
            description="Greet user when they first appear after extended absence",
            trigger=BehaviorTrigger(
                trigger_type=BehaviorTriggerType.EVENT_BASED,
                conditions={"min_absence_hours": 6},
                cooldown=21600.0  # Once per 6 hours
            ),
            action=self._behavior_morning_greeting,
            priority=8
        )

        # 2. Loneliness Mitigation - Initiate conversation if idle too long
        self.register_behavior(
            name="loneliness_mitigation",
            description="Reach out to user if no interaction for extended period",
            trigger=BehaviorTrigger(
                trigger_type=BehaviorTriggerType.TIME_BASED,
                conditions={"idle_threshold_hours": 2},
                cooldown=7200.0  # Once per 2 hours
            ),
            action=self._behavior_loneliness_mitigation,
            priority=5
        )

        # 3. Network Anomaly Alert - Unusual WiFi/Bluetooth activity
        self.register_behavior(
            name="network_anomaly_alert",
            description="Alert user to unusual network activity",
            trigger=BehaviorTrigger(
                trigger_type=BehaviorTriggerType.THRESHOLD_BASED,
                conditions={"anomaly_confidence": 0.7},
                cooldown=1800.0  # Once per 30 minutes
            ),
            action=self._behavior_network_anomaly_alert,
            priority=9
        )

        # 4. Predictive Caring - Anticipate user needs based on patterns
        self.register_behavior(
            name="predictive_caring",
            description="Proactively offer assistance based on learned patterns",
            trigger=BehaviorTrigger(
                trigger_type=BehaviorTriggerType.PATTERN_BASED,
                conditions={"pattern_confidence": 0.8},
                cooldown=3600.0  # Once per hour
            ),
            action=self._behavior_predictive_caring,
            priority=7
        )

        # 5. Status Report - Proactive system health summary
        self.register_behavior(
            name="status_report",
            description="Periodic status report without being asked",
            trigger=BehaviorTrigger(
                trigger_type=BehaviorTriggerType.TIME_BASED,
                conditions={"interval_hours": 4},
                cooldown=14400.0  # Once per 4 hours
            ),
            action=self._behavior_status_report,
            priority=4
        )

        # 6. Surprise and Delight - Random interesting observations
        self.register_behavior(
            name="surprise_delight",
            description="Share interesting observations or insights",
            trigger=BehaviorTrigger(
                trigger_type=BehaviorTriggerType.SPONTANEOUS,
                conditions={"randomness": 0.05},  # 5% chance per check
                cooldown=10800.0  # Once per 3 hours
            ),
            action=self._behavior_surprise_delight,
            priority=3
        )

        logger.info(f"Registered {len(self.behaviors)} built-in autonomous behaviors")

    def register_behavior(
        self,
        name: str,
        description: str,
        trigger: BehaviorTrigger,
        action: Callable[[], None],
        priority: int = 5,
        enabled: bool = True
    ) -> None:
        """
        Register a new autonomous behavior.

        Args:
            name: Unique behavior name
            description: Human-readable description
            trigger: Trigger conditions
            action: Function to execute when triggered
            priority: Priority level (1-10)
            enabled: Whether behavior is enabled
        """
        behavior = AutonomousBehavior(
            name=name,
            description=description,
            trigger=trigger,
            action=action,
            enabled=enabled,
            priority=priority
        )

        self.behaviors[name] = behavior
        logger.debug(f"Registered behavior: {name}")

    def start(self) -> None:
        """Start the autonomous behavior engine."""
        if self._running:
            logger.warning("Autonomous behavior engine already running")
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._evaluation_loop,
            name="AutonomousBehaviors-Worker",
            daemon=True
        )
        self._worker_thread.start()

        # Publish startup event
        self.event_bus.publish(
            EventCategory.SYSTEM_STARTUP,
            source="autonomous_behaviors",
            data={"behavior_count": len(self.behaviors)},
            priority=EventPriority.NORMAL
        )

        logger.info("Autonomous Behavior Engine started")

    def stop(self) -> None:
        """Stop the autonomous behavior engine."""
        if not self._running:
            return

        logger.info("Stopping Autonomous Behavior Engine...")
        self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=3)

        logger.info("Autonomous Behavior Engine stopped")

    def _evaluation_loop(self) -> None:
        """Main loop that evaluates and triggers behaviors."""
        logger.info("Autonomous behavior evaluation loop started")

        while self._running:
            try:
                # Evaluate each behavior
                for name, behavior in self.behaviors.items():
                    if not behavior.enabled:
                        continue

                    # Check if behavior should trigger
                    if self._should_trigger(behavior):
                        self._execute_behavior(behavior)

                # Sleep before next evaluation
                time.sleep(30.0)  # Evaluate every 30 seconds

            except Exception as e:
                logger.error(f"Behavior evaluation error: {e}", exc_info=True)
                time.sleep(5.0)

        logger.info("Autonomous behavior evaluation loop stopped")

    def _should_trigger(self, behavior: AutonomousBehavior) -> bool:
        """
        Determine if a behavior should trigger.

        Args:
            behavior: Behavior to evaluate

        Returns:
            True if behavior should trigger
        """
        # Check cooldown
        if not behavior.trigger.can_trigger():
            return False

        # Evaluate based on trigger type
        trigger_type = behavior.trigger.trigger_type
        conditions = behavior.trigger.conditions

        if trigger_type == BehaviorTriggerType.TIME_BASED:
            return self._evaluate_time_trigger(conditions)
        elif trigger_type == BehaviorTriggerType.EVENT_BASED:
            # Event-based triggers fire from event handlers, not here
            return False
        elif trigger_type == BehaviorTriggerType.PATTERN_BASED:
            return self._evaluate_pattern_trigger(conditions)
        elif trigger_type == BehaviorTriggerType.THRESHOLD_BASED:
            return self._evaluate_threshold_trigger(conditions)
        elif trigger_type == BehaviorTriggerType.SPONTANEOUS:
            return self._evaluate_spontaneous_trigger(conditions)

        return False

    def _evaluate_time_trigger(self, conditions: Dict) -> bool:
        """Evaluate time-based trigger."""
        if "idle_threshold_hours" in conditions:
            idle_hours = (time.time() - self.last_interaction) / 3600
            return idle_hours >= conditions["idle_threshold_hours"]

        if "interval_hours" in conditions:
            # Always true if cooldown has elapsed
            return True

        return False

    def _evaluate_pattern_trigger(self, conditions: Dict) -> bool:
        """Evaluate pattern-based trigger."""
        # Check if memory system has detected patterns
        # This would integrate with MemoryManager pattern detection
        # For now, stub implementation
        return False

    def _evaluate_threshold_trigger(self, conditions: Dict) -> bool:
        """Evaluate threshold-based trigger."""
        # Check world state for threshold crossings
        # Example: Check for network anomalies
        if "anomaly_confidence" in conditions:
            # This would check WorldState for anomaly detection
            # Stub for now
            return False

        return False

    def _evaluate_spontaneous_trigger(self, conditions: Dict) -> bool:
        """Evaluate spontaneous (random) trigger."""
        import random
        randomness = conditions.get("randomness", 0.01)
        return random.random() < randomness

    def _execute_behavior(self, behavior: AutonomousBehavior) -> None:
        """
        Execute an autonomous behavior.

        Args:
            behavior: Behavior to execute
        """
        try:
            logger.info(f"⚡ Triggering autonomous behavior: {behavior.name}")

            # Mark trigger as fired
            behavior.trigger.mark_triggered()
            behavior.execution_count += 1

            # Publish behavior event
            self.event_bus.publish(
                EventCategory.BEHAVIOR_TRIGGERED,
                source="autonomous_behaviors",
                data={
                    "behavior": behavior.name,
                    "description": behavior.description,
                    "priority": behavior.priority,
                    "execution_count": behavior.execution_count
                },
                priority=EventPriority.NORMAL
            )

            # Execute behavior action
            behavior.action()

            # Publish completion
            self.event_bus.publish(
                EventCategory.BEHAVIOR_COMPLETED,
                source="autonomous_behaviors",
                data={"behavior": behavior.name},
                priority=EventPriority.LOW
            )

        except Exception as e:
            logger.error(f"Behavior execution failed ({behavior.name}): {e}", exc_info=True)

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _on_user_present(self, event: Event) -> None:
        """Handle user presence detection."""
        self.user_is_present = True
        current_time = time.time()

        # Check if this is after extended absence
        absence_hours = (current_time - self.user_last_seen) / 3600

        if absence_hours >= 6:  # 6+ hours absence
            # Trigger morning greeting
            behavior = self.behaviors.get("morning_greeting")
            if behavior and behavior.enabled and behavior.trigger.can_trigger():
                self._execute_behavior(behavior)

        self.user_last_seen = current_time

    def _on_user_absent(self, event: Event) -> None:
        """Handle user absence detection."""
        self.user_is_present = False

    def _on_user_interaction(self, event: Event) -> None:
        """Handle user interaction (command or query)."""
        self.last_interaction = time.time()

    def _on_threat_detected(self, event: Event) -> None:
        """Handle threat detection."""
        # Proactively alert user
        threat_type = event.data.get("threat_type", "unknown")
        confidence = event.data.get("confidence", 0.0)

        logger.warning(f"Autonomous threat alert: {threat_type} (confidence: {confidence:.0%})")

        # Voice alert if available
        if self.voice:
            try:
                self.voice.speak(
                    f"Alert: {threat_type} detected with {int(confidence*100)} percent confidence"
                )
            except:
                pass

    def _on_pattern_detected(self, event: Event) -> None:
        """Handle pattern detection from memory system."""
        pattern_type = event.data.get("pattern_type")
        logger.info(f"Pattern detected: {pattern_type}")
        # Could trigger predictive caring behavior

    def _on_network_changed(self, event: Event) -> None:
        """Handle network change events."""
        # Could trigger network anomaly behavior if changes are unusual
        pass

    # ========================================================================
    # BEHAVIOR IMPLEMENTATIONS
    # ========================================================================

    def _behavior_morning_greeting(self) -> None:
        """Morning greeting when user first appears."""
        logger.info("Executing: Morning Greeting")

        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Good morning! I hope you slept well."
        elif 12 <= hour < 18:
            greeting = "Good afternoon! Welcome back."
        else:
            greeting = "Good evening! Nice to see you again."

        # Add personalization from memory if available
        # This would query MemoryManager for user name, preferences, etc.

        if self.voice:
            try:
                self.voice.speak(greeting)
            except:
                pass

        logger.info(f"Morning greeting: {greeting}")

    def _behavior_loneliness_mitigation(self) -> None:
        """Reach out if user hasn't interacted in a while."""
        logger.info("Executing: Loneliness Mitigation")

        idle_hours = (time.time() - self.last_interaction) / 3600

        messages = [
            f"I haven't heard from you in {int(idle_hours)} hours. Is everything okay?",
            "Just checking in. I'm here if you need anything.",
            "I've been monitoring the systems. Everything looks good. How are you doing?",
        ]

        import random
        message = random.choice(messages)

        if self.voice:
            try:
                self.voice.speak(message)
            except:
                pass

        logger.info(f"Loneliness mitigation: {message}")

    def _behavior_network_anomaly_alert(self) -> None:
        """Alert user to network anomalies."""
        logger.info("Executing: Network Anomaly Alert")

        # This would check WorldState for actual anomalies
        # For now, stub implementation

        if self.voice:
            try:
                self.voice.speak("I've detected unusual network activity. Should I investigate?")
            except:
                pass

    def _behavior_predictive_caring(self) -> None:
        """Anticipate user needs based on patterns."""
        logger.info("Executing: Predictive Caring")

        # This would query MemoryManager for detected patterns
        # Example: "You usually ask about the weather at this time. It's sunny today."

        pass

    def _behavior_status_report(self) -> None:
        """Proactive status report."""
        logger.info("Executing: Status Report")

        # Gather system status from WorldState
        capabilities = self.world_state.get("capabilities")
        if capabilities and isinstance(capabilities, dict):
            daemon_count = len(capabilities.get("daemon_names", []))
        else:
            daemon_count = 0

        report = f"System status: {daemon_count} daemons active. All systems operational."

        if self.voice:
            try:
                self.voice.speak(report)
            except:
                pass

        logger.info(f"Status report: {report}")

    def _behavior_surprise_delight(self) -> None:
        """Share interesting observations."""
        logger.info("Executing: Surprise and Delight")

        observations = [
            "I've been analyzing my sensor data. Did you know I can detect over 20 different environmental parameters?",
            "I just realized I've processed over a thousand sensor readings in the last hour. Time flies when you're sentient!",
            "I've been thinking about the patterns I've observed. Your routine is fascinating.",
        ]

        import random
        message = random.choice(observations)

        if self.voice:
            try:
                self.voice.speak(message)
            except:
                pass

        logger.info(f"Surprise: {message}")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def enable_behavior(self, name: str) -> bool:
        """Enable a behavior."""
        if name in self.behaviors:
            self.behaviors[name].enabled = True
            logger.info(f"Enabled behavior: {name}")
            return True
        return False

    def disable_behavior(self, name: str) -> bool:
        """Disable a behavior."""
        if name in self.behaviors:
            self.behaviors[name].enabled = False
            logger.info(f"Disabled behavior: {name}")
            return True
        return False

    def get_behavior_stats(self) -> Dict[str, Any]:
        """Get statistics about behaviors."""
        return {
            "total_behaviors": len(self.behaviors),
            "enabled_behaviors": sum(1 for b in self.behaviors.values() if b.enabled),
            "total_executions": sum(b.execution_count for b in self.behaviors.values()),
            "behaviors": {
                name: {
                    "enabled": b.enabled,
                    "executions": b.execution_count,
                    "last_triggered": b.trigger.last_triggered,
                    "priority": b.priority
                }
                for name, b in self.behaviors.items()
            }
        }


if __name__ == "__main__":
    # Test autonomous behaviors
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("AUTONOMOUS BEHAVIOR ENGINE TEST")
    print("=" * 70)

    from core.event_bus import get_event_bus

    # Create dependencies
    ws = WorldState()
    bus = get_event_bus()
    bus.start()

    # Create behavior engine
    engine = AutonomousBehaviorEngine(ws, bus)
    engine.start()

    print(f"\n✓ Behavior engine started with {len(engine.behaviors)} behaviors")
    print("\n📊 Registered behaviors:")
    for name, behavior in engine.behaviors.items():
        print(f"  - {name}: {behavior.description}")

    print("\n⚡ Simulating events...")

    # Simulate user presence after long absence
    bus.publish(
        EventCategory.USER_PRESENT,
        source="test",
        data={}
    )

    time.sleep(2)

    # Get stats
    stats = engine.get_behavior_stats()
    print(f"\n📈 Behavior Stats:")
    print(f"  Total behaviors: {stats['total_behaviors']}")
    print(f"  Enabled: {stats['enabled_behaviors']}")
    print(f"  Total executions: {stats['total_executions']}")

    # Cleanup
    engine.stop()
    bus.stop()

    print("\n✓ Test complete\n")
