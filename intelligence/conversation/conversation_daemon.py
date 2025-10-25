#!/usr/bin/env python3
"""
Conversation Daemon for Sentient Core

Integrates multi-model conversational AI with the world state system.
Provides intelligent, context-aware responses using Ollama LLMs with
automatic model selection based on query complexity and type.

Features:
- Intelligent model routing (qwen, llama3.1, llama3.2, mistral)
- Real-time sensor context injection
- Personality-driven responses
- Conversation history management
- Proactive conversation based on activity detection
"""

import logging
import time
from typing import Dict, Optional, Any
from pathlib import Path
import sys

# Add parent directory to path for daemon_base import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daemon_base import BaseDaemon
from world_state import WorldState
from intelligence.conversation.model_router import ModelRouter, PersonalityTraits
from intelligence.memory.memory_manager import MemoryManager

logger = logging.getLogger("ConversationDaemon")


class ConversationDaemon(BaseDaemon):
    """
    Conversation daemon - provides sentient AI conversation capabilities.

    Integrates with:
    - Intelligence inference layer (presence, activity detection)
    - Environmental sensors (temperature, light, etc.)
    - Power monitoring (battery status)
    - System state (uptime, active daemons)

    Provides:
    - Context-aware conversational responses
    - Intelligent model routing based on query type
    - Proactive conversation triggers
    - Emotional awareness and personality
    """

    def __init__(
        self,
        world_state: WorldState,
        update_rate: float = 0.5,  # Check for events 2x/second
        enable_proactive: bool = False  # Proactive conversation (future feature)
    ):
        """
        Initialize conversation daemon.

        Args:
            world_state: Central world state
            update_rate: How often to check for conversation triggers (Hz)
            enable_proactive: Enable proactive conversation initiation
        """
        super().__init__("conversation", world_state, update_rate)

        self.enable_proactive = enable_proactive

        # Configure personality (can be made dynamic in future)
        self.personality = PersonalityTraits(
            curiosity=0.8,
            helpfulness=0.9,
            formality=0.3,  # Casual and friendly
            proactiveness=0.6,
            empathy=0.9,
            chattiness=0.7
        )

        # Initialize multi-model router
        self.router: Optional[ModelRouter] = None

        # Initialize memory manager
        self.memory: Optional[MemoryManager] = None
        self.user_id = "default_user"  # TODO: Support multiple users

        # Conversation statistics
        self.conversation_count = 0
        self.total_response_time = 0.0
        self.last_conversation_time = None

        # Proactive conversation state
        self.last_proactive_trigger = None
        self.proactive_cooldown = 300  # 5 minutes between proactive messages

    def initialize(self) -> bool:
        """
        Initialize conversation daemon and model router.

        Returns:
            True if initialization successful
        """
        self.logger.info("Initializing Conversation Daemon...")

        try:
            # Create model router (will check Ollama health)
            self.router = ModelRouter(
                personality=self.personality,
                default_model="llama3.2:3b",  # Fast casual conversation
                enable_routing=True
            )

            # Initialize memory manager
            self.memory = MemoryManager(
                db_path="intelligence/memory/sentient_memory.db"
            )
            self.logger.info("✓ Memory system initialized")

            # Update world state
            self.world_state.update("conversation", {
                "status": "active",
                "router_enabled": True,
                "memory_enabled": True,
                "personality": {
                    "curiosity": self.personality.curiosity,
                    "helpfulness": self.personality.helpfulness,
                    "formality": self.personality.formality,
                    "empathy": self.personality.empathy
                },
                "proactive_enabled": self.enable_proactive
            })

            self.logger.info("✓ Conversation Daemon initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}", exc_info=True)
            return False

    def update(self) -> None:
        """
        Main update cycle - check for conversation requests.

        Monitors world_state for:
        - User message requests (world_state.conversation.user_message)
        - Proactive trigger events (if enabled)
        """
        if not self.router:
            return

        # Check for user message request
        user_message = self.world_state.get_nested("conversation.user_message")

        if user_message:
            # Clear the request immediately to prevent reprocessing
            self.world_state.update_nested("conversation.user_message", None)

            # Generate response
            self._handle_user_message(user_message)

        # Check for proactive triggers (future feature)
        if self.enable_proactive:
            self._check_proactive_triggers()

    def _handle_user_message(self, message: str) -> None:
        """
        Handle incoming user message and generate response.

        Args:
            message: User's message string
        """
        start_time = time.time()

        try:
            # Retrieve relevant memories BEFORE generating response
            relevant_memories = []
            if self.memory:
                relevant_memories = self.memory.retrieve_relevant(
                    user_id=self.user_id,
                    context=message,
                    limit=3,
                    min_importance=0.5
                )
                if relevant_memories:
                    self.logger.debug(f"Retrieved {len(relevant_memories)} relevant memories")

            # Gather context from world state
            context = self._gather_context()

            # Inject memories into context
            if relevant_memories:
                context["memories"] = [
                    {
                        "content": mem.content,
                        "type": mem.memory_type,
                        "importance": mem.importance,
                        "age_hours": (time.time() - mem.timestamp) / 3600
                    }
                    for mem in relevant_memories
                ]

            # Generate response with intelligent model routing
            response = self.router.generate(
                user_message=message,
                context=context
            )

            # Store conversation in memory
            if self.memory:
                # Store user message
                self.memory.store_memory(
                    user_id=self.user_id,
                    content=f"User: {message}",
                    memory_type="conversation",
                    importance=0.6  # Conversations are moderately important
                )

                # Store AI response
                self.memory.store_memory(
                    user_id=self.user_id,
                    content=f"Aura: {response}",
                    memory_type="conversation",
                    importance=0.6
                )

                self.logger.debug("Conversation stored in long-term memory")

            # Update statistics
            response_time = time.time() - start_time
            self.conversation_count += 1
            self.total_response_time += response_time
            self.last_conversation_time = time.time()

            # Store response in world state
            self.world_state.update("conversation.response", {
                "message": response,
                "timestamp": time.time(),
                "response_time_s": response_time,
                "conversation_count": self.conversation_count,
                "memories_used": len(relevant_memories)
            })

            self.logger.info(
                f"Conversation #{self.conversation_count}: "
                f"Generated response in {response_time:.2f}s "
                f"(used {len(relevant_memories)} memories)"
            )

        except ConnectionError as e:
            # Ollama service is down - provide helpful fallback
            self.logger.error(f"Ollama service unavailable: {e}")

            fallback_message = (
                "I'm experiencing connectivity issues with my language processing system. "
                "I can still sense my environment, but I can't form complex responses right now. "
                "Please check if the Ollama service is running."
            )

            self.world_state.update("conversation.response", {
                "message": fallback_message,
                "error": "ollama_unavailable",
                "timestamp": time.time(),
                "fallback": True
            })

        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)

            # Provide context-aware fallback based on what we know
            context = self._gather_context()
            fallback_message = self._generate_fallback_response(message, context)

            self.world_state.update("conversation.response", {
                "message": fallback_message,
                "error": str(e),
                "timestamp": time.time(),
                "fallback": True
            })

    def _gather_context(self) -> Dict[str, Any]:
        """
        Gather current context from world state for LLM.

        Returns:
            Context dictionary with all available sensor/system data
        """
        context = {}

        # Intelligence inference (presence, activity)
        intelligence = self.world_state.get("intelligence")
        if intelligence:
            context["intelligence"] = intelligence

        # Environment sensors
        environment = self.world_state.get("environment")
        if environment:
            context["environment"] = environment

        # Power status
        power = self.world_state.get("power")
        if power:
            context["power"] = power

        # System status
        system = self.world_state.get("system")
        if system:
            context["system"] = system

        return context

    def _generate_fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate simple context-aware fallback response when LLM is unavailable.

        Args:
            message: User's message
            context: Current world state context

        Returns:
            Fallback response string
        """
        message_lower = message.lower()

        # Status queries
        if any(word in message_lower for word in ["status", "how are", "what's happening"]):
            parts = ["Here's what I can sense:"]

            # Presence
            if "intelligence" in context:
                inference = context["intelligence"].get("inference", {})
                presence = inference.get("presence", {})
                if presence.get("detected"):
                    parts.append(f"- You're present ({presence.get('confidence', 0)*100:.0f}% confidence)")

                activity = inference.get("activity", {})
                if activity:
                    parts.append(f"- Activity: {activity.get('activity', 'unknown')}")

            # Environment
            if "environment" in context:
                env = context["environment"]
                if env.get("temperature"):
                    parts.append(f"- Temperature: {env['temperature']:.1f}°C")

            return " ".join(parts) if len(parts) > 1 else "I'm operational but my language system is currently unavailable."

        # Help/assistance queries
        elif any(word in message_lower for word in ["help", "assist", "can you"]):
            return "I'd like to help, but my language processing is temporarily offline. I can still monitor sensors and basic status."

        # Greetings
        elif any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm running in fallback mode right now - my conversation system is unavailable, but I can still provide basic sensor information."

        # Default fallback
        else:
            return "I received your message, but I'm operating in fallback mode and can't provide a detailed response. My sensor systems are still active."

    def _check_proactive_triggers(self) -> None:
        """
        Check for conditions that should trigger proactive conversation.

        Future implementation:
        - User enters room after long absence
        - Critical battery level
        - Unusual activity patterns
        - Scheduled reminders
        """
        # Check cooldown
        if self.last_proactive_trigger:
            time_since_last = time.time() - self.last_proactive_trigger
            if time_since_last < self.proactive_cooldown:
                return

        # Example: Presence detected after absence
        inference = self.world_state.get_nested("intelligence.inference")
        if inference:
            presence = inference.get("presence", {})
            if presence.get("detected") and presence.get("confidence", 0) > 0.9:
                # User is present - could trigger greeting
                # (Implementation TBD based on user preferences)
                pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics.

        Returns:
            Dictionary of statistics
        """
        avg_response_time = (
            self.total_response_time / self.conversation_count
            if self.conversation_count > 0
            else 0
        )

        stats = {
            "conversations": self.conversation_count,
            "avg_response_time_s": avg_response_time,
            "last_conversation": self.last_conversation_time,
            "proactive_enabled": self.enable_proactive
        }

        # Add router stats if available
        if self.router:
            stats["routing"] = self.router.get_routing_stats()

        return stats

    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Shutting down Conversation Daemon...")

        if self.conversation_count > 0:
            avg_time = self.total_response_time / self.conversation_count
            self.logger.info(
                f"Conversation Statistics: "
                f"{self.conversation_count} conversations, "
                f"avg {avg_time:.2f}s per response"
            )

        if self.router:
            # Clear all conversation history
            self.router.clear_all_history()

        self.router = None

        if self.memory:
            # Run memory consolidation before shutdown
            consolidated = self.memory.consolidate_memories(self.user_id)
            if consolidated > 0:
                self.logger.info(f"Consolidated {consolidated} memories before shutdown")

            # Close database connection
            self.memory.close()

        self.memory = None


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "="*60)
    print("CONVERSATION DAEMON TEST")
    print("="*60)

    # Create world state
    ws = WorldState()

    # Simulate intelligence context
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

    # Create daemon
    daemon = ConversationDaemon(ws, update_rate=1.0)

    if not daemon.initialize():
        print("✗ Initialization failed")
        sys.exit(1)

    print("\n✓ Daemon initialized")
    print("✓ Simulating conversation...\n")

    # Simulate user messages
    test_messages = [
        "Hello! Can you tell me about yourself?",
        "What can you sense about my current environment?",
        "Help me debug this Python function: def foo(): return bar",
        "Why is the sky blue?"
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n[Conversation {i}]")
        print(f"User: {msg}")

        # Set message in world state
        ws.update_nested("conversation.user_message", msg)

        # Trigger daemon update
        daemon.update()

        # Wait a moment for processing
        time.sleep(0.1)

        # Get response
        response = ws.get_nested("conversation.response")
        if response:
            print(f"Aura: {response['message']}")
            print(f"  (response time: {response.get('response_time_s', 0):.2f}s)")

        time.sleep(1)

    # Show statistics
    print("\n" + "="*60)
    print("CONVERSATION STATISTICS")
    print("="*60)
    stats = daemon.get_stats()

    print(f"Total conversations: {stats['conversations']}")
    print(f"Avg response time: {stats['avg_response_time_s']:.2f}s")

    if 'routing' in stats:
        routing = stats['routing']
        print(f"\nModel routing statistics:")
        for model, count in routing['route_counts'].items():
            pct = routing['route_percentages'].get(model, 0)
            if count > 0:
                print(f"  {model}: {count} times ({pct:.1f}%)")

    print("\n✓ Conversation daemon test complete\n")

    daemon.cleanup()
