#!/usr/bin/env python3
"""
Hierarchical Temporal Memory System

Three-tier memory architecture based on cognitive science and 2024 AI research:
1. Working Memory: Current 5 seconds (high detail, high temporal resolution)
2. Episodic Memory: Key events from last session (event-based, selective)
3. Semantic Memory: Long-term patterns (compressed, knowledge-based)

Includes graph-based memory indexing for traversable temporal and semantic links.

Reference: "Rethinking Memory in AI" (2024), "3DLLM-Mem" (2024)
"""

import numpy as np
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class MemoryEvent:
    """Single memory event/observation."""
    timestamp: float
    observation: Dict[str, Any]
    importance: float = 0.5
    emotional_valence: float = 0.5
    tags: List[str] = field(default_factory=list)
    event_id: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'observation': self.observation,
            'importance': self.importance,
            'emotional_valence': self.emotional_valence,
            'tags': self.tags,
            'event_id': self.event_id
        }


class TemporalGraph:
    """
    Graph structure for traversable memory indices.

    Nodes: Memory events
    Edges: Temporal (before/after) and semantic (similar to) links
    """

    def __init__(self):
        self.nodes: List[MemoryEvent] = []
        self.edges: Dict[Tuple[int, int], List[str]] = defaultdict(list)

    def add_event(self, event: MemoryEvent,
                  temporal_links: List[int] = None,
                  semantic_links: List[int] = None) -> int:
        """
        Add event to graph with temporal and semantic links.

        Args:
            event: Memory event to add
            temporal_links: IDs of temporally nearby events
            semantic_links: IDs of semantically similar events

        Returns:
            Node ID of added event
        """
        node_id = len(self.nodes)
        event.event_id = node_id
        self.nodes.append(event)

        # Add temporal edges (bidirectional)
        if temporal_links:
            for neighbor_id in temporal_links:
                if 0 <= neighbor_id < len(self.nodes):
                    self.edges[(node_id, neighbor_id)].append('temporal')
                    self.edges[(neighbor_id, node_id)].append('temporal')

        # Add semantic edges (bidirectional)
        if semantic_links:
            for neighbor_id in semantic_links:
                if 0 <= neighbor_id < len(self.nodes):
                    self.edges[(node_id, neighbor_id)].append('semantic')
                    self.edges[(neighbor_id, node_id)].append('semantic')

        return node_id

    def get_neighbors(self, node_id: int, edge_type: Optional[str] = None) -> List[int]:
        """
        Get neighboring nodes.

        Args:
            node_id: Node to find neighbors for
            edge_type: Filter by edge type ('temporal', 'semantic', or None for all)

        Returns:
            List of neighbor node IDs
        """
        neighbors = []
        for (src, dst), types in self.edges.items():
            if src == node_id:
                if edge_type is None or edge_type in types:
                    neighbors.append(dst)
        return neighbors

    def query(self, query_features: Dict,
              temporal_weight: float = 0.3,
              semantic_weight: float = 0.7,
              k: int = 5) -> List[MemoryEvent]:
        """
        Retrieve k most relevant memories.

        Args:
            query_features: Query to match against
            temporal_weight: Weight for temporal relevance (0-1)
            semantic_weight: Weight for semantic similarity (0-1)
            k: Number of results to return

        Returns:
            List of most relevant memory events
        """
        if not self.nodes:
            return []

        # Score all nodes
        scores = []
        current_time = time.time()

        for node in self.nodes:
            # Temporal score (recency)
            time_diff = current_time - node.timestamp
            temporal_score = np.exp(-time_diff / 3600.0)  # Decay over hours

            # Semantic score (similarity)
            semantic_score = self._compute_similarity(query_features, node.observation)

            # Combined score
            total_score = (temporal_weight * temporal_score +
                          semantic_weight * semantic_score)

            scores.append((total_score, node))

        # Sort by score and return top k
        scores.sort(key=lambda x: x[0], reverse=True)
        return [node for score, node in scores[:k]]

    def _compute_similarity(self, query: Dict, observation: Dict) -> float:
        """
        Compute semantic similarity between query and observation.

        Simple implementation - could be replaced with learned embeddings.
        """
        # Check for tag overlap
        query_tags = set(query.get('tags', []))
        obs_tags = set(observation.get('tags', []))

        if query_tags and obs_tags:
            jaccard = len(query_tags & obs_tags) / len(query_tags | obs_tags)
            return jaccard

        # Check for activity match
        if query.get('activity') == observation.get('activity'):
            return 0.8

        # Default similarity
        return 0.3


class HierarchicalTemporalMemory:
    """
    Three-tier hierarchical memory system.

    Tier 1 (Working Memory): 5 seconds, full detail
    Tier 2 (Episodic Memory): Key events, selective storage
    Tier 3 (Semantic Memory): Compressed patterns, long-term knowledge
    """

    def __init__(self, working_memory_size: int = 5,
                 max_episodes: int = 100):
        """
        Initialize hierarchical memory.

        Args:
            working_memory_size: Number of recent observations to keep
            max_episodes: Maximum episodic memories before compression
        """
        # Tier 1: Working Memory (high temporal resolution)
        self.working_memory = deque(maxlen=working_memory_size)

        # Tier 2: Episodic Memory (event-based, selective)
        self.episodic_memory: List[MemoryEvent] = []
        self.max_episodes = max_episodes

        # Tier 3: Semantic Memory (compressed patterns)
        self.semantic_memory = {
            'user_patterns': {},      # "User usually enters at 6pm"
            'environmental_patterns': {},  # "Room is quiet on weekends"
            'interaction_history': {},     # "User likes playful mode"
            'learned_associations': {}     # "Sound of door → user arriving"
        }

        # Memory graph for indexing
        self.memory_graph = TemporalGraph()

        # Statistics
        self.total_observations = 0
        self.memorable_events_count = 0

        logger.info("Hierarchical memory initialized (working=%d, max_episodes=%d)",
                   working_memory_size, max_episodes)

    def store_observation(self, observation: Dict[str, Any]) -> bool:
        """
        Store observation in appropriate memory tier(s).

        Args:
            observation: Current observation/context

        Returns:
            True if observation was memorable (stored in episodic memory)
        """
        self.total_observations += 1

        # Always add to working memory
        self.working_memory.append({
            'timestamp': time.time(),
            'observation': observation
        })

        # Check if observation is memorable (worthy of episodic storage)
        if self._is_memorable(observation):
            importance = self._calculate_importance(observation)
            emotional_valence = observation.get('emotion', {}).get('valence', 0.5)

            event = MemoryEvent(
                timestamp=time.time(),
                observation=observation,
                importance=importance,
                emotional_valence=emotional_valence,
                tags=self._extract_tags(observation)
            )

            self.episodic_memory.append(event)
            self.memorable_events_count += 1

            # Add to memory graph
            temporal_links = self._find_temporal_neighbors()
            semantic_links = self._find_semantic_neighbors(event)

            self.memory_graph.add_event(
                event=event,
                temporal_links=temporal_links,
                semantic_links=semantic_links
            )

            logger.debug("Memorable event stored: %s (importance=%.2f)",
                        event.tags, importance)

            # Periodically compress episodic → semantic
            if len(self.episodic_memory) > self.max_episodes:
                self._compress_to_semantic()

            return True

        return False

    def _is_memorable(self, observation: Dict) -> bool:
        """
        Determine if observation should be stored in episodic memory.

        Memorable events:
        - High emotional arousal
        - User interactions
        - Novel/unexpected occurrences
        - Important environmental changes
        """
        # High arousal
        if observation.get('emotion', {}).get('arousal', 0) > 0.7:
            return True

        # User detected (always memorable)
        if observation.get('vision', {}).get('people_count', 0) > 0:
            return True

        # User interaction
        if observation.get('user_interaction', False):
            return True

        # Novel event
        if observation.get('novel_event', False):
            return True

        # Danger detected
        if observation.get('danger_detected', False):
            return True

        # Significant environmental change
        if observation.get('scene_change_magnitude', 0) > 0.5:
            return True

        return False

    def _calculate_importance(self, observation: Dict) -> float:
        """
        Calculate importance score for observation.

        Returns:
            Importance score [0, 1]
        """
        importance = 0.5

        # User interaction is highly important
        if observation.get('user_interaction', False):
            importance += 0.3

        # Danger is critical
        if observation.get('danger_detected', False):
            importance += 0.4

        # Emotional arousal
        arousal = observation.get('emotion', {}).get('arousal', 0)
        importance += arousal * 0.2

        # Novel events are important
        if observation.get('novel_event', False):
            importance += 0.2

        return min(importance, 1.0)

    def _extract_tags(self, observation: Dict) -> List[str]:
        """Extract semantic tags from observation for indexing."""
        tags = []

        # Activity tags
        if 'activity' in observation:
            tags.append(f"activity:{observation['activity']}")

        # Person detection
        if observation.get('vision', {}).get('people_count', 0) > 0:
            tags.append('person_present')

        # Emotion tags
        if 'emotion' in observation:
            emotion = observation['emotion']
            if isinstance(emotion, dict) and 'state' in emotion:
                tags.append(f"emotion:{emotion['state']}")

        # Time of day
        hour = datetime.now().hour
        if 6 <= hour < 12:
            tags.append('time:morning')
        elif 12 <= hour < 18:
            tags.append('time:afternoon')
        elif 18 <= hour < 22:
            tags.append('time:evening')
        else:
            tags.append('time:night')

        return tags

    def _find_temporal_neighbors(self, window: int = 5) -> List[int]:
        """
        Find temporally nearby events (last N events).

        Args:
            window: Number of recent events to link

        Returns:
            List of event IDs
        """
        if len(self.episodic_memory) < 2:
            return []

        # Get last few events
        recent_count = min(window, len(self.episodic_memory) - 1)
        start_idx = len(self.episodic_memory) - recent_count - 1

        return list(range(start_idx, len(self.episodic_memory) - 1))

    def _find_semantic_neighbors(self, event: MemoryEvent, k: int = 3) -> List[int]:
        """
        Find semantically similar past events.

        Args:
            event: New event to find neighbors for
            k: Number of neighbors to find

        Returns:
            List of event IDs
        """
        if len(self.episodic_memory) < 2:
            return []

        # Compute similarity with all past events
        similarities = []
        event_tags = set(event.tags)

        for past_event in self.episodic_memory[:-1]:  # Exclude current event
            past_tags = set(past_event.tags)

            # Jaccard similarity on tags
            if event_tags and past_tags:
                similarity = len(event_tags & past_tags) / len(event_tags | past_tags)
            else:
                similarity = 0.0

            if past_event.event_id is not None:
                similarities.append((similarity, past_event.event_id))

        # Return top k most similar
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [event_id for similarity, event_id in similarities[:k] if similarity > 0.3]

    def retrieve_context(self, query: Dict, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant past experiences for current query.

        Args:
            query: Query context/features
            k: Number of memories to retrieve

        Returns:
            List of relevant memory events
        """
        # First check working memory (recent context)
        recent = list(self.working_memory)

        # Then query memory graph for episodic memories
        relevant_events = self.memory_graph.query(
            query_features=query,
            temporal_weight=0.3,
            semantic_weight=0.7,
            k=k
        )

        # Combine and return
        return [e.to_dict() for e in relevant_events]

    def _compress_to_semantic(self):
        """
        Extract patterns from episodic memory → semantic memory.

        Example:
        Episodic: "User entered at 6:02pm, 6:01pm, 5:58pm..."
        Semantic: "User usually enters around 6pm"
        """
        logger.info("Compressing episodic memory to semantic patterns...")

        # Pattern 1: User entry times
        user_entry_times = [
            e.timestamp for e in self.episodic_memory
            if 'person_present' in e.tags or 'user_interaction' in str(e.tags)
        ]

        if len(user_entry_times) > 10:
            # Extract time-of-day pattern
            hour_histogram = defaultdict(int)
            for t in user_entry_times:
                hour = datetime.fromtimestamp(t).hour
                hour_histogram[hour] += 1

            # Find peak hour
            if hour_histogram:
                peak_hour = max(hour_histogram.items(), key=lambda x: x[1])[0]
                self.semantic_memory['user_patterns']['typical_entry_time'] = peak_hour
                logger.debug("Learned pattern: User typically arrives at %d:00", peak_hour)

        # Pattern 2: Activity patterns
        activity_counts = defaultdict(int)
        for e in self.episodic_memory:
            for tag in e.tags:
                if tag.startswith('activity:'):
                    activity_counts[tag] += 1

        if activity_counts:
            common_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            self.semantic_memory['user_patterns']['common_activities'] = [a[0] for a in common_activities]

        # Pattern 3: Emotion-trigger associations
        for e in self.episodic_memory:
            if e.emotional_valence > 0.7:  # Positive emotions
                for tag in e.tags:
                    if tag.startswith('activity:'):
                        self.semantic_memory['learned_associations'][tag] = 'positive'
            elif e.emotional_valence < 0.3:  # Negative emotions
                for tag in e.tags:
                    if tag.startswith('activity:'):
                        self.semantic_memory['learned_associations'][tag] = 'negative'

        # Keep only most important episodic memories
        self.episodic_memory = sorted(
            self.episodic_memory,
            key=lambda e: e.importance,
            reverse=True
        )[:self.max_episodes // 2]

        logger.info("Episodic memory compressed. Retained %d important events.",
                   len(self.episodic_memory))

    def get_semantic_knowledge(self, key: str) -> Any:
        """
        Retrieve semantic knowledge.

        Args:
            key: Knowledge key (e.g., 'user_patterns', 'learned_associations')

        Returns:
            Semantic knowledge or None
        """
        return self.semantic_memory.get(key)

    def get_statistics(self) -> Dict:
        """Get memory system statistics."""
        return {
            'total_observations': self.total_observations,
            'memorable_events': self.memorable_events_count,
            'working_memory_size': len(self.working_memory),
            'episodic_memory_size': len(self.episodic_memory),
            'semantic_patterns': len(self.semantic_memory),
            'graph_nodes': len(self.memory_graph.nodes),
            'graph_edges': len(self.memory_graph.edges)
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create memory system
    memory = HierarchicalTemporalMemory()

    # Simulate observations
    observations = [
        {'user_interaction': True, 'activity': 'working',
         'emotion': {'valence': 0.6, 'arousal': 0.5, 'state': 'focused'}},
        {'vision': {'people_count': 1}, 'activity': 'talking',
         'emotion': {'valence': 0.8, 'arousal': 0.7, 'state': 'happy'}},
        {'novel_event': True, 'activity': 'unknown',
         'emotion': {'valence': 0.5, 'arousal': 0.8, 'state': 'curious'}},
        {'activity': 'working',
         'emotion': {'valence': 0.5, 'arousal': 0.4, 'state': 'calm'}},
    ]

    print("\nHierarchical Temporal Memory Test\n" + "=" * 60)

    for i, obs in enumerate(observations):
        memorable = memory.store_observation(obs)
        print(f"\nObservation {i+1}: memorable={memorable}")
        if memorable:
            print(f"  Tags: {memory.episodic_memory[-1].tags}")
            print(f"  Importance: {memory.episodic_memory[-1].importance:.2f}")

    # Test retrieval
    print("\n\nRetrieving context for query: user interaction")
    query = {'tags': ['person_present'], 'activity': 'talking'}
    context = memory.retrieve_context(query, k=3)

    print(f"Retrieved {len(context)} relevant memories")
    for mem in context:
        print(f"  - {mem['tags']} (importance={mem['importance']:.2f})")

    # Show statistics
    print("\n\nMemory Statistics:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
