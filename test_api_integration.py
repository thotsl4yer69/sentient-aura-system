#!/usr/bin/env python3
"""
Sentient Core v4 - API Integration Test Suite
Comprehensive testing of all API services.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import json
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger("test_api_integration")


class APIIntegrationTest:
    """Test suite for API integration."""

    def __init__(self):
        """Initialize test suite."""
        self.results = {
            'config': {'status': 'not_tested', 'details': None},
            'llm': {'status': 'not_tested', 'details': None},
            'search': {'status': 'not_tested', 'details': None},
            'weather': {'status': 'not_tested', 'details': None},
            'homeassistant': {'status': 'not_tested', 'details': None},
            'memory': {'status': 'not_tested', 'details': None},
            'api_manager': {'status': 'not_tested', 'details': None},
        }

    def test_config(self) -> bool:
        """Test API configuration."""
        print("\n" + "=" * 80)
        print("Testing API Configuration")
        print("=" * 80)

        try:
            from sentient_aura.api_config import get_api_config

            config = get_api_config()
            safe_config = config.get_safe_config()
            validation = config.validate()

            print("\n✓ API Configuration loaded successfully")
            print(f"\nAvailable LLM Backends: {validation['llm_backends']}")
            print(f"Search Available: {validation['search_available']}")
            print(f"Weather Available: {validation['weather_available']}")
            print(f"Home Assistant Available: {validation['homeassistant_available']}")
            print(f"Memory Available: {validation['database_configured']}")

            self.results['config'] = {
                'status': 'passed',
                'details': validation
            }

            return True

        except Exception as e:
            print(f"\n✗ Configuration test failed: {e}")
            self.results['config'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def test_llm(self) -> bool:
        """Test LLM service."""
        print("\n" + "=" * 80)
        print("Testing LLM Service")
        print("=" * 80)

        try:
            from sentient_aura.api_config import get_api_config
            from sentient_aura.llm_service import LLMService

            config = get_api_config()
            service = LLMService(config)

            if not service.available_backends:
                print("\n⚠ No LLM backends available")
                self.results['llm'] = {
                    'status': 'skipped',
                    'details': 'No backends configured'
                }
                return False

            print(f"\nAvailable backends: {service.available_backends}")

            # Test chat
            print("\nTesting chat with simple query...")
            response = service.chat("Say 'Hello World' in exactly 2 words.", stream=False)

            if response.is_success():
                print(f"✓ Response received from {response.backend}")
                print(f"  Content: {response.content}")
                print(f"  Latency: {response.latency:.2f}s")

                self.results['llm'] = {
                    'status': 'passed',
                    'details': {
                        'backend': response.backend,
                        'model': response.model,
                        'latency': response.latency,
                    }
                }
                return True
            else:
                print(f"✗ LLM request failed: {response.error}")
                self.results['llm'] = {
                    'status': 'failed',
                    'details': response.error
                }
                return False

        except Exception as e:
            print(f"\n✗ LLM test failed: {e}")
            self.results['llm'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def test_search(self) -> bool:
        """Test search service."""
        print("\n" + "=" * 80)
        print("Testing Search Service")
        print("=" * 80)

        try:
            from sentient_aura.api_config import get_api_config
            from sentient_aura.search_service import SearchService

            config = get_api_config()
            service = SearchService(config)

            if not service.available:
                print("\n⚠ Search service not available (no API key)")
                self.results['search'] = {
                    'status': 'skipped',
                    'details': 'No API key configured'
                }
                return False

            # Test search
            print("\nSearching for 'Raspberry Pi'...")
            response = service.search("Raspberry Pi", max_results=3)

            if response.is_success():
                print(f"✓ Found {response.total_results} results in {response.search_time:.2f}s")
                for i, result in enumerate(response.results[:2], 1):
                    print(f"  {i}. {result.title}")

                self.results['search'] = {
                    'status': 'passed',
                    'details': {
                        'results': response.total_results,
                        'search_time': response.search_time,
                    }
                }
                return True
            else:
                print(f"✗ Search failed: {response.error}")
                self.results['search'] = {
                    'status': 'failed',
                    'details': response.error
                }
                return False

        except Exception as e:
            print(f"\n✗ Search test failed: {e}")
            self.results['search'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def test_weather(self) -> bool:
        """Test weather service."""
        print("\n" + "=" * 80)
        print("Testing Weather Service")
        print("=" * 80)

        try:
            from sentient_aura.api_config import get_api_config
            from sentient_aura.weather_service import WeatherService

            config = get_api_config()
            service = WeatherService(config)

            print(f"\nWeather service initialized:")
            print(f"  API Key: {'✓' if service.has_api_key else '✗'}")
            print(f"  Location: {'✓' if service.has_location else '✗'}")

            # Test weather fetch
            print("\nFetching weather data...")
            response = service.get_current_weather()

            if response.is_success():
                w = response.current
                print(f"✓ Weather data received")
                print(f"  Temperature: {w.temperature}°C")
                print(f"  Humidity: {w.humidity}%")
                print(f"  Pressure: {w.pressure} hPa")
                print(f"  Source: {w.source}")

                self.results['weather'] = {
                    'status': 'passed',
                    'details': {
                        'temperature': w.temperature,
                        'source': w.source,
                    }
                }
                return True
            else:
                print(f"✗ Weather fetch failed: {response.error}")
                self.results['weather'] = {
                    'status': 'failed',
                    'details': response.error
                }
                return False

        except Exception as e:
            print(f"\n✗ Weather test failed: {e}")
            self.results['weather'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def test_homeassistant(self) -> bool:
        """Test Home Assistant bridge."""
        print("\n" + "=" * 80)
        print("Testing Home Assistant Bridge")
        print("=" * 80)

        try:
            from sentient_aura.api_config import get_api_config
            from sentient_aura.homeassistant_bridge import HomeAssistantBridge

            config = get_api_config()
            bridge = HomeAssistantBridge(config)

            if not bridge.available:
                print("\n⚠ Home Assistant not available")
                self.results['homeassistant'] = {
                    'status': 'skipped',
                    'details': 'Service not available'
                }
                return False

            # Test entity fetch
            print("\nFetching entities...")
            entities = bridge.get_states()

            if entities:
                print(f"✓ Found {len(entities)} entities")

                # Count by domain
                domains = {}
                for entity in entities:
                    domains[entity.domain] = domains.get(entity.domain, 0) + 1

                for domain, count in sorted(domains.items())[:5]:
                    print(f"  {domain}: {count}")

                self.results['homeassistant'] = {
                    'status': 'passed',
                    'details': {
                        'total_entities': len(entities),
                        'domains': domains,
                    }
                }
                return True
            else:
                print("✗ No entities found")
                self.results['homeassistant'] = {
                    'status': 'failed',
                    'details': 'No entities'
                }
                return False

        except Exception as e:
            print(f"\n✗ Home Assistant test failed: {e}")
            self.results['homeassistant'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def test_memory(self) -> bool:
        """Test memory manager."""
        print("\n" + "=" * 80)
        print("Testing Memory Manager")
        print("=" * 80)

        try:
            from sentient_aura.api_config import get_api_config
            from sentient_aura.memory_manager import MemoryManager

            config = get_api_config()
            manager = MemoryManager(config)

            if not manager.available:
                print("\n⚠ Memory manager not available (PostgreSQL not running)")
                self.results['memory'] = {
                    'status': 'skipped',
                    'details': 'Database not available'
                }
                return False

            # Test conversation storage
            print("\nStoring test conversation...")
            entry_id = manager.store_conversation(
                "user",
                "This is a test message",
                intent="test"
            )

            if entry_id:
                print(f"✓ Conversation stored (ID: {entry_id})")

                # Test retrieval
                print("\nRetrieving recent conversations...")
                recent = manager.get_recent_conversations(limit=5)

                print(f"✓ Retrieved {len(recent)} conversations")

                # Test analytics
                print("\nGetting analytics...")
                analytics = manager.get_analytics()

                print(f"✓ Analytics retrieved:")
                print(f"  Total: {analytics.get('total_conversations', 0)}")

                manager.close()

                self.results['memory'] = {
                    'status': 'passed',
                    'details': {
                        'conversations': analytics.get('total_conversations', 0),
                    }
                }
                return True
            else:
                print("✗ Failed to store conversation")
                manager.close()
                self.results['memory'] = {
                    'status': 'failed',
                    'details': 'Storage failed'
                }
                return False

        except Exception as e:
            print(f"\n✗ Memory test failed: {e}")
            self.results['memory'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def test_api_manager(self) -> bool:
        """Test unified API manager."""
        print("\n" + "=" * 80)
        print("Testing Unified API Manager")
        print("=" * 80)

        try:
            from sentient_aura.api_manager import APIManager

            manager = APIManager()

            # Health check
            print("\nHealth Check:")
            health = manager.health_check()

            print(f"  LLM: {'✓' if health.llm_available else '✗'}")
            print(f"  Search: {'✓' if health.search_available else '✗'}")
            print(f"  Weather: {'✓' if health.weather_available else '✗'}")
            print(f"  Home Assistant: {'✓' if health.homeassistant_available else '✗'}")
            print(f"  Memory: {'✓' if health.memory_available else '✗'}")

            # Test basic functionality
            services_tested = 0
            services_passed = 0

            if health.llm_available:
                print("\nTesting LLM via API Manager...")
                services_tested += 1
                response = manager.chat("Hello", stream=False)
                if response.is_success():
                    print(f"  ✓ LLM: {response.backend}")
                    services_passed += 1

            if health.weather_available:
                print("\nTesting Weather via API Manager...")
                services_tested += 1
                weather = manager.get_weather()
                if weather.is_success():
                    print(f"  ✓ Weather: {weather.current.temperature}°C")
                    services_passed += 1

            # Get statistics
            stats = manager.get_detailed_stats()

            print(f"\n✓ API Manager: {services_passed}/{services_tested} services working")

            manager.shutdown()

            self.results['api_manager'] = {
                'status': 'passed',
                'details': {
                    'health': health.to_dict(),
                    'services_tested': services_tested,
                    'services_passed': services_passed,
                }
            }

            return True

        except Exception as e:
            print(f"\n✗ API Manager test failed: {e}")
            self.results['api_manager'] = {
                'status': 'failed',
                'details': str(e)
            }
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        total_tests = len(self.results)
        passed = sum(1 for r in self.results.values() if r['status'] == 'passed')
        failed = sum(1 for r in self.results.values() if r['status'] == 'failed')
        skipped = sum(1 for r in self.results.values() if r['status'] == 'skipped')

        for test_name, result in self.results.items():
            status = result['status']
            icon = {
                'passed': '✓',
                'failed': '✗',
                'skipped': '⚠',
                'not_tested': '-'
            }.get(status, '?')

            print(f"{icon} {test_name.upper()}: {status}")

        print("\n" + "-" * 80)
        print(f"Total: {total_tests} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

        if failed == 0:
            print("\n🎉 All tests passed!")
        elif passed > 0:
            print(f"\n⚠ Partial success: {passed} services working")
        else:
            print("\n❌ No services available - check configuration")

        print("=" * 80)

        # Save results to file
        with open('api_test_results.json', 'w') as f:
            json.dump(self.results, indent=2, fp=f, default=str)
        print("\nResults saved to: api_test_results.json")

    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 80)
        print("SENTIENT CORE v4 - API INTEGRATION TEST SUITE")
        print("=" * 80)

        self.test_config()
        self.test_llm()
        self.test_search()
        self.test_weather()
        self.test_homeassistant()
        self.test_memory()
        self.test_api_manager()

        self.print_summary()


def main():
    """Main test function."""
    test_suite = APIIntegrationTest()
    test_suite.run_all()


if __name__ == "__main__":
    main()
