#!/usr/bin/env python3
"""
Sentient Core v4 - Memory Manager
PostgreSQL-backed conversation memory and analytics.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("memory_manager")


@dataclass
class ConversationEntry:
    """A single conversation entry."""
    id: Optional[int] = None
    timestamp: float = None
    role: str = "user"  # "user" or "assistant"
    content: str = ""
    intent: Optional[str] = None
    entities: Optional[Dict] = None
    sentiment: Optional[str] = None
    context: Optional[Dict] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'role': self.role,
            'content': self.content,
            'intent': self.intent,
            'entities': self.entities,
            'sentiment': self.sentiment,
            'context': self.context,
        }


class MemoryManager:
    """
    PostgreSQL-backed conversation memory system.

    Features:
    - Long-term conversation storage
    - Semantic search (simple keyword-based)
    - Context retrieval
    - Analytics and insights
    - Automatic summarization
    - Memory cleanup
    """

    def __init__(self, api_config, world_state=None):
        """
        Initialize memory manager.

        Args:
            api_config: APIConfig instance
            world_state: Optional WorldState for context injection
        """
        self.config = api_config
        self.world_state = world_state

        # Database configuration
        self.db_config = {
            'host': self.config.database['host'],
            'port': self.config.database['port'],
            'database': self.config.database['database'],
            'user': self.config.database['user'],
            'password': self.config.database['password'],
        }

        # Connection pool
        self.pool = None
        self.min_connections = self.config.database['min_connections']
        self.max_connections = self.config.database['max_connections']

        # Settings
        self.auto_summarize = self.config.advanced['memory_auto_summarize']
        self.retention_days = self.config.advanced['memory_retention_days']

        # Statistics
        self.stats = {
            'total_entries': 0,
            'queries_executed': 0,
            'cache_hits': 0,
            'failed_operations': 0,
        }

        # Initialize database
        self.available = self._initialize_database()

        if self.available:
            logger.info("✓ Memory manager initialized")
        else:
            logger.warning("Memory manager unavailable: Database connection failed")

    def _initialize_database(self) -> bool:
        """
        Initialize database connection and schema.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create connection pool
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                **self.db_config
            )

            logger.info("Database connection pool created")

            # Create schema if not exists
            self._create_schema()

            return True

        except psycopg2.Error as e:
            logger.error(f"Database initialization failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            return False

    def _create_schema(self):
        """Create database schema for memory storage."""
        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor()

            # Conversation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id SERIAL PRIMARY KEY,
                    timestamp DOUBLE PRECISION NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    intent VARCHAR(100),
                    entities JSONB,
                    sentiment VARCHAR(20),
                    context JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_timestamp
                ON conversation_history(timestamp DESC);
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_role
                ON conversation_history(role);
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_intent
                ON conversation_history(intent);
            """)

            # Sensor data analytics table (optional)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_analytics (
                    id SERIAL PRIMARY KEY,
                    timestamp DOUBLE PRECISION NOT NULL,
                    sensor_type VARCHAR(50) NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp
                ON sensor_analytics(timestamp DESC);
            """)

            # Command history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id SERIAL PRIMARY KEY,
                    timestamp DOUBLE PRECISION NOT NULL,
                    command_id VARCHAR(50),
                    intent VARCHAR(100) NOT NULL,
                    parameters JSONB,
                    status VARCHAR(20),
                    result JSONB,
                    execution_time DOUBLE PRECISION,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_timestamp
                ON command_history(timestamp DESC);
            """)

            conn.commit()
            logger.info("✓ Database schema created/verified")

        except psycopg2.Error as e:
            logger.error(f"Schema creation failed: {e}")
            if conn:
                conn.rollback()

        finally:
            if conn:
                self.pool.putconn(conn)

    def store_conversation(self, role: str, content: str, intent: Optional[str] = None,
                          entities: Optional[Dict] = None, sentiment: Optional[str] = None,
                          context: Optional[Dict] = None) -> Optional[int]:
        """
        Store a conversation entry.

        Args:
            role: "user" or "assistant"
            content: Message content
            intent: Detected intent (optional)
            entities: Extracted entities (optional)
            sentiment: Sentiment analysis result (optional)
            context: Additional context data (optional)

        Returns:
            int: Entry ID, or None if failed
        """
        if not self.available:
            return None

        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO conversation_history
                (timestamp, role, content, intent, entities, sentiment, context)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                time.time(),
                role,
                content,
                intent,
                json.dumps(entities) if entities else None,
                sentiment,
                json.dumps(context) if context else None,
            ))

            entry_id = cursor.fetchone()[0]
            conn.commit()

            self.stats['total_entries'] += 1
            logger.debug(f"Stored conversation entry {entry_id}")

            return entry_id

        except psycopg2.Error as e:
            logger.error(f"Failed to store conversation: {e}")
            if conn:
                conn.rollback()
            self.stats['failed_operations'] += 1
            return None

        finally:
            if conn:
                self.pool.putconn(conn)

    def get_recent_conversations(self, limit: int = 10, role: Optional[str] = None) -> List[ConversationEntry]:
        """
        Get recent conversation entries.

        Args:
            limit: Maximum number of entries to return
            role: Filter by role ("user" or "assistant"), or None for all

        Returns:
            List of ConversationEntry objects
        """
        if not self.available:
            return []

        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            self.stats['queries_executed'] += 1

            if role:
                cursor.execute("""
                    SELECT * FROM conversation_history
                    WHERE role = %s
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (role, limit))
            else:
                cursor.execute("""
                    SELECT * FROM conversation_history
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (limit,))

            rows = cursor.fetchall()

            entries = []
            for row in rows:
                entry = ConversationEntry(
                    id=row['id'],
                    timestamp=row['timestamp'],
                    role=row['role'],
                    content=row['content'],
                    intent=row['intent'],
                    entities=row['entities'],
                    sentiment=row['sentiment'],
                    context=row['context'],
                )
                entries.append(entry)

            return entries

        except psycopg2.Error as e:
            logger.error(f"Failed to get conversations: {e}")
            self.stats['failed_operations'] += 1
            return []

        finally:
            if conn:
                self.pool.putconn(conn)

    def search_conversations(self, query: str, limit: int = 10) -> List[ConversationEntry]:
        """
        Search conversations by keyword.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of ConversationEntry objects
        """
        if not self.available:
            return []

        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            self.stats['queries_executed'] += 1

            # Simple keyword search using ILIKE
            search_pattern = f"%{query}%"

            cursor.execute("""
                SELECT * FROM conversation_history
                WHERE content ILIKE %s OR intent ILIKE %s
                ORDER BY timestamp DESC
                LIMIT %s;
            """, (search_pattern, search_pattern, limit))

            rows = cursor.fetchall()

            entries = []
            for row in rows:
                entry = ConversationEntry(
                    id=row['id'],
                    timestamp=row['timestamp'],
                    role=row['role'],
                    content=row['content'],
                    intent=row['intent'],
                    entities=row['entities'],
                    sentiment=row['sentiment'],
                    context=row['context'],
                )
                entries.append(entry)

            logger.debug(f"Found {len(entries)} conversations matching '{query}'")

            return entries

        except psycopg2.Error as e:
            logger.error(f"Search failed: {e}")
            self.stats['failed_operations'] += 1
            return []

        finally:
            if conn:
                self.pool.putconn(conn)

    def get_conversation_context(self, window: int = 5) -> List[ConversationEntry]:
        """
        Get recent conversation context for LLM.

        Args:
            window: Number of recent exchanges to retrieve

        Returns:
            List of ConversationEntry objects
        """
        return self.get_recent_conversations(limit=window * 2)  # *2 for user+assistant pairs

    def store_command(self, command_id: str, intent: str, parameters: Optional[Dict] = None,
                     status: str = "initiated", result: Optional[Dict] = None,
                     execution_time: Optional[float] = None) -> Optional[int]:
        """
        Store a command execution record.

        Args:
            command_id: Unique command ID
            intent: Command intent
            parameters: Command parameters
            status: Execution status
            result: Execution result
            execution_time: Time taken to execute

        Returns:
            int: Record ID, or None if failed
        """
        if not self.available:
            return None

        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO command_history
                (timestamp, command_id, intent, parameters, status, result, execution_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                time.time(),
                command_id,
                intent,
                json.dumps(parameters) if parameters else None,
                status,
                json.dumps(result) if result else None,
                execution_time,
            ))

            record_id = cursor.fetchone()[0]
            conn.commit()

            logger.debug(f"Stored command record {record_id}")

            return record_id

        except psycopg2.Error as e:
            logger.error(f"Failed to store command: {e}")
            if conn:
                conn.rollback()
            self.stats['failed_operations'] += 1
            return None

        finally:
            if conn:
                self.pool.putconn(conn)

    def get_analytics(self) -> Dict[str, Any]:
        """
        Get conversation analytics.

        Returns:
            dict: Analytics data
        """
        if not self.available:
            return {}

        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            analytics = {}

            # Total conversations
            cursor.execute("SELECT COUNT(*) as total FROM conversation_history;")
            analytics['total_conversations'] = cursor.fetchone()['total']

            # Conversations by role
            cursor.execute("""
                SELECT role, COUNT(*) as count
                FROM conversation_history
                GROUP BY role;
            """)
            analytics['by_role'] = {row['role']: row['count'] for row in cursor.fetchall()}

            # Most common intents
            cursor.execute("""
                SELECT intent, COUNT(*) as count
                FROM conversation_history
                WHERE intent IS NOT NULL
                GROUP BY intent
                ORDER BY count DESC
                LIMIT 10;
            """)
            analytics['top_intents'] = [
                {'intent': row['intent'], 'count': row['count']}
                for row in cursor.fetchall()
            ]

            # Conversations per day (last 7 days)
            cursor.execute("""
                SELECT DATE(to_timestamp(timestamp)) as day, COUNT(*) as count
                FROM conversation_history
                WHERE timestamp > %s
                GROUP BY day
                ORDER BY day DESC;
            """, (time.time() - 7 * 24 * 3600,))

            analytics['daily_conversations'] = [
                {'day': str(row['day']), 'count': row['count']}
                for row in cursor.fetchall()
            ]

            return analytics

        except psycopg2.Error as e:
            logger.error(f"Analytics query failed: {e}")
            return {}

        finally:
            if conn:
                self.pool.putconn(conn)

    def cleanup_old_data(self, days: Optional[int] = None):
        """
        Remove old conversation data.

        Args:
            days: Remove data older than this many days (default: from config)
        """
        if not self.available:
            return

        days = days or self.retention_days
        cutoff_timestamp = time.time() - (days * 24 * 3600)

        conn = None
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM conversation_history
                WHERE timestamp < %s;
            """, (cutoff_timestamp,))

            deleted = cursor.rowcount
            conn.commit()

            logger.info(f"Cleaned up {deleted} old conversation entries (>{days} days)")

        except psycopg2.Error as e:
            logger.error(f"Cleanup failed: {e}")
            if conn:
                conn.rollback()

        finally:
            if conn:
                self.pool.putconn(conn)

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            **self.stats,
            'available': self.available,
            'pool_active': self.pool is not None,
        }

    def close(self):
        """Close database connections."""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connections closed")

    def __repr__(self) -> str:
        """String representation."""
        return f"MemoryManager(available={self.available}, entries={self.stats['total_entries']})"


# Test function
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from api_config import get_api_config

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Memory Manager Test")
    print("=" * 80)

    config = get_api_config()
    manager = MemoryManager(config)

    print(f"\nManager: {manager}")
    print(f"Available: {manager.available}")

    if manager.available:
        # Store test conversations
        print("\nStoring test conversations...")

        manager.store_conversation("user", "What's the weather like?", intent="weather")
        manager.store_conversation("assistant", "The current temperature is 22°C with partly cloudy skies.")

        manager.store_conversation("user", "Turn on the living room lights", intent="homeassistant")
        manager.store_conversation("assistant", "I've turned on the living room lights for you.")

        # Retrieve recent conversations
        print("\nRecent conversations:")
        recent = manager.get_recent_conversations(limit=5)
        for entry in recent:
            print(f"  [{entry.role}] {entry.content[:50]}...")

        # Search
        print("\nSearching for 'weather':")
        results = manager.search_conversations("weather", limit=3)
        for entry in results:
            print(f"  [{entry.role}] {entry.content}")

        # Analytics
        print("\nAnalytics:")
        analytics = manager.get_analytics()
        print(f"  Total conversations: {analytics.get('total_conversations', 0)}")
        print(f"  By role: {analytics.get('by_role', {})}")

        print(f"\nStats: {manager.get_stats()}")

        # Cleanup
        manager.close()

    else:
        print("\nMemory manager not available. Check PostgreSQL configuration.")
        print("Required: PostgreSQL running and credentials in .env")

    print("=" * 80)
