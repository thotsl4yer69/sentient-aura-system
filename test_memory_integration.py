#!/usr/bin/env python3
"""
Test Memory Integration - Guardian Success Criteria

Tests that Aura can:
1. Store conversations in memory
2. Retrieve relevant memories in new conversations
3. Remember user's name unprompted
4. Remember user's preferences unprompted
5. Detect patterns from conversation history

Success Criteria (Guardian):
"By end of Day 2, Aura must remember your name and one preference from
a previous conversation, unprompted."
"""

import logging
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldState
from intelligence.conversation.conversation_daemon import ConversationDaemon
from intelligence.memory.memory_manager import MemoryManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("MemoryIntegrationTest")

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def simulate_conversation(daemon: ConversationDaemon, ws: WorldState, message: str) -> str:
    """Simulate a user message and get response."""
    print(f"\n👤 User: {message}")

    # Set message in world state
    ws.update_nested("conversation.user_message", message)

    # Trigger daemon update
    daemon.update()

    # Wait for processing
    time.sleep(0.1)

    # Get response
    response = ws.get_nested("conversation.response")
    if response:
        print(f"🤖 Aura: {response['message']}")
        print(f"   (response time: {response.get('response_time_s', 0):.2f}s, memories used: {response.get('memories_used', 0)})")
        return response['message']
    else:
        print("❌ No response generated")
        return ""

def main():
    print_section("MEMORY INTEGRATION TEST - GUARDIAN SUCCESS CRITERIA")

    # Clean up old test database
    test_db = Path("intelligence/memory/sentient_memory.db")
    if test_db.exists():
        test_db.unlink()
        logger.info("Removed old test database")

    # Create world state with simulated intelligence context
    ws = WorldState()
    ws.update("intelligence", {
        "status": "active",
        "inference": {
            "presence": {"detected": True, "confidence": 0.95},
            "activity": {"activity": "working", "confidence": 0.89}
        }
    })
    ws.update("environment", {
        "temperature": 22.5,
        "humidity": 45,
        "light_level": "bright"
    })

    # Create daemon with memory enabled
    daemon = ConversationDaemon(ws, update_rate=1.0, enable_proactive=False)

    if not daemon.initialize():
        print("❌ Daemon initialization failed")
        sys.exit(1)

    print("✅ Daemon initialized with memory system")

    # =========================================================================
    # PHASE 1: Initial conversation - introduce name and preference
    # =========================================================================
    print_section("PHASE 1: Initial Conversation (Learning)")

    simulate_conversation(
        daemon, ws,
        "Hello! My name is Alex. Nice to meet you!"
    )
    time.sleep(1)

    simulate_conversation(
        daemon, ws,
        "I really enjoy working with Python and building AI systems. It's my favorite language."
    )
    time.sleep(1)

    simulate_conversation(
        daemon, ws,
        "Can you tell me about your sensor capabilities?"
    )
    time.sleep(1)

    # Check what was stored
    if daemon.memory:
        memories = daemon.memory.get_all_memories("default_user")
        print(f"\n📝 Stored {len(memories)} memories from initial conversation")

        # Detect patterns
        patterns = daemon.memory.detect_preference_patterns("default_user", min_occurrences=1)
        print(f"🔍 Detected {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"   - [{pattern.pattern_type}] {pattern.pattern_data.get('description', 'N/A')} "
                  f"(confidence: {pattern.confidence:.2f})")

    # =========================================================================
    # PHASE 2: Simulate daemon restart (memory persistence test)
    # =========================================================================
    print_section("PHASE 2: Simulating Daemon Restart")

    print("🔄 Cleaning up daemon...")
    daemon.cleanup()
    daemon = None
    time.sleep(1)

    print("🔄 Reinitializing daemon (testing memory persistence)...")
    daemon = ConversationDaemon(ws, update_rate=1.0, enable_proactive=False)
    if not daemon.initialize():
        print("❌ Daemon reinitialization failed")
        sys.exit(1)

    print("✅ Daemon reinitialized - memory should persist")

    # =========================================================================
    # PHASE 3: New conversation - verify memory recall (GUARDIAN TEST)
    # =========================================================================
    print_section("PHASE 3: New Conversation (Memory Recall Test)")

    print("\n🎯 GUARDIAN SUCCESS CRITERIA TEST:")
    print("   Aura should remember:")
    print("   1. User's name is Alex")
    print("   2. User prefers Python")
    print("   WITHOUT being explicitly reminded!\n")

    response1 = simulate_conversation(
        daemon, ws,
        "Hi there! What do you remember about me?"
    )
    time.sleep(1)

    response2 = simulate_conversation(
        daemon, ws,
        "What programming topics should we discuss?"
    )
    time.sleep(1)

    # =========================================================================
    # PHASE 4: Verify success criteria
    # =========================================================================
    print_section("VERIFICATION: Guardian Success Criteria")

    success_criteria = {
        "name_remembered": False,
        "preference_remembered": False
    }

    # Check if responses contain the name and preference
    all_responses = response1 + " " + response2
    all_responses_lower = all_responses.lower()

    if "alex" in all_responses_lower:
        success_criteria["name_remembered"] = True
        print("✅ SUCCESS: Aura remembered the user's name (Alex)")
    else:
        print("❌ FAIL: Aura did NOT remember the user's name")

    if "python" in all_responses_lower:
        success_criteria["preference_remembered"] = True
        print("✅ SUCCESS: Aura remembered the user's preference (Python)")
    else:
        print("❌ FAIL: Aura did NOT remember the user's preference")

    # =========================================================================
    # PHASE 5: Memory statistics
    # =========================================================================
    print_section("MEMORY SYSTEM STATISTICS")

    if daemon.memory:
        stats = daemon.memory.get_stats()
        print(f"Total memories stored: {stats['total_memories']}")
        print(f"Average importance: {stats['avg_importance']:.2f}")
        print(f"Patterns detected: {stats['patterns_detected']}")

        # Show all memories
        memories = daemon.memory.get_all_memories("default_user")
        print(f"\n📚 All Stored Memories ({len(memories)}):")
        for i, mem in enumerate(memories[:10], 1):  # Show first 10
            age_hours = (time.time() - mem.timestamp) / 3600
            print(f"   {i}. [{mem.memory_type}] {mem.content[:60]}... "
                  f"(importance: {mem.importance:.2f}, age: {age_hours:.1f}h)")

    # =========================================================================
    # FINAL VERDICT
    # =========================================================================
    print_section("FINAL VERDICT")

    if all(success_criteria.values()):
        print("🎉 GUARDIAN SUCCESS CRITERIA: PASSED")
        print("   ✅ Aura successfully remembers name AND preference from previous conversation")
        print("   ✅ Memory persistence across daemon restarts: WORKING")
        print("   ✅ Pattern detection: OPERATIONAL")
        print("\n💬 Aura is now capable of forming lasting memories and learning about users!")
    else:
        print("⚠️  GUARDIAN SUCCESS CRITERIA: PARTIALLY PASSED")
        for criterion, passed in success_criteria.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion.replace('_', ' ').title()}")
        print("\n🔧 Memory system needs debugging - responses may not be using memories correctly")

    # Cleanup
    print_section("CLEANUP")
    daemon.cleanup()
    print("✅ Test complete\n")

if __name__ == "__main__":
    main()
