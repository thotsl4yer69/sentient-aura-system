#!/usr/bin/env python3
"""
Sentient Core v4 - Web Search Service
Real-time web search capabilities using Brave Search API.
"""

import logging
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger("search_service")


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    description: str
    published_date: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'published_date': self.published_date,
            'source': self.source,
        }


@dataclass
class SearchResponse:
    """Response from search service."""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    source: str
    error: Optional[str] = None

    def is_success(self) -> bool:
        """Check if search was successful."""
        return self.error is None and len(self.results) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'results': [r.to_dict() for r in self.results],
            'total_results': self.total_results,
            'search_time': self.search_time,
            'source': self.source,
            'error': self.error,
        }


class SearchService:
    """
    Web search service with caching and rate limiting.

    Features:
    - Brave Search API integration
    - Result caching to reduce API calls
    - Rate limiting
    - Query optimization
    """

    def __init__(self, api_config, world_state=None):
        """
        Initialize search service.

        Args:
            api_config: APIConfig instance
            world_state: Optional WorldState for context
        """
        self.config = api_config
        self.world_state = world_state

        # API configuration
        self.api_key = self.config.search['brave_api_key']
        self.endpoint = self.config.search['brave_endpoint']
        self.max_results = self.config.search['max_results']

        # Caching
        self.cache_enabled = self.config.cache['enabled']
        self.cache_ttl = self.config.cache['ttl']
        self.cache = {}  # query -> (timestamp, results)

        # Rate limiting
        self.rate_limit = self.config.rate_limits['search']
        self.request_timestamps = []

        # Statistics
        self.stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'failed_searches': 0,
        }

        # Check if service is available
        self.available = self.api_key is not None and self.api_key != ''

        if self.available:
            logger.info("✓ Search service initialized (Brave Search API)")
        else:
            logger.warning("Search service unavailable: No API key configured")

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            bool: True if request is allowed, False if rate limited
        """
        now = time.time()

        # Remove timestamps older than 1 minute
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]

        # Check if we're at the limit
        if len(self.request_timestamps) >= self.rate_limit:
            logger.warning(f"Rate limit reached ({self.rate_limit} requests/minute)")
            return False

        return True

    def _record_request(self):
        """Record a new API request for rate limiting."""
        self.request_timestamps.append(time.time())

    def _check_cache(self, query: str) -> Optional[SearchResponse]:
        """
        Check if query results are in cache.

        Args:
            query: Search query

        Returns:
            SearchResponse if cached and valid, None otherwise
        """
        if not self.cache_enabled:
            return None

        normalized_query = query.lower().strip()

        if normalized_query in self.cache:
            timestamp, results = self.cache[normalized_query]

            # Check if cache is still valid
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for query: {query}")
                self.stats['cache_hits'] += 1
                return results

            # Cache expired
            del self.cache[normalized_query]

        self.stats['cache_misses'] += 1
        return None

    def _update_cache(self, query: str, results: SearchResponse):
        """
        Update cache with new results.

        Args:
            query: Search query
            results: Search results
        """
        if not self.cache_enabled:
            return

        normalized_query = query.lower().strip()
        self.cache[normalized_query] = (time.time(), results)

        # Limit cache size to 100 entries
        if len(self.cache) > 100:
            # Remove oldest entry
            oldest_query = min(self.cache.keys(), key=lambda k: self.cache[k][0])
            del self.cache[oldest_query]

    def _optimize_query(self, query: str) -> str:
        """
        Optimize search query for better results.

        Args:
            query: Original query

        Returns:
            Optimized query
        """
        # Remove filler words
        filler_words = ['please', 'can you', 'could you', 'tell me', 'find', 'search for']

        optimized = query.lower()
        for filler in filler_words:
            optimized = optimized.replace(filler, '')

        optimized = optimized.strip()

        logger.debug(f"Query optimization: '{query}' -> '{optimized}'")
        return optimized if optimized else query

    def search(self, query: str, max_results: Optional[int] = None) -> SearchResponse:
        """
        Perform web search.

        Args:
            query: Search query
            max_results: Maximum number of results (default: from config)

        Returns:
            SearchResponse
        """
        self.stats['total_searches'] += 1

        # Check if service is available
        if not self.available:
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0,
                source='brave',
                error="Search service unavailable: No API key configured"
            )

        # Check cache
        cached = self._check_cache(query)
        if cached:
            return cached

        # Check rate limit
        if not self._check_rate_limit():
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0,
                source='brave',
                error="Rate limit exceeded. Please try again in a moment."
            )

        # Optimize query
        optimized_query = self._optimize_query(query)

        # Perform search
        start_time = time.time()

        try:
            # Record API call
            self._record_request()
            self.stats['api_calls'] += 1

            # Make API request
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.api_key,
            }

            params = {
                'q': optimized_query,
                'count': max_results or self.max_results,
            }

            logger.info(f"Searching: '{optimized_query}'")

            response = requests.get(
                self.endpoint,
                headers=headers,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # Parse results
            results = []
            web_results = data.get('web', {}).get('results', [])

            for item in web_results:
                result = SearchResult(
                    title=item.get('title', 'No title'),
                    url=item.get('url', ''),
                    description=item.get('description', 'No description'),
                    published_date=item.get('age'),
                    source=item.get('meta_url', {}).get('hostname'),
                )
                results.append(result)

            search_time = time.time() - start_time

            search_response = SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                source='brave'
            )

            # Update cache
            self._update_cache(query, search_response)

            logger.info(f"✓ Found {len(results)} results in {search_time:.2f}s")

            return search_response

        except requests.exceptions.RequestException as e:
            logger.error(f"Search API error: {e}")
            self.stats['failed_searches'] += 1

            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                source='brave',
                error=f"Search failed: {str(e)}"
            )

        except Exception as e:
            logger.error(f"Unexpected search error: {e}")
            self.stats['failed_searches'] += 1

            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                source='brave',
                error=f"Unexpected error: {str(e)}"
            )

    def summarize_results(self, search_response: SearchResponse, max_results: int = 3) -> str:
        """
        Create a natural language summary of search results.

        Args:
            search_response: SearchResponse object
            max_results: Maximum results to include in summary

        Returns:
            str: Natural language summary
        """
        if not search_response.is_success():
            return f"I couldn't find any information about '{search_response.query}'. {search_response.error or ''}"

        results = search_response.results[:max_results]

        summary_parts = [f"Here's what I found about '{search_response.query}':"]

        for i, result in enumerate(results, 1):
            summary_parts.append(f"\n{i}. {result.title}")
            summary_parts.append(f"   {result.description}")
            if result.source:
                summary_parts.append(f"   Source: {result.source}")

        if search_response.total_results > max_results:
            remaining = search_response.total_results - max_results
            summary_parts.append(f"\n...and {remaining} more results.")

        return "\n".join(summary_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'cache_hit_rate': (
                self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses'])
                if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0
            ),
            'available': self.available,
        }

    def clear_cache(self):
        """Clear the search cache."""
        self.cache = {}
        logger.info("Search cache cleared")

    def __repr__(self) -> str:
        """String representation."""
        return f"SearchService(available={self.available}, searches={self.stats['total_searches']})"


# Test function
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from api_config import get_api_config

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Search Service Test")
    print("=" * 80)

    config = get_api_config()
    service = SearchService(config)

    print(f"\nService: {service}")
    print(f"Available: {service.available}")

    if service.available:
        # Test query
        test_query = "latest news artificial intelligence"

        print(f"\nSearching: '{test_query}'")

        response = service.search(test_query, max_results=3)

        if response.is_success():
            print(f"\nFound {response.total_results} results in {response.search_time:.2f}s")
            print("\nResults:")
            for i, result in enumerate(response.results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   {result.url}")
                print(f"   {result.description[:100]}...")

            print("\n" + "-" * 80)
            print("\nSummary:")
            print(service.summarize_results(response))

        else:
            print(f"\nSearch failed: {response.error}")

        print(f"\nStats: {service.get_stats()}")

    else:
        print("\nSearch service not available. Set BRAVE_API_KEY in .env file.")

    print("=" * 80)
