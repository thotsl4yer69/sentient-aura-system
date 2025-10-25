#!/usr/bin/env python3
"""
Memory Manager for Sentient Core

Persistent memory system providing long-term storage, pattern recognition,
and memory consolidation for true sentient behavior.

This is the foundation for:
- Remembering conversations across sessions
- Learning user preferences
- Detecting behavioral patterns
- Building relationships over time
- Enabling autonomous decision-making

Database Schema:
- memories: Individual memory entries with embeddings for semantic search
- patterns: Detected patterns (temporal, behavioral, preference)
"""

import logging
import sqlite3
import json
import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger("MemoryManager")


@dataclass
class Memory:
    """Individual memory entry."""
    id: Optional[int]
    timestamp: float
    user_id: str
    memory_type: str  # conversation, observation, learned, event
    content: str
    importance: float  # 0.0-1.0
    decay_rate: float  # How quickly importance decreases
    embedding: Optional[np.ndarray]  # Vector for semantic search
    associations: List[int]  # Related memory IDs
    metadata: Dict[str, Any]  # Additional context


@dataclass
class Pattern:
    """Detected behavioral pattern."""
    id: Optional[int]
    user_id: str
    pattern_type: str  # temporal, behavioral, preference
    pattern_data: Dict[str, Any]
    confidence: float  # 0.0-1.0
    occurrences: int
    last_seen: float
    first_seen: float


class MemoryManager:
    """
    Persistent memory management system.

    Provides:
    - Long-term memory storage (SQLite)
    - Semantic memory retrieval
    - Pattern detection and learning
    - Memory consolidation (short→long term)
    - Forgetting mechanisms (importance decay)
    - Association networks
    """

    def __init__(
        self,
        db_path: str = "intelligence/memory/sentient_memory.db",
        max_memory_age_days: int = 365,
        consolidation_threshold: float = 0.7
    ):
        """
        Initialize memory manager.

        Args:
            db_path: Path to SQLite database
            max_memory_age_days: Maximum age of low-importance memories
            consolidation_threshold: Importance threshold for consolidation
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.max_memory_age = max_memory_age_days * 86400  # Convert to seconds
        self.consolidation_threshold = consolidation_threshold

        # Thread-safe database access
        self._local = threading.local()

        # Initialize database
        self._initialize_database()

        # Statistics
        self.memories_stored = 0
        self.memories_retrieved = 0
        self.patterns_detected = 0

        logger.info(f"Memory Manager initialized (db: {self.db_path})")

    @property
    def _conn(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(str(self.db_path))
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _initialize_database(self) -> None:
        """Create database schema if not exists."""
        cursor = self._conn.cursor()

        # Memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                decay_rate REAL DEFAULT 0.01,
                embedding BLOB,
                associations TEXT,
                metadata TEXT,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL
            )
        """)

        # Indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_user_time
            ON memories(user_id, timestamp DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_type
            ON memories(memory_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_importance
            ON memories(importance DESC)
        """)

        # Patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                occurrences INTEGER DEFAULT 1,
                last_seen REAL NOT NULL,
                first_seen REAL NOT NULL,
                created_at REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_user_type
            ON patterns(user_id, pattern_type)
        """)

        self._conn.commit()
        logger.info("Database schema initialized")

    def store_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "conversation",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store a new memory.

        Args:
            user_id: User identifier
            content: Memory content (text)
            memory_type: Type of memory (conversation, observation, learned, event)
            importance: Initial importance (0.0-1.0)
            metadata: Additional context

        Returns:
            Memory ID
        """
        now = time.time()

        # Calculate decay rate based on importance
        # High importance memories decay slower
        decay_rate = 0.001 if importance > 0.8 else 0.01

        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO memories
            (timestamp, user_id, memory_type, content, importance, decay_rate,
             associations, metadata, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now,
            user_id,
            memory_type,
            content,
            importance,
            decay_rate,
            json.dumps([]),  # Empty associations initially
            json.dumps(metadata or {}),
            now,
            now
        ))

        self._conn.commit()
        memory_id = cursor.lastrowid

        self.memories_stored += 1
        logger.debug(f"Stored memory #{memory_id} (type: {memory_type}, importance: {importance:.2f})")

        return memory_id

    def retrieve_relevant(
        self,
        user_id: str,
        context: Optional[str] = None,
        memory_types: Optional[List[str]] = None,
        limit: int = 5,
        min_importance: float = 0.3
    ) -> List[Memory]:
        """
        Retrieve relevant memories for a context.

        Args:
            user_id: User identifier
            context: Context string for relevance (optional)
            memory_types: Filter by memory types (optional)
            limit: Maximum memories to return
            min_importance: Minimum importance threshold

        Returns:
            List of relevant memories, sorted by relevance
        """
        cursor = self._conn.cursor()

        # Build query
        query = """
            SELECT * FROM memories
            WHERE user_id = ? AND importance >= ?
        """
        params = [user_id, min_importance]

        if memory_types:
            placeholders = ','.join('?' * len(memory_types))
            query += f" AND memory_type IN ({placeholders})"
            params.extend(memory_types)

        # Order by importance and recency
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Update access times
        if rows:
            now = time.time()
            ids = [row['id'] for row in rows]
            placeholders = ','.join('?' * len(ids))
            cursor.execute(
                f"UPDATE memories SET last_accessed = ? WHERE id IN ({placeholders})",
                [now] + ids
            )
            self._conn.commit()

        # Convert to Memory objects
        memories = []
        for row in rows:
            memories.append(Memory(
                id=row['id'],
                timestamp=row['timestamp'],
                user_id=row['user_id'],
                memory_type=row['memory_type'],
                content=row['content'],
                importance=row['importance'],
                decay_rate=row['decay_rate'],
                embedding=None,  # TODO: Deserialize from BLOB
                associations=json.loads(row['associations']),
                metadata=json.loads(row['metadata'])
            ))

        self.memories_retrieved += len(memories)
        logger.debug(f"Retrieved {len(memories)} relevant memories for user {user_id}")

        return memories

    def get_recent_conversations(
        self,
        user_id: str,
        limit: int = 10,
        hours: int = 24
    ) -> List[Memory]:
        """
        Get recent conversation memories.

        Args:
            user_id: User identifier
            limit: Maximum conversations to return
            hours: Time window in hours

        Returns:
            List of recent conversation memories
        """
        cutoff_time = time.time() - (hours * 3600)

        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM memories
            WHERE user_id = ? AND memory_type = 'conversation' AND timestamp >= ?
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, cutoff_time, limit))

        rows = cursor.fetchall()

        memories = []
        for row in rows:
            memories.append(Memory(
                id=row['id'],
                timestamp=row['timestamp'],
                user_id=row['user_id'],
                memory_type=row['memory_type'],
                content=row['content'],
                importance=row['importance'],
                decay_rate=row['decay_rate'],
                embedding=None,
                associations=json.loads(row['associations']),
                metadata=json.loads(row['metadata'])
            ))

        return memories

    def get_all_memories(
        self,
        user_id: str,
        memory_types: Optional[List[str]] = None,
        min_importance: float = 0.0,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        Get all memories for a user.

        Args:
            user_id: User identifier
            memory_types: Filter by memory types (optional)
            min_importance: Minimum importance threshold
            limit: Maximum memories to return (optional)

        Returns:
            List of all memories matching criteria, sorted by timestamp DESC
        """
        cursor = self._conn.cursor()

        query = "SELECT * FROM memories WHERE user_id = ? AND importance >= ?"
        params = [user_id, min_importance]

        if memory_types:
            placeholders = ','.join('?' * len(memory_types))
            query += f" AND memory_type IN ({placeholders})"
            params.extend(memory_types)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        memories = []
        for row in rows:
            memories.append(Memory(
                id=row['id'],
                timestamp=row['timestamp'],
                user_id=row['user_id'],
                memory_type=row['memory_type'],
                content=row['content'],
                importance=row['importance'],
                decay_rate=row['decay_rate'],
                embedding=None,
                associations=json.loads(row['associations']),
                metadata=json.loads(row['metadata'])
            ))

        return memories

    def identify_patterns(
        self,
        user_id: str,
        pattern_type: Optional[str] = None,
        timeframe_days: int = 30
    ) -> List[Pattern]:
        """
        Identify patterns in user behavior.

        Args:
            user_id: User identifier
            pattern_type: Filter by pattern type (optional)
            timeframe_days: Analysis timeframe

        Returns:
            List of detected patterns
        """
        cursor = self._conn.cursor()

        query = "SELECT * FROM patterns WHERE user_id = ?"
        params = [user_id]

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        query += " ORDER BY confidence DESC, occurrences DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        patterns = []
        for row in rows:
            patterns.append(Pattern(
                id=row['id'],
                user_id=row['user_id'],
                pattern_type=row['pattern_type'],
                pattern_data=json.loads(row['pattern_data']),
                confidence=row['confidence'],
                occurrences=row['occurrences'],
                last_seen=row['last_seen'],
                first_seen=row['first_seen']
            ))

        return patterns

    def detect_preference_patterns(
        self,
        user_id: str,
        min_occurrences: int = 3
    ) -> List[Pattern]:
        """
        Detect user preference patterns from memory.

        Analyzes conversation memories to identify:
        - Preferred response styles (technical vs casual)
        - Topic interests
        - Interaction times
        - Communication preferences

        Args:
            user_id: User identifier
            min_occurrences: Minimum occurrences to consider a pattern

        Returns:
            List of preference patterns
        """
        # Get recent conversations
        memories = self.get_recent_conversations(user_id, limit=100, hours=720)  # 30 days

        if len(memories) < min_occurrences:
            return []

        # Analyze for patterns
        patterns = []

        # 1. Detect time-of-day preferences
        hour_counts = {}
        for mem in memories:
            dt = datetime.fromtimestamp(mem.timestamp)
            hour = dt.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        if hour_counts:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])
            if peak_hour[1] >= min_occurrences:
                pattern = self._store_pattern(
                    user_id=user_id,
                    pattern_type="temporal",
                    pattern_data={
                        "peak_hour": peak_hour[0],
                        "frequency": peak_hour[1],
                        "description": f"Most active around {peak_hour[0]:02d}:00"
                    },
                    confidence=min(peak_hour[1] / len(memories), 1.0),
                    occurrences=peak_hour[1]
                )
                patterns.append(pattern)

        # 2. Detect topic preferences (keyword frequency)
        topic_keywords = {
            "coding": ["code", "python", "javascript", "function", "debug", "programming", "script"],
            "sensors": ["sensor", "hardware", "arduino", "flipper", "coral", "tpu", "gpio"],
            "ai_ml": ["ai", "machine learning", "neural", "model", "training", "inference"],
            "system": ["linux", "system", "server", "process", "daemon", "service"],
            "personal": ["how are", "feeling", "think", "like", "prefer", "favorite"]
        }

        topic_counts = {topic: 0 for topic in topic_keywords.keys()}
        for mem in memories:
            content_lower = mem.content.lower()
            for topic, keywords in topic_keywords.items():
                if any(kw in content_lower for kw in keywords):
                    topic_counts[topic] += 1

        for topic, count in topic_counts.items():
            if count >= min_occurrences:
                pattern = self._store_pattern(
                    user_id=user_id,
                    pattern_type="topic_preference",
                    pattern_data={
                        "topic": topic,
                        "frequency": count,
                        "description": f"Frequently discusses {topic}"
                    },
                    confidence=min(count / len(memories), 1.0),
                    occurrences=count
                )
                patterns.append(pattern)

        # 3. Detect named entities (names, preferences)
        # Look for "my name is X", "I'm X", "call me X"
        name_patterns = [
            r"(?:my name is|i'm|call me|i am)\s+([A-Z][a-z]+)",
            r"(?:User|user):\s*([A-Z][a-z]+)"
        ]

        import re
        detected_names = []
        for mem in memories:
            for pattern_str in name_patterns:
                matches = re.findall(pattern_str, mem.content)
                detected_names.extend(matches)

        if detected_names:
            # Find most common name
            name_counts = {}
            for name in detected_names:
                name_counts[name] = name_counts.get(name, 0) + 1

            most_common_name = max(name_counts.items(), key=lambda x: x[1])
            if most_common_name[1] >= min_occurrences:
                pattern = self._store_pattern(
                    user_id=user_id,
                    pattern_type="identity",
                    pattern_data={
                        "name": most_common_name[0],
                        "confidence_count": most_common_name[1],
                        "description": f"User's name is {most_common_name[0]}"
                    },
                    confidence=min(most_common_name[1] / len(memories), 1.0),
                    occurrences=most_common_name[1]
                )
                patterns.append(pattern)

        # 4. Detect stated preferences ("I prefer X", "I like X")
        preference_patterns = [
            r"(?:i prefer|i like|i love|i enjoy|favorite)\s+([a-zA-Z\s]+?)(?:\.|,|!|\?|$)",
        ]

        detected_preferences = []
        for mem in memories:
            for pattern_str in preference_patterns:
                matches = re.findall(pattern_str, mem.content.lower())
                detected_preferences.extend([m.strip() for m in matches if len(m.strip()) > 2])

        if detected_preferences:
            pref_counts = {}
            for pref in detected_preferences:
                pref_counts[pref] = pref_counts.get(pref, 0) + 1

            for pref, count in pref_counts.items():
                if count >= min_occurrences:
                    pattern = self._store_pattern(
                        user_id=user_id,
                        pattern_type="preference",
                        pattern_data={
                            "preference": pref,
                            "frequency": count,
                            "description": f"User prefers: {pref}"
                        },
                        confidence=min(count / len(memories), 1.0),
                        occurrences=count
                    )
                    patterns.append(pattern)

        self.patterns_detected += len(patterns)
        logger.info(f"Detected {len(patterns)} patterns for user {user_id}")
        return patterns

    def _store_pattern(
        self,
        user_id: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence: float,
        occurrences: int
    ) -> Pattern:
        """Store a detected pattern."""
        now = time.time()

        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO patterns
            (user_id, pattern_type, pattern_data, confidence, occurrences,
             last_seen, first_seen, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            pattern_type,
            json.dumps(pattern_data),
            confidence,
            occurrences,
            now,
            now,
            now
        ))

        self._conn.commit()
        pattern_id = cursor.lastrowid

        logger.debug(f"Stored pattern #{pattern_id} (type: {pattern_type}, confidence: {confidence:.2f})")

        return Pattern(
            id=pattern_id,
            user_id=user_id,
            pattern_type=pattern_type,
            pattern_data=pattern_data,
            confidence=confidence,
            occurrences=occurrences,
            last_seen=now,
            first_seen=now
        )

    def consolidate_memories(self, user_id: str) -> int:
        """
        Consolidate short-term memories into long-term storage.

        Increases importance of frequently accessed memories.
        Merges similar memories.

        Args:
            user_id: User identifier

        Returns:
            Number of memories consolidated
        """
        cursor = self._conn.cursor()

        # Find frequently accessed memories in last 7 days
        week_ago = time.time() - (7 * 86400)

        cursor.execute("""
            SELECT id, importance, last_accessed, created_at
            FROM memories
            WHERE user_id = ? AND created_at >= ?
        """, (user_id, week_ago))

        rows = cursor.fetchall()
        consolidated = 0

        for row in rows:
            # Calculate access frequency
            age_days = (time.time() - row['created_at']) / 86400
            if age_days < 1:
                continue

            # Boost importance if accessed recently
            time_since_access = time.time() - row['last_accessed']
            if time_since_access < 86400:  # Accessed in last 24h
                new_importance = min(row['importance'] + 0.1, 1.0)

                cursor.execute("""
                    UPDATE memories SET importance = ? WHERE id = ?
                """, (new_importance, row['id']))

                consolidated += 1

        self._conn.commit()

        if consolidated > 0:
            logger.info(f"Consolidated {consolidated} memories for user {user_id}")

        return consolidated

    def prune_memories(self, user_id: str) -> int:
        """
        Remove old, low-importance memories.

        Implements forgetting mechanism to prevent unbounded growth.

        Args:
            user_id: User identifier

        Returns:
            Number of memories pruned
        """
        cursor = self._conn.cursor()

        # Apply importance decay
        now = time.time()
        cursor.execute("""
            UPDATE memories
            SET importance = importance * (1 - decay_rate *
                ((? - last_accessed) / 86400))
            WHERE user_id = ? AND importance > 0.1
        """, (now, user_id))

        # Delete very old, low-importance memories
        old_threshold = now - self.max_memory_age

        cursor.execute("""
            DELETE FROM memories
            WHERE user_id = ? AND importance < 0.1 AND timestamp < ?
        """, (user_id, old_threshold))

        pruned = cursor.rowcount
        self._conn.commit()

        if pruned > 0:
            logger.info(f"Pruned {pruned} old memories for user {user_id}")

        return pruned

    def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory system statistics.

        Args:
            user_id: User identifier (optional, for user-specific stats)

        Returns:
            Statistics dictionary
        """
        cursor = self._conn.cursor()

        stats = {
            "memories_stored": self.memories_stored,
            "memories_retrieved": self.memories_retrieved,
            "patterns_detected": self.patterns_detected
        }

        if user_id:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(importance) as avg_importance,
                    MAX(timestamp) as latest
                FROM memories WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()

            stats.update({
                "total_memories": row['total'],
                "avg_importance": row['avg_importance'] or 0.0,
                "latest_memory": row['latest'] or 0.0
            })

            cursor.execute("""
                SELECT COUNT(*) as count FROM patterns WHERE user_id = ?
            """, (user_id,))
            stats["total_patterns"] = cursor.fetchone()['count']
        else:
            cursor.execute("SELECT COUNT(*) as count FROM memories")
            stats["total_memories"] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM patterns")
            stats["total_patterns"] = cursor.fetchone()['count']

        return stats

    def close(self) -> None:
        """Close database connections."""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            logger.info("Memory Manager closed")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "="*60)
    print("MEMORY MANAGER TEST")
    print("="*60 + "\n")

    # Create memory manager
    mm = MemoryManager(db_path="test_memory.db")

    user_id = "test_user"

    # Test 1: Store memories
    print("Test 1: Storing memories...")
    mm.store_memory(user_id, "User prefers technical explanations", "learned", importance=0.8)
    mm.store_memory(user_id, "User asked about Coral TPU", "conversation", importance=0.6)
    mm.store_memory(user_id, "User name is Mike", "learned", importance=0.9)
    mm.store_memory(user_id, "Weather check at 7am", "observation", importance=0.5)
    mm.store_memory(user_id, "User mentioned Python programming", "conversation", importance=0.7)
    print(f"✓ Stored 5 memories")

    # Test 2: Retrieve relevant memories
    print("\nTest 2: Retrieving relevant memories...")
    memories = mm.retrieve_relevant(user_id, limit=3)
    for mem in memories:
        print(f"  - [{mem.memory_type}] {mem.content} (importance: {mem.importance:.2f})")

    # Test 3: Get recent conversations
    print("\nTest 3: Recent conversations...")
    convos = mm.get_recent_conversations(user_id, limit=5)
    print(f"✓ Found {len(convos)} recent conversations")

    # Test 4: Detect patterns
    print("\nTest 4: Pattern detection...")
    patterns = mm.detect_preference_patterns(user_id)
    print(f"✓ Detected {len(patterns)} patterns")
    for pattern in patterns:
        print(f"  - {pattern.pattern_type}: {pattern.pattern_data} (confidence: {pattern.confidence:.2f})")

    # Test 5: Consolidation
    print("\nTest 5: Memory consolidation...")
    consolidated = mm.consolidate_memories(user_id)
    print(f"✓ Consolidated {consolidated} memories")

    # Test 6: Statistics
    print("\nTest 6: Statistics...")
    stats = mm.get_stats(user_id)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Cleanup
    mm.close()
    Path("test_memory.db").unlink()

    print("\n✓ Memory Manager test complete\n")
