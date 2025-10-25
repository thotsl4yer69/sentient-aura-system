#!/usr/bin/env python3
"""
Integration Test - Verify All Systems Working Together

Tests:
1. EventBus creates and distributes events
2. Autonomous behaviors subscribe and respond
3. Sensor recorder captures data
4. WorldState integrates with EventBus
5. All daemons can publish events
"""

import sys
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("IntegrationTest")


def test_eventbus():
    """Test EventBus creation and basic operations."""
    logger.info("=" * 70)
    logger.info("TEST 1: EventBus")
    logger.info("=" * 70)

    from core.event_bus import get_event_bus, EventCategory, EventPriority

    bus = get_event_bus()
    bus.start()

    # Test event publishing
    event_received = []

    def test_callback(event):
        event_received.append(event)

    bus.subscribe(EventCategory.SENSOR_UPDATE, test_callback)

    bus.publish(
        EventCategory.SENSOR_UPDATE,
        source="test",
        data={"temperature": 25.5}
    )

    time.sleep(0.5)

    assert len(event_received) == 1, "Event not received!"
    assert event_received[0].data["temperature"] == 25.5

    logger.info("✓ EventBus: PASSED")
    logger.info(f"  Stats: {bus.get_stats()}")

    bus.stop()
    return True


def test_autonomous_behaviors():
    """Test Autonomous Behavior Engine."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Autonomous Behaviors")
    logger.info("=" * 70)

    from core.event_bus import get_event_bus, EventCategory
    from core.autonomous_behaviors import AutonomousBehaviorEngine
    from world_state import WorldState

    ws = WorldState()
    bus = get_event_bus()
    bus.start()

    engine = AutonomousBehaviorEngine(ws, bus)
    engine.start()

    # Check registered behaviors
    assert len(engine.behaviors) == 6, f"Expected 6 behaviors, got {len(engine.behaviors)}"

    logger.info(f"✓ Autonomous Behaviors: PASSED")
    logger.info(f"  Registered behaviors: {list(engine.behaviors.keys())}")

    stats = engine.get_behavior_stats()
    logger.info(f"  Stats: {stats['total_behaviors']} behaviors, {stats['enabled_behaviors']} enabled")

    engine.stop()
    bus.stop()
    return True


def test_sensor_recorder():
    """Test Real Sensor Recorder."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Real Sensor Recorder")
    logger.info("=" * 70)

    from core.event_bus import get_event_bus
    from core.real_sensor_recorder import RealSensorRecorder
    from world_state import WorldState

    ws = WorldState()
    bus = get_event_bus()
    bus.start()

    recorder = RealSensorRecorder(
        ws, bus,
        db_path="test_sensor_data.db",
        recording_interval=1.0
    )
    recorder.start()

    # Let it record a few snapshots
    logger.info("  Recording sensor data for 3 seconds...")
    time.sleep(3)

    stats = recorder.get_statistics()
    assert stats['snapshots_recorded'] >= 2, "Not enough snapshots recorded!"

    logger.info("✓ Sensor Recorder: PASSED")
    logger.info(f"  Snapshots: {stats['snapshots_recorded']}")
    logger.info(f"  Labels: {stats['by_label']}")

    recorder.stop()
    bus.stop()

    # Cleanup test database
    import os
    if os.path.exists("test_sensor_data.db"):
        os.remove("test_sensor_data.db")

    return True


def test_daemon_eventbus_integration():
    """Test that daemons can publish to EventBus."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Daemon → EventBus Integration")
    logger.info("=" * 70)

    from core.event_bus import get_event_bus, EventCategory
    from world_state import WorldState

    ws = WorldState()
    bus = get_event_bus()
    bus.start()

    # Wire EventBus to WorldState
    ws.event_bus = bus

    events_received = []

    def capture_event(event):
        events_received.append(event)

    # Subscribe to all events
    bus.subscribe_all(capture_event)

    # Simulate daemon publishing event
    bus.publish(
        EventCategory.SENSOR_UPDATE,
        source="test_daemon",
        data={"value": 42}
    )

    time.sleep(0.2)

    assert len(events_received) > 0, "No events received!"

    logger.info("✓ Daemon → EventBus: PASSED")
    logger.info(f"  Events captured: {len(events_received)}")

    bus.stop()
    return True


def test_full_pipeline():
    """Test complete integration pipeline."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: Full Integration Pipeline")
    logger.info("=" * 70)

    from core.event_bus import get_event_bus, EventCategory, EventPriority
    from core.autonomous_behaviors import AutonomousBehaviorEngine
    from core.real_sensor_recorder import RealSensorRecorder
    from world_state import WorldState

    ws = WorldState()
    bus = get_event_bus()
    bus.start()

    # Wire EventBus to WorldState
    ws.event_bus = bus

    # Start all systems
    engine = AutonomousBehaviorEngine(ws, bus)
    engine.start()

    recorder = RealSensorRecorder(
        ws, bus,
        db_path="test_full_pipeline.db",
        recording_interval=1.0
    )
    recorder.start()

    # Simulate event flow
    logger.info("  Publishing test event...")
    bus.publish(
        EventCategory.SENSOR_UPDATE,
        source="integration_test",
        data={"test": True},
        priority=EventPriority.NORMAL
    )

    # Let systems process
    time.sleep(2)

    # Verify all systems working
    bus_stats = bus.get_stats()
    behavior_stats = engine.get_behavior_stats()
    recorder_stats = recorder.get_statistics()

    assert bus_stats['events_published'] > 0, "No events published!"
    assert behavior_stats['total_behaviors'] == 6, "Behaviors not initialized!"
    assert recorder_stats['snapshots_recorded'] >= 1, "Recorder not working!"

    logger.info("✓ Full Pipeline: PASSED")
    logger.info(f"  EventBus: {bus_stats['events_published']} events published")
    logger.info(f"  Behaviors: {behavior_stats['total_behaviors']} registered")
    logger.info(f"  Recorder: {recorder_stats['snapshots_recorded']} snapshots")

    # Cleanup
    engine.stop()
    recorder.stop()
    bus.stop()

    import os
    if os.path.exists("test_full_pipeline.db"):
        os.remove("test_full_pipeline.db")

    return True


def main():
    """Run all integration tests."""
    logger.info("\n" + "=" * 70)
    logger.info("SENTIENT CORE V4 - INTEGRATION TEST SUITE")
    logger.info("=" * 70)

    tests = [
        ("EventBus", test_eventbus),
        ("Autonomous Behaviors", test_autonomous_behaviors),
        ("Sensor Recorder", test_sensor_recorder),
        ("Daemon Integration", test_daemon_eventbus_integration),
        ("Full Pipeline", test_full_pipeline),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                logger.error(f"✗ {name}: FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {name}: FAILED with exception")
            logger.exception(e)

    logger.info("\n" + "=" * 70)
    logger.info("TEST RESULTS")
    logger.info("=" * 70)
    logger.info(f"Passed: {passed}/{len(tests)}")
    logger.info(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        logger.info("\n🎉 ALL TESTS PASSED! System integration complete.")
        logger.info("\nNext steps:")
        logger.info("  1. Run full system: ./launch_enhanced.sh")
        logger.info("  2. Let it run for 24 hours to collect data")
        logger.info("  3. Monitor autonomous behaviors triggering")
        logger.info("=" * 70)
        return 0
    else:
        logger.error("\n⚠️  SOME TESTS FAILED! Check logs above.")
        logger.info("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
