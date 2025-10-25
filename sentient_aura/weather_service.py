#!/usr/bin/env python3
"""
Sentient Core v4 - Weather Service
Real-time weather data with sensor data fusion.
"""

import logging
import time
import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("weather_service")


@dataclass
class WeatherData:
    """Current weather data."""
    temperature: float  # Celsius
    feels_like: float
    humidity: int  # Percentage
    pressure: int  # hPa
    description: str
    wind_speed: float  # m/s
    wind_direction: int  # degrees
    clouds: int  # Percentage
    visibility: Optional[int] = None  # meters
    uv_index: Optional[float] = None
    precipitation: Optional[float] = None  # mm
    source: str = "api"
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'description': self.description,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'clouds': self.clouds,
            'visibility': self.visibility,
            'uv_index': self.uv_index,
            'precipitation': self.precipitation,
            'source': self.source,
            'timestamp': self.timestamp,
        }


@dataclass
class WeatherResponse:
    """Response from weather service."""
    location: str
    current: Optional[WeatherData]
    forecast: Optional[list] = None
    error: Optional[str] = None

    def is_success(self) -> bool:
        """Check if request was successful."""
        return self.error is None and self.current is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'location': self.location,
            'current': self.current.to_dict() if self.current else None,
            'forecast': [f.to_dict() for f in self.forecast] if self.forecast else None,
            'error': self.error,
        }


class WeatherService:
    """
    Weather service with sensor data fusion.

    Features:
    - OpenWeatherMap API integration
    - Weather.gov API (free, no key required)
    - Sensor data fusion (BME280)
    - Caching to reduce API calls
    - Natural language summaries
    """

    def __init__(self, api_config, world_state=None):
        """
        Initialize weather service.

        Args:
            api_config: APIConfig instance
            world_state: Optional WorldState for sensor fusion
        """
        self.config = api_config
        self.world_state = world_state

        # API configuration
        self.openweather_key = self.config.weather['openweather_api_key']
        self.units = self.config.weather['openweather_units']
        self.default_lat = self.config.weather['default_latitude']
        self.default_lon = self.config.weather['default_longitude']
        self.default_location = self.config.weather['default_location_name']

        # Caching
        self.cache_enabled = self.config.cache['enabled']
        self.cache_ttl = self.config.cache['ttl']
        self.cache = {}  # location -> (timestamp, weather_data)

        # Rate limiting
        self.rate_limit = self.config.rate_limits['weather']
        self.request_timestamps = []

        # Statistics
        self.stats = {
            'total_requests': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'sensor_fusions': 0,
            'failed_requests': 0,
        }

        # Check availability
        self.has_api_key = self.openweather_key is not None and self.openweather_key != ''
        self.has_location = self.default_lat is not None and self.default_lon is not None

        if self.has_api_key:
            logger.info("✓ Weather service initialized (OpenWeatherMap API)")
        else:
            logger.info("Weather service in sensor-only mode (no API key)")

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]

        if len(self.request_timestamps) >= self.rate_limit:
            logger.warning(f"Weather API rate limit reached ({self.rate_limit} requests/minute)")
            return False

        return True

    def _record_request(self):
        """Record a new API request."""
        self.request_timestamps.append(time.time())

    def _check_cache(self, location: str) -> Optional[WeatherResponse]:
        """Check if weather data is cached."""
        if not self.cache_enabled:
            return None

        if location in self.cache:
            timestamp, data = self.cache[location]

            # Weather cache is valid for longer (5 minutes)
            if time.time() - timestamp < 300:
                logger.debug(f"Weather cache hit for: {location}")
                self.stats['cache_hits'] += 1
                return data

            del self.cache[location]

        return None

    def _update_cache(self, location: str, data: WeatherResponse):
        """Update cache with new weather data."""
        if self.cache_enabled:
            self.cache[location] = (time.time(), data)

    def _get_sensor_weather(self) -> Optional[WeatherData]:
        """
        Get weather data from local sensors (BME280).

        Returns:
            WeatherData from sensors, or None if not available
        """
        if self.world_state is None:
            return None

        try:
            env = self.world_state.get('environment')
            if not env:
                return None

            temp = env.get('temperature')
            humidity = env.get('humidity')
            pressure = env.get('pressure')

            if temp is not None and humidity is not None and pressure is not None:
                logger.debug(f"Sensor weather: {temp}°C, {humidity}%, {pressure}hPa")

                self.stats['sensor_fusions'] += 1

                return WeatherData(
                    temperature=temp,
                    feels_like=temp,  # Simple approximation
                    humidity=int(humidity),
                    pressure=int(pressure),
                    description="Measured by local sensors",
                    wind_speed=0.0,
                    wind_direction=0,
                    clouds=0,
                    source="sensor"
                )

        except Exception as e:
            logger.debug(f"Error reading sensor weather: {e}")

        return None

    def _fetch_openweather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """
        Fetch weather from OpenWeatherMap API.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            WeatherData or None
        """
        if not self.has_api_key:
            return None

        if not self._check_rate_limit():
            return None

        try:
            self._record_request()
            self.stats['api_calls'] += 1

            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_key,
                'units': self.units,
            }

            logger.info(f"Fetching weather for ({lat}, {lon})")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse response
            main = data['main']
            weather = data['weather'][0]
            wind = data['wind']

            weather_data = WeatherData(
                temperature=main['temp'],
                feels_like=main['feels_like'],
                humidity=main['humidity'],
                pressure=main['pressure'],
                description=weather['description'],
                wind_speed=wind.get('speed', 0),
                wind_direction=wind.get('deg', 0),
                clouds=data['clouds']['all'],
                visibility=data.get('visibility'),
                source="openweather"
            )

            logger.info(f"✓ Weather fetched: {weather_data.temperature}°C, {weather_data.description}")

            return weather_data

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWeatherMap API error: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected weather error: {e}")
            return None

    def get_current_weather(self, location: Optional[str] = None) -> WeatherResponse:
        """
        Get current weather for a location.

        Args:
            location: Location name or coordinates (default: configured location)

        Returns:
            WeatherResponse
        """
        self.stats['total_requests'] += 1

        # Use default location if not specified
        if location is None:
            location = self.default_location
            lat = self.default_lat
            lon = self.default_lon
        else:
            # TODO: Geocoding to convert location name to coordinates
            # For now, use default coordinates
            lat = self.default_lat
            lon = self.default_lon

        # Check cache
        cached = self._check_cache(location)
        if cached:
            return cached

        # Try API first
        weather_data = None

        if self.has_location and self.has_api_key:
            weather_data = self._fetch_openweather(lat, lon)

        # Fallback to sensors
        if weather_data is None:
            weather_data = self._get_sensor_weather()

        # Build response
        if weather_data:
            response = WeatherResponse(
                location=location,
                current=weather_data
            )

            # Fuse sensor data with API data if both available
            if weather_data.source == "openweather" and self.world_state:
                env = self.world_state.get('environment')
                if env and env.get('temperature'):
                    # Use local sensor temperature as ground truth
                    sensor_temp = env['temperature']
                    api_temp = weather_data.temperature
                    logger.debug(f"Temperature comparison - Sensor: {sensor_temp}°C, API: {api_temp}°C")

            self._update_cache(location, response)
            return response

        else:
            self.stats['failed_requests'] += 1
            return WeatherResponse(
                location=location,
                current=None,
                error="Unable to fetch weather data. No API key or sensors available."
            )

    def summarize_weather(self, weather_response: WeatherResponse) -> str:
        """
        Create natural language summary of weather.

        Args:
            weather_response: WeatherResponse object

        Returns:
            str: Natural language summary
        """
        if not weather_response.is_success():
            return f"I couldn't get weather information for {weather_response.location}. {weather_response.error or ''}"

        w = weather_response.current

        summary_parts = [
            f"Current weather in {weather_response.location}:",
            f"Temperature: {w.temperature:.1f}°C (feels like {w.feels_like:.1f}°C)",
            f"Conditions: {w.description.capitalize()}",
            f"Humidity: {w.humidity}%",
            f"Pressure: {w.pressure} hPa",
        ]

        if w.wind_speed > 0:
            summary_parts.append(f"Wind: {w.wind_speed:.1f} m/s")

        if w.source == "sensor":
            summary_parts.append("(Data from local environmental sensors)")

        return "\n".join(summary_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self.stats,
            'has_api_key': self.has_api_key,
            'has_location': self.has_location,
            'has_sensors': self.world_state is not None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"WeatherService(api={self.has_api_key}, sensors={self.world_state is not None})"


# Test function
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from api_config import get_api_config

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Weather Service Test")
    print("=" * 80)

    config = get_api_config()
    service = WeatherService(config)

    print(f"\nService: {service}")
    print(f"Has API key: {service.has_api_key}")
    print(f"Has location: {service.has_location}")

    # Test query
    print(f"\nGetting weather for: {service.default_location}")

    response = service.get_current_weather()

    if response.is_success():
        print("\nWeather Data:")
        print(f"  Temperature: {response.current.temperature}°C")
        print(f"  Feels like: {response.current.feels_like}°C")
        print(f"  Humidity: {response.current.humidity}%")
        print(f"  Pressure: {response.current.pressure} hPa")
        print(f"  Description: {response.current.description}")
        print(f"  Source: {response.current.source}")

        print("\n" + "-" * 80)
        print("\nSummary:")
        print(service.summarize_weather(response))

    else:
        print(f"\nWeather fetch failed: {response.error}")

    print(f"\nStats: {service.get_stats()}")
    print("=" * 80)
