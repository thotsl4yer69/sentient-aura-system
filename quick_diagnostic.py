#!/usr/bin/env python3
"""Quick diagnostic to find what's blocking startup."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagnostic")

def test_imports():
    """Test all critical imports."""
    logger.info("Testing imports...")

    try:
        logger.info("  - WorldState...")
        from world_state import WorldState
        logger.info("    ✓ WorldState")

        logger.info("  - HardwareDiscovery...")
        from hardware_discovery import HardwareDiscovery
        logger.info("    ✓ HardwareDiscovery")

        logger.info("  - AdaptiveDaemonManager...")
        from adaptive_daemon_manager import AdaptiveDaemonManager
        logger.info("    ✓ AdaptiveDaemonManager")

        logger.info("  - EventBus...")
        from core.event_bus import get_event_bus
        logger.info("    ✓ EventBus")

        logger.info("All imports successful!")
        return True

    except Exception as e:
        logger.error(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hardware_discovery():
    """Test hardware discovery."""
    logger.info("\nTesting hardware discovery...")

    try:
        from hardware_discovery import HardwareDiscovery
        discovery = HardwareDiscovery()

        logger.info("Running discovery (this might take a few seconds)...")
        capabilities = discovery.discover_all()

        logger.info(f"Found {len(capabilities)} capabilities:")
        for cap_id, cap in capabilities.items():
            # HardwareCapability is a dataclass, access attributes directly
            logger.info(f"  - {cap_id}: {cap.name} ({'✓' if cap.available else '✗'})")

        return True

    except Exception as e:
        logger.error(f"Hardware discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_daemon_creation():
    """Test daemon creation without starting."""
    logger.info("\nTesting daemon creation...")

    try:
        from world_state import WorldState
        from adaptive_daemon_manager import AdaptiveDaemonManager

        ws = WorldState()
        manager = AdaptiveDaemonManager(ws)

        logger.info("Discovering and configuring daemons...")
        logger.info("(NOTE: This may hang if a daemon blocks during __init__)")

        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError("Daemon creation timed out!")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        try:
            daemons = manager.discover_and_configure()
            signal.alarm(0)  # Cancel alarm

            logger.info(f"Created {len(daemons)} daemons:")
            for daemon in daemons:
                logger.info(f"  - {daemon.daemon_name}")

            return True

        except TimeoutError:
            logger.error("TIMEOUT during daemon creation!")
            logger.error("One of the daemons is blocking in __init__")
            return False

    except Exception as e:
        logger.error(f"Daemon creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("SENTIENT CORE - QUICK DIAGNOSTIC")
    logger.info("=" * 70)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Hardware Discovery
    results.append(("Hardware Discovery", test_hardware_discovery()))

    # Test 3: Daemon Creation
    results.append(("Daemon Creation", test_daemon_creation()))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        logger.info("\n✓ All tests passed! System should be able to start.")
    else:
        logger.info("\n✗ Some tests failed. Fix these issues before starting the system.")

    sys.exit(0 if all_passed else 1)
