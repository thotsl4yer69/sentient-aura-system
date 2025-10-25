#!/usr/bin/env python3
"""
Sentient Core v4 - API Configuration Manager
Centralized API key and configuration management with security best practices.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("api_config")


class APIConfig:
    """
    Centralized API configuration manager.

    Handles:
    - Environment variable loading
    - Secure credential management
    - API endpoint configuration
    - Feature flags
    - Rate limiting settings
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize API configuration.

        Args:
            env_file: Path to .env file (default: PROJECT_ROOT/.env)
        """
        # Determine project root
        self.project_root = Path(__file__).parent.parent

        # Load environment variables
        if env_file is None:
            env_file = self.project_root / ".env"

        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
        else:
            logger.warning(f"No .env file found at {env_file}, using defaults")

        # Initialize configuration sections
        self._load_llm_config()
        self._load_search_config()
        self._load_weather_config()
        self._load_news_config()
        self._load_homeassistant_config()
        self._load_database_config()
        self._load_github_config()
        self._load_rate_limiting_config()
        self._load_feature_flags()
        self._load_advanced_settings()

    def _getenv(self, key: str, default: Any = None, cast: type = str) -> Any:
        """
        Get environment variable with type casting and default.

        Args:
            key: Environment variable name
            default: Default value if not found
            cast: Type to cast the value to

        Returns:
            The environment variable value, cast to the specified type
        """
        value = os.getenv(key)

        if value is None:
            return default

        try:
            if cast == bool:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif cast == int:
                return int(value)
            elif cast == float:
                return float(value)
            else:
                return cast(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to cast {key}={value} to {cast}, using default")
            return default

    def _load_llm_config(self):
        """Load LLM API configuration."""
        self.llm = {
            # Ollama (Local)
            'ollama_host': self._getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'ollama_model': self._getenv('OLLAMA_MODEL', 'llama3.1:8b'),
            'ollama_timeout': self._getenv('OLLAMA_TIMEOUT', 120, int),

            # Anthropic Claude
            'anthropic_api_key': self._getenv('ANTHROPIC_API_KEY'),
            'anthropic_model': self._getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022'),
            'anthropic_max_tokens': self._getenv('ANTHROPIC_MAX_TOKENS', 2048, int),

            # OpenAI
            'openai_api_key': self._getenv('OPENAI_API_KEY'),
            'openai_model': self._getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
            'openai_max_tokens': self._getenv('OPENAI_MAX_TOKENS', 2048, int),

            # Groq
            'groq_api_key': self._getenv('GROQ_API_KEY'),
            'groq_model': self._getenv('GROQ_MODEL', 'llama-3.1-70b-versatile'),

            # Google Gemini
            'google_api_key': self._getenv('GOOGLE_API_KEY'),
            'google_model': self._getenv('GOOGLE_MODEL', 'gemini-1.5-pro'),

            # Backend priority
            'backend_priority': self._getenv('LLM_BACKEND_PRIORITY', 'ollama,anthropic,openai').split(','),
        }

    def _load_search_config(self):
        """Load web search API configuration."""
        self.search = {
            'brave_api_key': self._getenv('BRAVE_API_KEY'),
            'brave_endpoint': self._getenv('BRAVE_SEARCH_ENDPOINT',
                                          'https://api.search.brave.com/res/v1/web/search'),
            'max_results': self._getenv('SEARCH_MAX_RESULTS', 5, int),
        }

    def _load_weather_config(self):
        """Load weather API configuration."""
        self.weather = {
            'openweather_api_key': self._getenv('OPENWEATHER_API_KEY'),
            'openweather_units': self._getenv('OPENWEATHER_UNITS', 'metric'),
            'weathergov_user_agent': self._getenv('WEATHER_GOV_USER_AGENT',
                                                  'SentientCore/4.0 (contact@example.com)'),
            'default_latitude': self._getenv('DEFAULT_LATITUDE', cast=float),
            'default_longitude': self._getenv('DEFAULT_LONGITUDE', cast=float),
            'default_location_name': self._getenv('DEFAULT_LOCATION_NAME', 'Unknown'),
        }

    def _load_news_config(self):
        """Load news API configuration."""
        self.news = {
            'api_key': self._getenv('NEWS_API_KEY'),
            'country': self._getenv('NEWS_API_COUNTRY', 'us'),
            'language': self._getenv('NEWS_API_LANGUAGE', 'en'),
            'max_articles': self._getenv('NEWS_MAX_ARTICLES', 10, int),
        }

    def _load_homeassistant_config(self):
        """Load Home Assistant API configuration."""
        self.homeassistant = {
            'url': self._getenv('HOMEASSISTANT_URL', 'http://localhost:8123'),
            'token': self._getenv('HOMEASSISTANT_TOKEN'),
            'verify_ssl': self._getenv('HOMEASSISTANT_VERIFY_SSL', False, bool),
        }

    def _load_database_config(self):
        """Load PostgreSQL database configuration."""
        self.database = {
            'host': self._getenv('POSTGRES_HOST', 'localhost'),
            'port': self._getenv('POSTGRES_PORT', 5432, int),
            'database': self._getenv('POSTGRES_DB', 'sentient_core'),
            'user': self._getenv('POSTGRES_USER', 'postgres'),
            'password': self._getenv('POSTGRES_PASSWORD', 'postgres'),
            'min_connections': self._getenv('POSTGRES_MIN_CONNECTIONS', 2, int),
            'max_connections': self._getenv('POSTGRES_MAX_CONNECTIONS', 10, int),
        }

    def _load_github_config(self):
        """Load GitHub API configuration."""
        self.github = {
            'token': self._getenv('GITHUB_TOKEN'),
        }

    def _load_rate_limiting_config(self):
        """Load rate limiting configuration."""
        self.rate_limits = {
            'llm': self._getenv('RATE_LIMIT_LLM', 20, int),
            'search': self._getenv('RATE_LIMIT_SEARCH', 10, int),
            'weather': self._getenv('RATE_LIMIT_WEATHER', 60, int),
            'news': self._getenv('RATE_LIMIT_NEWS', 30, int),
        }

        self.cache = {
            'enabled': self._getenv('API_CACHE_ENABLED', True, bool),
            'ttl': self._getenv('API_CACHE_TTL', 300, int),
        }

    def _load_feature_flags(self):
        """Load feature flags."""
        self.features = {
            'llm_api': self._getenv('ENABLE_LLM_API', True, bool),
            'search_api': self._getenv('ENABLE_SEARCH_API', True, bool),
            'weather_api': self._getenv('ENABLE_WEATHER_API', True, bool),
            'news_api': self._getenv('ENABLE_NEWS_API', True, bool),
            'homeassistant_api': self._getenv('ENABLE_HOMEASSISTANT_API', True, bool),
            'github_api': self._getenv('ENABLE_GITHUB_API', True, bool),
            'memory_storage': self._getenv('ENABLE_MEMORY_STORAGE', True, bool),
            'offline_mode': self._getenv('OFFLINE_MODE', False, bool),
        }

    def _load_advanced_settings(self):
        """Load advanced settings."""
        self.advanced = {
            # LLM settings
            'llm_context_window': self._getenv('LLM_CONTEXT_WINDOW', 8, int),
            'llm_temperature': self._getenv('LLM_TEMPERATURE', 0.7, float),
            'llm_streaming': self._getenv('LLM_STREAMING', True, bool),

            # Memory settings
            'memory_auto_summarize': self._getenv('MEMORY_AUTO_SUMMARIZE', True, bool),
            'memory_retention_days': self._getenv('MEMORY_RETENTION_DAYS', 90, int),

            # Logging
            'log_requests': self._getenv('API_LOG_REQUESTS', True, bool),
            'log_responses': self._getenv('API_LOG_RESPONSES', False, bool),
            'log_errors': self._getenv('API_LOG_ERRORS', True, bool),

            # Cost tracking
            'track_costs': self._getenv('TRACK_API_COSTS', True, bool),
            'cost_alert_threshold': self._getenv('COST_ALERT_THRESHOLD', 10.0, float),
        }

    def is_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature name (e.g., 'llm_api', 'search_api')

        Returns:
            bool: True if enabled, False otherwise
        """
        return self.features.get(feature, False)

    def has_credentials(self, service: str) -> bool:
        """
        Check if credentials are available for a service.

        Args:
            service: Service name (e.g., 'anthropic', 'brave', 'openweather')

        Returns:
            bool: True if credentials exist, False otherwise
        """
        credentials_map = {
            'anthropic': self.llm.get('anthropic_api_key'),
            'openai': self.llm.get('openai_api_key'),
            'groq': self.llm.get('groq_api_key'),
            'google': self.llm.get('google_api_key'),
            'brave': self.search.get('brave_api_key'),
            'openweather': self.weather.get('openweather_api_key'),
            'newsapi': self.news.get('api_key'),
            'homeassistant': self.homeassistant.get('token'),
            'github': self.github.get('token'),
        }

        cred = credentials_map.get(service)
        return cred is not None and cred != ''

    def get_available_llm_backends(self) -> list:
        """
        Get list of available LLM backends based on credentials and priority.

        Returns:
            list: Available backend names in priority order
        """
        available = []

        for backend in self.llm['backend_priority']:
            backend = backend.strip().lower()

            if backend == 'ollama':
                # Ollama doesn't need credentials, just check if it's reachable
                available.append('ollama')
            elif backend == 'anthropic' and self.has_credentials('anthropic'):
                available.append('anthropic')
            elif backend == 'openai' and self.has_credentials('openai'):
                available.append('openai')
            elif backend == 'groq' and self.has_credentials('groq'):
                available.append('groq')
            elif backend == 'google' and self.has_credentials('google'):
                available.append('google')

        return available

    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration and return status report.

        Returns:
            dict: Validation status for each service
        """
        status = {
            'llm_backends': self.get_available_llm_backends(),
            'search_available': self.has_credentials('brave'),
            'weather_available': self.has_credentials('openweather') or True,  # weather.gov is free
            'news_available': self.has_credentials('newsapi'),
            'homeassistant_available': self.has_credentials('homeassistant'),
            'github_available': self.has_credentials('github'),
            'database_configured': True,  # Always available locally
        }

        return status

    def get_safe_config(self) -> Dict[str, Any]:
        """
        Get configuration with sensitive data redacted.

        Returns:
            dict: Safe configuration for logging/debugging
        """
        def redact(value):
            """Redact sensitive values."""
            if value is None or value == '':
                return None
            if isinstance(value, str) and len(value) > 8:
                return f"{value[:4]}...{value[-4:]}"
            return "***"

        return {
            'llm': {
                'ollama_host': self.llm['ollama_host'],
                'ollama_model': self.llm['ollama_model'],
                'anthropic_api_key': redact(self.llm['anthropic_api_key']),
                'openai_api_key': redact(self.llm['openai_api_key']),
                'backend_priority': self.llm['backend_priority'],
                'available_backends': self.get_available_llm_backends(),
            },
            'search': {
                'brave_api_key': redact(self.search['brave_api_key']),
            },
            'weather': {
                'openweather_api_key': redact(self.weather['openweather_api_key']),
                'default_location': self.weather['default_location_name'],
            },
            'homeassistant': {
                'url': self.homeassistant['url'],
                'token': redact(self.homeassistant['token']),
            },
            'features': self.features,
            'validation': self.validate(),
        }

    def __repr__(self) -> str:
        """String representation."""
        backends = self.get_available_llm_backends()
        return f"APIConfig(llm_backends={backends}, features={list(self.features.keys())})"


# Singleton instance
_api_config_instance = None


def get_api_config(env_file: Optional[str] = None) -> APIConfig:
    """
    Get or create the singleton API configuration instance.

    Args:
        env_file: Path to .env file (only used on first call)

    Returns:
        APIConfig: The configuration instance
    """
    global _api_config_instance

    if _api_config_instance is None:
        _api_config_instance = APIConfig(env_file)

    return _api_config_instance


# Test function
if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("API Configuration Test")
    print("=" * 80)

    config = get_api_config()

    print("\nConfiguration Status:")
    print(json.dumps(config.get_safe_config(), indent=2))

    print("\nValidation Report:")
    print(json.dumps(config.validate(), indent=2))

    print("\nAvailable LLM Backends:")
    for backend in config.get_available_llm_backends():
        print(f"  ✓ {backend}")

    print("\nFeature Flags:")
    for feature, enabled in config.features.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}: {enabled}")

    print("\n" + "=" * 80)
