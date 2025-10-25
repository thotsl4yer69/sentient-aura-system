#!/usr/bin/env python3
"""
Sentient Core v4 - Home Assistant Bridge
Integration with Home Assistant for smart home control.
"""

import logging
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("homeassistant_bridge")


class EntityDomain(Enum):
    """Home Assistant entity domains."""
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    CLIMATE = "climate"
    COVER = "cover"
    LOCK = "lock"
    MEDIA_PLAYER = "media_player"
    AUTOMATION = "automation"
    SCENE = "scene"


@dataclass
class Entity:
    """Home Assistant entity."""
    entity_id: str
    state: str
    friendly_name: str
    attributes: Dict[str, Any]
    last_changed: str
    last_updated: str

    @property
    def domain(self) -> str:
        """Get entity domain."""
        return self.entity_id.split('.')[0]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'state': self.state,
            'friendly_name': self.friendly_name,
            'attributes': self.attributes,
            'last_changed': self.last_changed,
            'last_updated': self.last_updated,
        }


class HomeAssistantBridge:
    """
    Home Assistant REST API bridge.

    Features:
    - Entity state queries
    - Service calls (turn on/off, etc.)
    - State change monitoring
    - Automation triggers
    - Scene activation
    """

    def __init__(self, api_config, world_state=None):
        """
        Initialize Home Assistant bridge.

        Args:
            api_config: APIConfig instance
            world_state: Optional WorldState for state sharing
        """
        self.config = api_config
        self.world_state = world_state

        # Configuration
        self.base_url = self.config.homeassistant['url'].rstrip('/')
        self.token = self.config.homeassistant['token']
        self.verify_ssl = self.config.homeassistant['verify_ssl']

        # API endpoints
        self.api_url = f"{self.base_url}/api"

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        })
        if not self.verify_ssl:
            self.session.verify = False

        # Entity cache
        self.entity_cache = {}  # entity_id -> Entity
        self.cache_timestamp = 0
        self.cache_ttl = 30  # seconds

        # Statistics
        self.stats = {
            'total_requests': 0,
            'api_calls': 0,
            'service_calls': 0,
            'failed_requests': 0,
            'entities_tracked': 0,
        }

        # Check availability
        self.available = self._check_connection()

        if self.available:
            logger.info("✓ Home Assistant bridge initialized")
        else:
            logger.warning("Home Assistant bridge unavailable")

    def _check_connection(self) -> bool:
        """
        Check if Home Assistant is reachable.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self.token:
            logger.warning("No Home Assistant token configured")
            return False

        try:
            response = self.session.get(f"{self.api_url}/", timeout=5)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Connected to Home Assistant: {data.get('message', 'Unknown version')}")
            return True

        except requests.exceptions.RequestException as e:
            logger.warning(f"Home Assistant connection failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected Home Assistant error: {e}")
            return False

    def get_states(self, refresh: bool = False) -> List[Entity]:
        """
        Get all entity states.

        Args:
            refresh: Force refresh from API (ignore cache)

        Returns:
            List of Entity objects
        """
        self.stats['total_requests'] += 1

        if not self.available:
            return []

        # Check cache
        if not refresh and time.time() - self.cache_timestamp < self.cache_ttl:
            logger.debug("Using cached entity states")
            return list(self.entity_cache.values())

        try:
            self.stats['api_calls'] += 1

            response = self.session.get(f"{self.api_url}/states", timeout=10)
            response.raise_for_status()

            states = response.json()

            # Parse entities
            entities = []
            for state_data in states:
                entity = Entity(
                    entity_id=state_data['entity_id'],
                    state=state_data['state'],
                    friendly_name=state_data['attributes'].get('friendly_name', state_data['entity_id']),
                    attributes=state_data['attributes'],
                    last_changed=state_data['last_changed'],
                    last_updated=state_data['last_updated'],
                )
                entities.append(entity)
                self.entity_cache[entity.entity_id] = entity

            self.cache_timestamp = time.time()
            self.stats['entities_tracked'] = len(entities)

            logger.info(f"✓ Retrieved {len(entities)} entities")

            return entities

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get states: {e}")
            self.stats['failed_requests'] += 1
            return []

        except Exception as e:
            logger.error(f"Unexpected error getting states: {e}")
            self.stats['failed_requests'] += 1
            return []

    def get_entity(self, entity_id: str, refresh: bool = False) -> Optional[Entity]:
        """
        Get a specific entity's state.

        Args:
            entity_id: Entity ID (e.g., 'light.living_room')
            refresh: Force refresh from API

        Returns:
            Entity object or None
        """
        self.stats['total_requests'] += 1

        if not self.available:
            return None

        # Check cache first
        if not refresh and entity_id in self.entity_cache:
            if time.time() - self.cache_timestamp < self.cache_ttl:
                logger.debug(f"Using cached state for {entity_id}")
                return self.entity_cache[entity_id]

        try:
            self.stats['api_calls'] += 1

            response = self.session.get(f"{self.api_url}/states/{entity_id}", timeout=5)
            response.raise_for_status()

            state_data = response.json()

            entity = Entity(
                entity_id=state_data['entity_id'],
                state=state_data['state'],
                friendly_name=state_data['attributes'].get('friendly_name', state_data['entity_id']),
                attributes=state_data['attributes'],
                last_changed=state_data['last_changed'],
                last_updated=state_data['last_updated'],
            )

            # Update cache
            self.entity_cache[entity_id] = entity

            logger.debug(f"✓ Got state for {entity_id}: {entity.state}")

            return entity

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            self.stats['failed_requests'] += 1
            return None

        except Exception as e:
            logger.error(f"Unexpected error getting entity: {e}")
            self.stats['failed_requests'] += 1
            return None

    def call_service(self, domain: str, service: str, entity_id: Optional[str] = None,
                     service_data: Optional[Dict] = None) -> bool:
        """
        Call a Home Assistant service.

        Args:
            domain: Service domain (e.g., 'light', 'switch')
            service: Service name (e.g., 'turn_on', 'turn_off')
            entity_id: Target entity ID (optional)
            service_data: Additional service data (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        self.stats['total_requests'] += 1
        self.stats['service_calls'] += 1

        if not self.available:
            logger.warning(f"Cannot call service {domain}.{service}: Bridge unavailable")
            return False

        try:
            # Build service data
            data = service_data or {}
            if entity_id:
                data['entity_id'] = entity_id

            logger.info(f"Calling service: {domain}.{service} on {entity_id or 'all entities'}")

            self.stats['api_calls'] += 1

            response = self.session.post(
                f"{self.api_url}/services/{domain}/{service}",
                json=data,
                timeout=10
            )

            response.raise_for_status()

            logger.info(f"✓ Service call successful: {domain}.{service}")

            # Invalidate cache for affected entity
            if entity_id and entity_id in self.entity_cache:
                del self.entity_cache[entity_id]

            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Service call failed: {e}")
            self.stats['failed_requests'] += 1
            return False

        except Exception as e:
            logger.error(f"Unexpected error calling service: {e}")
            self.stats['failed_requests'] += 1
            return False

    def turn_on(self, entity_id: str, **kwargs) -> bool:
        """
        Turn on a device.

        Args:
            entity_id: Entity ID
            **kwargs: Additional service data (brightness, color, etc.)

        Returns:
            bool: Success status
        """
        domain = entity_id.split('.')[0]
        return self.call_service(domain, 'turn_on', entity_id, kwargs if kwargs else None)

    def turn_off(self, entity_id: str) -> bool:
        """
        Turn off a device.

        Args:
            entity_id: Entity ID

        Returns:
            bool: Success status
        """
        domain = entity_id.split('.')[0]
        return self.call_service(domain, 'turn_off', entity_id)

    def toggle(self, entity_id: str) -> bool:
        """
        Toggle a device.

        Args:
            entity_id: Entity ID

        Returns:
            bool: Success status
        """
        domain = entity_id.split('.')[0]
        return self.call_service(domain, 'toggle', entity_id)

    def activate_scene(self, scene_id: str) -> bool:
        """
        Activate a scene.

        Args:
            scene_id: Scene entity ID (e.g., 'scene.movie_time')

        Returns:
            bool: Success status
        """
        return self.call_service('scene', 'turn_on', scene_id)

    def get_entities_by_domain(self, domain: str) -> List[Entity]:
        """
        Get all entities for a specific domain.

        Args:
            domain: Entity domain (e.g., 'light', 'switch')

        Returns:
            List of Entity objects
        """
        all_entities = self.get_states()
        return [e for e in all_entities if e.domain == domain]

    def get_entities_by_state(self, state: str) -> List[Entity]:
        """
        Get all entities with a specific state.

        Args:
            state: State value (e.g., 'on', 'off', 'home')

        Returns:
            List of Entity objects
        """
        all_entities = self.get_states()
        return [e for e in all_entities if e.state == state]

    def summarize_state(self) -> str:
        """
        Create natural language summary of smart home state.

        Returns:
            str: Summary text
        """
        if not self.available:
            return "Smart home system is not available."

        entities = self.get_states()

        if not entities:
            return "No smart home devices found."

        # Count by domain
        domain_counts = {}
        for entity in entities:
            domain_counts[entity.domain] = domain_counts.get(entity.domain, 0) + 1

        # Count lights that are on
        lights = self.get_entities_by_domain('light')
        lights_on = [l for l in lights if l.state == 'on']

        # Count switches that are on
        switches = self.get_entities_by_domain('switch')
        switches_on = [s for s in switches if s.state == 'on']

        summary_parts = [
            f"Smart Home Status ({len(entities)} total devices):"
        ]

        if lights:
            summary_parts.append(f"  Lights: {len(lights_on)}/{len(lights)} on")

        if switches:
            summary_parts.append(f"  Switches: {len(switches_on)}/{len(switches)} on")

        # Add other domains
        for domain, count in sorted(domain_counts.items()):
            if domain not in ['light', 'switch']:
                summary_parts.append(f"  {domain.replace('_', ' ').title()}: {count}")

        return "\n".join(summary_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return {
            **self.stats,
            'available': self.available,
            'cached_entities': len(self.entity_cache),
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"HomeAssistantBridge(available={self.available}, entities={self.stats['entities_tracked']})"


# Test function
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from api_config import get_api_config

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Home Assistant Bridge Test")
    print("=" * 80)

    config = get_api_config()
    bridge = HomeAssistantBridge(config)

    print(f"\nBridge: {bridge}")
    print(f"Available: {bridge.available}")

    if bridge.available:
        # Get all entities
        print("\nFetching entities...")
        entities = bridge.get_states()

        print(f"\nFound {len(entities)} entities")

        # Show lights
        lights = bridge.get_entities_by_domain('light')
        if lights:
            print(f"\nLights ({len(lights)}):")
            for light in lights[:5]:  # Show first 5
                print(f"  - {light.friendly_name}: {light.state}")

        # Show summary
        print("\n" + "-" * 80)
        print("\nSummary:")
        print(bridge.summarize_state())

        print(f"\nStats: {bridge.get_stats()}")

    else:
        print("\nHome Assistant not available. Check configuration in .env")
        print("Required: HOMEASSISTANT_URL and HOMEASSISTANT_TOKEN")

    print("=" * 80)
