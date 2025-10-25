#!/usr/bin/env python3
"""
Sentient Core v4 - Unified API Manager
Coordinates all API services and provides a unified interface.
"""

import logging
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

from sentient_aura.api_config import get_api_config
from sentient_aura.llm_service import LLMService, LLMResponse
from sentient_aura.search_service import SearchService, SearchResponse
from sentient_aura.weather_service import WeatherService, WeatherResponse
from sentient_aura.homeassistant_bridge import HomeAssistantBridge, Entity
from sentient_aura.memory_manager import MemoryManager, ConversationEntry

logger = logging.getLogger("api_manager")


@dataclass
class APIHealth:
    """Health status of API services."""
    llm_available: bool
    search_available: bool
    weather_available: bool
    homeassistant_available: bool
    memory_available: bool
    total_requests: int
    failed_requests: int
    uptime: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'llm_available': self.llm_available,
            'search_available': self.search_available,
            'weather_available': self.weather_available,
            'homeassistant_available': self.homeassistant_available,
            'memory_available': self.memory_available,
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'uptime': self.uptime,
        }


class APIManager:
    """
    Unified API manager.

    Provides a single interface to all API services:
    - LLM (Ollama, Claude, OpenAI, etc.)
    - Web Search (Brave)
    - Weather (OpenWeatherMap + Sensors)
    - Home Assistant (Smart Home)
    - Memory (PostgreSQL)

    Features:
    - Automatic service initialization
    - Health monitoring
    - Error handling with fallbacks
    - Request queuing
    - Cost tracking
    - Graceful degradation (offline mode)
    """

    def __init__(self, world_state=None):
        """
        Initialize API manager.

        Args:
            world_state: Optional WorldState for context sharing
        """
        self.world_state = world_state
        self.start_time = time.time()

        # Load configuration
        self.config = get_api_config()

        logger.info("Initializing API Manager...")

        # Initialize services
        self.llm = None
        self.search = None
        self.weather = None
        self.homeassistant = None
        self.memory = None

        self._init_services()

        # Global statistics
        self.stats = {
            'total_requests': 0,
            'failed_requests': 0,
            'service_calls': {
                'llm': 0,
                'search': 0,
                'weather': 0,
                'homeassistant': 0,
                'memory': 0,
            },
        }

        logger.info("✓ API Manager initialized")

    def _init_services(self):
        """Initialize all API services."""
        # LLM Service
        if self.config.is_enabled('llm_api'):
            try:
                self.llm = LLMService(self.config, self.world_state)
                logger.info("✓ LLM service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize LLM service: {e}")

        # Search Service
        if self.config.is_enabled('search_api'):
            try:
                self.search = SearchService(self.config, self.world_state)
                logger.info("✓ Search service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize search service: {e}")

        # Weather Service
        if self.config.is_enabled('weather_api'):
            try:
                self.weather = WeatherService(self.config, self.world_state)
                logger.info("✓ Weather service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize weather service: {e}")

        # Home Assistant Bridge
        if self.config.is_enabled('homeassistant_api'):
            try:
                self.homeassistant = HomeAssistantBridge(self.config, self.world_state)
                logger.info("✓ Home Assistant bridge initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Home Assistant bridge: {e}")

        # Memory Manager
        if self.config.is_enabled('memory_storage'):
            try:
                self.memory = MemoryManager(self.config, self.world_state)
                logger.info("✓ Memory manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize memory manager: {e}")

    def chat(self, message: str, stream: bool = False) -> LLMResponse:
        """
        Send a message to LLM and get response.

        Args:
            message: User message
            stream: Enable streaming

        Returns:
            LLMResponse
        """
        self.stats['total_requests'] += 1
        self.stats['service_calls']['llm'] += 1

        if not self.llm:
            self.stats['failed_requests'] += 1
            return LLMResponse(
                content="LLM service is not available. Please check your configuration.",
                backend='none',
                model='none',
                error="LLM service not initialized"
            )

        try:
            # Store user message in memory
            if self.memory:
                self.memory.store_conversation("user", message)

            # Get LLM response
            response = self.llm.chat(message, stream)

            # Store assistant response in memory
            if self.memory and response.is_success():
                self.memory.store_conversation("assistant", response.content)

            if not response.is_success():
                self.stats['failed_requests'] += 1

            return response

        except Exception as e:
            logger.error(f"Chat error: {e}")
            self.stats['failed_requests'] += 1
            return LLMResponse(
                content="I encountered an error processing your message.",
                backend='error',
                model='none',
                error=str(e)
            )

    def search(self, query: str, max_results: int = 5) -> SearchResponse:
        """
        Perform web search.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            SearchResponse
        """
        self.stats['total_requests'] += 1
        self.stats['service_calls']['search'] += 1

        if not self.search:
            self.stats['failed_requests'] += 1
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0,
                source='none',
                error="Search service not available"
            )

        try:
            response = self.search.search(query, max_results)

            if not response.is_success():
                self.stats['failed_requests'] += 1

            return response

        except Exception as e:
            logger.error(f"Search error: {e}")
            self.stats['failed_requests'] += 1
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0,
                source='error',
                error=str(e)
            )

    def get_weather(self, location: Optional[str] = None) -> WeatherResponse:
        """
        Get weather information.

        Args:
            location: Location name (default: configured location)

        Returns:
            WeatherResponse
        """
        self.stats['total_requests'] += 1
        self.stats['service_calls']['weather'] += 1

        if not self.weather:
            self.stats['failed_requests'] += 1
            return WeatherResponse(
                location=location or "Unknown",
                current=None,
                error="Weather service not available"
            )

        try:
            response = self.weather.get_current_weather(location)

            if not response.is_success():
                self.stats['failed_requests'] += 1

            return response

        except Exception as e:
            logger.error(f"Weather error: {e}")
            self.stats['failed_requests'] += 1
            return WeatherResponse(
                location=location or "Unknown",
                current=None,
                error=str(e)
            )

    def smart_home_control(self, entity_id: str, action: str, **kwargs) -> bool:
        """
        Control smart home device.

        Args:
            entity_id: Entity ID (e.g., 'light.living_room')
            action: Action ('turn_on', 'turn_off', 'toggle')
            **kwargs: Additional parameters

        Returns:
            bool: Success status
        """
        self.stats['total_requests'] += 1
        self.stats['service_calls']['homeassistant'] += 1

        if not self.homeassistant or not self.homeassistant.available:
            logger.warning("Home Assistant not available")
            self.stats['failed_requests'] += 1
            return False

        try:
            if action == 'turn_on':
                return self.homeassistant.turn_on(entity_id, **kwargs)
            elif action == 'turn_off':
                return self.homeassistant.turn_off(entity_id)
            elif action == 'toggle':
                return self.homeassistant.toggle(entity_id)
            else:
                logger.error(f"Unknown action: {action}")
                self.stats['failed_requests'] += 1
                return False

        except Exception as e:
            logger.error(f"Smart home control error: {e}")
            self.stats['failed_requests'] += 1
            return False

    def get_smart_home_status(self) -> Optional[str]:
        """
        Get smart home system status summary.

        Returns:
            str: Status summary, or None if unavailable
        """
        if not self.homeassistant or not self.homeassistant.available:
            return None

        try:
            return self.homeassistant.summarize_state()
        except Exception as e:
            logger.error(f"Smart home status error: {e}")
            return None

    def remember_conversation(self, role: str, content: str, intent: Optional[str] = None,
                             entities: Optional[Dict] = None) -> bool:
        """
        Store conversation in memory.

        Args:
            role: "user" or "assistant"
            content: Message content
            intent: Detected intent
            entities: Extracted entities

        Returns:
            bool: Success status
        """
        self.stats['service_calls']['memory'] += 1

        if not self.memory or not self.memory.available:
            return False

        try:
            entry_id = self.memory.store_conversation(role, content, intent, entities)
            return entry_id is not None

        except Exception as e:
            logger.error(f"Memory storage error: {e}")
            return False

    def get_conversation_context(self, window: int = 5) -> List[ConversationEntry]:
        """
        Get recent conversation context.

        Args:
            window: Number of recent exchanges

        Returns:
            List of ConversationEntry objects
        """
        if not self.memory or not self.memory.available:
            return []

        try:
            return self.memory.get_conversation_context(window)
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return []

    def health_check(self) -> APIHealth:
        """
        Get health status of all services.

        Returns:
            APIHealth object
        """
        return APIHealth(
            llm_available=self.llm is not None and len(self.llm.available_backends) > 0,
            search_available=self.search is not None and self.search.available,
            weather_available=self.weather is not None,
            homeassistant_available=self.homeassistant is not None and self.homeassistant.available,
            memory_available=self.memory is not None and self.memory.available,
            total_requests=self.stats['total_requests'],
            failed_requests=self.stats['failed_requests'],
            uptime=time.time() - self.start_time,
        )

    def get_detailed_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics from all services.

        Returns:
            dict: Comprehensive statistics
        """
        stats = {
            'manager': {
                **self.stats,
                'uptime': time.time() - self.start_time,
            },
            'health': self.health_check().to_dict(),
        }

        if self.llm:
            stats['llm'] = self.llm.get_stats()

        if self.search:
            stats['search'] = self.search.get_stats()

        if self.weather:
            stats['weather'] = self.weather.get_stats()

        if self.homeassistant:
            stats['homeassistant'] = self.homeassistant.get_stats()

        if self.memory:
            stats['memory'] = self.memory.get_stats()

        return stats

    def shutdown(self):
        """Shutdown all services gracefully."""
        logger.info("Shutting down API Manager...")

        if self.memory:
            self.memory.close()

        logger.info("✓ API Manager shutdown complete")

    def __repr__(self) -> str:
        """String representation."""
        health = self.health_check()
        services_up = sum([
            health.llm_available,
            health.search_available,
            health.weather_available,
            health.homeassistant_available,
            health.memory_available,
        ])
        return f"APIManager(services_up={services_up}/5, requests={self.stats['total_requests']})"


# Test function
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("API Manager Test")
    print("=" * 80)

    manager = APIManager()

    print(f"\nManager: {manager}")

    # Health check
    health = manager.health_check()
    print("\nService Health:")
    print(f"  LLM: {'✓' if health.llm_available else '✗'}")
    print(f"  Search: {'✓' if health.search_available else '✗'}")
    print(f"  Weather: {'✓' if health.weather_available else '✗'}")
    print(f"  Home Assistant: {'✓' if health.homeassistant_available else '✗'}")
    print(f"  Memory: {'✓' if health.memory_available else '✗'}")

    # Test LLM
    if health.llm_available:
        print("\n" + "-" * 80)
        print("Testing LLM...")
        response = manager.chat("Hello! Tell me about yourself in one sentence.", stream=False)
        if response.is_success():
            print(f"Response: {response.content}")
            print(f"Backend: {response.backend}")
        else:
            print(f"Error: {response.error}")

    # Test Weather
    if health.weather_available:
        print("\n" + "-" * 80)
        print("Testing Weather...")
        weather = manager.get_weather()
        if weather.is_success():
            print(manager.weather.summarize_weather(weather))
        else:
            print(f"Error: {weather.error}")

    # Test Search
    if health.search_available:
        print("\n" + "-" * 80)
        print("Testing Search...")
        search_results = manager.search("artificial intelligence news", max_results=3)
        if search_results.is_success():
            print(f"Found {search_results.total_results} results")
            for i, result in enumerate(search_results.results[:2], 1):
                print(f"{i}. {result.title}")
        else:
            print(f"Error: {search_results.error}")

    # Statistics
    print("\n" + "-" * 80)
    print("\nDetailed Statistics:")
    import json
    print(json.dumps(manager.get_detailed_stats(), indent=2, default=str))

    # Cleanup
    manager.shutdown()

    print("\n" + "=" * 80)
