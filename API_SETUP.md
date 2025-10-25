# Sentient Core v4 - API Integration Setup Guide

Complete guide to unlocking the full potential of the Sentient Core with internet connectivity and API integration.

## Overview

The Sentient Core v4 API integration system provides:

- **LLM Integration**: Intelligent conversation using Ollama (local) or cloud LLMs (Claude, GPT-4, etc.)
- **Web Search**: Real-time information retrieval via Brave Search API
- **Weather Integration**: OpenWeatherMap API + local sensor fusion (BME280)
- **Smart Home Control**: Home Assistant REST API integration
- **Conversation Memory**: PostgreSQL-backed long-term memory and analytics
- **Graceful Degradation**: System works offline with reduced capabilities

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Sentient Core v4                            │
│                  (sentient_core_enhanced.py)                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │    API Manager      │
           │  (api_manager.py)   │
           └─────────┬───────────┘
                     │
      ┌──────────────┼──────────────┬──────────────┬──────────────┐
      │              │              │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐  ┌───▼────┐  ┌──────▼──────┐
│LLM Service│  │ Search  │  │   Weather   │  │ Home   │  │   Memory    │
│           │  │ Service │  │   Service   │  │Assistant│ │   Manager   │
│  Ollama   │  │         │  │             │  │ Bridge  │  │             │
│  Claude   │  │  Brave  │  │OpenWeather  │  │         │  │ PostgreSQL  │
│  OpenAI   │  │   API   │  │   + BME280  │  │ REST API│  │   Storage   │
│  Groq     │  │         │  │             │  │         │  │             │
│  Gemini   │  │         │  │             │  │         │  │             │
└───────────┘  └─────────┘  └─────────────┘  └─────────┘  └─────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd ~/Sentient-Core-v4

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

New dependencies include:
- `python-dotenv` - Environment variable management
- `ollama` - Local LLM client
- `anthropic` - Claude API client
- `openai` - GPT API client
- `groq` - Fast inference API client
- `google-generativeai` - Gemini API client
- `requests` - HTTP client for APIs
- `psycopg2-binary` - PostgreSQL database driver

### 2. Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit configuration
nano .env
```

**Minimum Configuration (Local-Only):**

```bash
# Ollama (no API key needed - runs locally)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# PostgreSQL (local database)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sentient_core
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Feature flags
ENABLE_LLM_API=true
ENABLE_MEMORY_STORAGE=true
```

**Full Configuration (with API keys):**

See `.env.template` for all available options. Add API keys for:
- **Brave Search** - Get free key at https://brave.com/search/api/
- **OpenWeatherMap** - Get free key at https://openweathermap.org/api
- **Anthropic Claude** - Get key at https://console.anthropic.com/
- **Home Assistant** - Generate long-lived token in HA settings

### 3. Set Up Services

#### A. Ollama (Local LLM - Recommended)

Ollama is already installed at `/usr/local/bin/ollama`.

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve &

# Pull a model (if not already downloaded)
ollama pull llama3.1:8b

# List available models
ollama list
```

**Recommended models for Raspberry Pi:**
- `llama3.1:8b` - Good balance (4-5GB RAM)
- `llama3.2:3b` - Faster, lower quality (2-3GB RAM)
- `phi3:mini` - Very fast, decent quality (2GB RAM)

#### B. PostgreSQL (Memory Storage)

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE sentient_core;"

# Test connection
PGPASSWORD=postgres psql -U postgres -d sentient_core -c "SELECT 1"

# Enable PostgreSQL to start on boot
sudo systemctl enable postgresql
```

The Memory Manager will automatically create the required tables on first run.

#### C. Home Assistant (Optional)

If Home Assistant is not running:

```bash
# Start Docker (if not running)
sudo systemctl start docker

# Start Home Assistant container
docker start homeassistant

# Get long-lived access token:
# 1. Open http://localhost:8123
# 2. Click on your profile (bottom left)
# 3. Scroll down to "Long-Lived Access Tokens"
# 4. Click "Create Token"
# 5. Copy token to .env file as HOMEASSISTANT_TOKEN
```

### 4. Test API Services

Test each service individually:

```bash
cd ~/Sentient-Core-v4/sentient_aura

# Test API Configuration
python api_config.py

# Test LLM Service
python llm_service.py

# Test Search Service (requires BRAVE_API_KEY)
python search_service.py

# Test Weather Service (requires OPENWEATHER_API_KEY or sensors)
python weather_service.py

# Test Home Assistant Bridge (requires HA running + token)
python homeassistant_bridge.py

# Test Memory Manager (requires PostgreSQL)
python memory_manager.py

# Test complete API Manager
python api_manager.py
```

### 5. Run Enhanced Sentient Core

The enhanced core is backward compatible with the original.

**Option 1: Replace original core**

```bash
cd ~/Sentient-Core-v4/sentient_aura

# Backup original
cp sentient_core.py sentient_core_original.py

# Replace with enhanced version
cp sentient_core_enhanced.py sentient_core.py
```

**Option 2: Use enhanced version directly**

Edit `sentient_aura_main.py` and import `SentientCoreEnhanced` instead of `SentientCore`.

**Run the system:**

```bash
cd ~/Sentient-Core-v4
python sentient_aura_main.py
```

## Configuration Options

### Feature Flags (config.py)

```python
# API Integration
ENABLE_API_INTEGRATION = True  # Master switch

# LLM
USE_LLM_FOR_RESPONSES = True  # Use LLM for responses
LLM_FALLBACK_TO_TEMPLATES = True  # Fall back on error

# Web Search
ENABLE_WEB_SEARCH = True

# Weather
ENABLE_WEATHER_API = True
FUSE_WEATHER_WITH_SENSORS = True  # Combine API + BME280

# Smart Home
ENABLE_SMART_HOME_CONTROL = True
SMART_HOME_VOICE_COMMANDS = True

# Memory
ENABLE_CONVERSATION_MEMORY = True
ENABLE_CONTEXT_RETRIEVAL = True
CONVERSATION_CONTEXT_WINDOW = 10
```

### LLM Backend Priority (.env)

```bash
# Try backends in this order (first available is used)
LLM_BACKEND_PRIORITY=ollama,anthropic,openai,groq,google
```

The system will automatically fall back to the next backend if one fails.

### Rate Limiting (.env)

```bash
# Requests per minute
RATE_LIMIT_LLM=20
RATE_LIMIT_SEARCH=10
RATE_LIMIT_WEATHER=60
RATE_LIMIT_NEWS=30
```

### Caching (.env)

```bash
# Enable caching to reduce API calls
API_CACHE_ENABLED=true
API_CACHE_TTL=300  # 5 minutes
```

## Usage Examples

### Voice Commands

**Basic Conversation:**
```
User: "Hello, how are you?"
Core: [Uses LLM] "I'm doing great! All my sensors are online and I'm ready to help..."
```

**Weather Query:**
```
User: "What's the weather like?"
Core: [Fetches OpenWeatherMap + BME280] "Current weather: 22°C, partly cloudy. Humidity 65%, pressure 1013 hPa..."
```

**Web Search:**
```
User: "Search for latest AI news"
Core: [Uses Brave Search] "Here's what I found about 'latest AI news':
      1. OpenAI announces GPT-5...
      2. Google releases Gemini 2.0...
      3. ..."
```

**Smart Home Control:**
```
User: "Turn on the living room lights"
Core: [Calls Home Assistant API] "I've turned on the living room lights for you."
```

**Sensor Status:**
```
User: "Show me your sensors"
Core: [Displays sensor GUI] "I have 5 sensors online: camera, Flipper Zero, environment sensors..."
```

### Programmatic API

```python
from sentient_aura.api_manager import APIManager

# Initialize
api = APIManager(world_state=world_state)

# Chat with LLM
response = api.chat("What is the meaning of life?")
print(response.content)

# Search the web
results = api.search("quantum computing", max_results=5)
for result in results.results:
    print(f"- {result.title}: {result.url}")

# Get weather
weather = api.get_weather()
print(f"Temperature: {weather.current.temperature}°C")

# Control smart home
success = api.smart_home_control("light.bedroom", "turn_on", brightness=128)

# Store conversation
api.remember_conversation("user", "Hello!")
api.remember_conversation("assistant", "Hi there!")

# Get conversation context
context = api.get_conversation_context(window=5)
for entry in context:
    print(f"[{entry.role}] {entry.content}")
```

## API Service Details

### LLM Service

**Backends Supported:**
1. **Ollama** (Local - Recommended)
   - No API key needed
   - Runs on device
   - Privacy-preserving
   - Models: llama3.1, llama3.2, phi3, mistral, etc.

2. **Anthropic Claude**
   - Excellent reasoning
   - Good for complex tasks
   - Requires API key + credits

3. **OpenAI GPT**
   - Industry standard
   - Requires API key + credits

4. **Groq**
   - Extremely fast inference
   - Free tier available
   - Requires API key

5. **Google Gemini**
   - Multimodal capabilities
   - Free tier available
   - Requires API key

**Automatic Fallback:**
If Ollama fails, the system automatically tries cloud backends in priority order.

### Search Service

**Features:**
- Real-time web search via Brave Search API
- Query optimization (removes filler words)
- Result ranking and summarization
- Built-in caching (5 min TTL)
- Rate limiting (10 requests/min default)

**API Key:**
Get free Brave Search API key: https://brave.com/search/api/
- Free tier: 2,000 queries/month
- Perfect for personal use

### Weather Service

**Features:**
- OpenWeatherMap API for global weather
- Local BME280 sensor fusion
- Temperature, humidity, pressure, wind, clouds
- Caching to reduce API calls
- Falls back to sensors if API unavailable

**API Key:**
OpenWeatherMap free tier: https://openweathermap.org/api
- 1,000 calls/day
- 60 calls/minute

**Sensor Fusion:**
If both API and sensors are available, the system cross-references data for accuracy.

### Home Assistant Bridge

**Features:**
- REST API integration
- Entity state queries
- Service calls (turn_on, turn_off, toggle)
- Scene activation
- Automation triggers
- Real-time state monitoring

**Setup:**
1. Home Assistant must be running
2. Generate long-lived access token
3. Add to `.env` as `HOMEASSISTANT_TOKEN`

**Supported Entities:**
- Lights
- Switches
- Climate controls
- Covers (blinds, garage doors)
- Locks
- Media players
- Sensors
- Binary sensors

### Memory Manager

**Features:**
- PostgreSQL-backed conversation storage
- Semantic search (keyword-based)
- Context retrieval for LLM
- Analytics and insights
- Automatic data cleanup (90-day retention)
- Command history tracking
- Sensor data archival

**Database Schema:**
- `conversation_history` - All conversations
- `command_history` - Executed commands
- `sensor_analytics` - Sensor data (optional)

**Queries:**
```python
# Recent conversations
recent = memory.get_recent_conversations(limit=10)

# Search conversations
results = memory.search_conversations("weather", limit=5)

# Get context for LLM
context = memory.get_conversation_context(window=5)

# Analytics
analytics = memory.get_analytics()
print(f"Total conversations: {analytics['total_conversations']}")
print(f"Top intents: {analytics['top_intents']}")
```

## Monitoring & Debugging

### Health Check

```python
from sentient_aura.api_manager import APIManager

api = APIManager()
health = api.health_check()

print(f"LLM Available: {health.llm_available}")
print(f"Search Available: {health.search_available}")
print(f"Weather Available: {health.weather_available}")
print(f"Home Assistant Available: {health.homeassistant_available}")
print(f"Memory Available: {health.memory_available}")
print(f"Total Requests: {health.total_requests}")
print(f"Failed Requests: {health.failed_requests}")
```

### Detailed Statistics

```python
stats = api.get_detailed_stats()

# LLM stats
print(f"LLM Backend Usage: {stats['llm']['backend_usage']}")
print(f"Total Tokens: {stats['llm']['total_tokens']}")

# Search stats
print(f"Search Cache Hit Rate: {stats['search']['cache_hit_rate']:.1%}")

# Memory stats
print(f"Conversations Stored: {stats['memory']['total_entries']}")
```

### Logs

All API operations are logged:

```bash
# View API logs
tail -f ~/Sentient-Core-v4/logs/sentient_aura.log | grep -E "api_|llm_|search_"
```

## Troubleshooting

### Ollama Connection Failed

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve &

# Check logs
journalctl -u ollama -f
```

### PostgreSQL Connection Failed

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Test connection
PGPASSWORD=postgres psql -U postgres -d sentient_core -c "SELECT 1"

# Check logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Home Assistant Not Connecting

```bash
# Check if HA container is running
docker ps | grep homeassistant

# Check HA logs
docker logs -f homeassistant

# Test REST API
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8123/api/
```

### API Key Not Working

1. Check `.env` file exists and is in project root
2. Verify API key is correct (no extra spaces)
3. Check API key permissions/quotas
4. Test API key directly with curl:

```bash
# Test Brave Search
curl -H "X-Subscription-Token: YOUR_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"

# Test OpenWeather
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
```

### LLM Response Slow

**For Ollama:**
- Use smaller model: `ollama pull llama3.2:3b`
- Reduce context window in config
- Ensure sufficient RAM (4GB+ recommended)

**For Cloud APIs:**
- Check internet connection
- Verify API rate limits
- Enable caching in `.env`

### Memory Issues (PostgreSQL)

```bash
# Clean old data
python -c "
from sentient_aura.memory_manager import MemoryManager
from sentient_aura.api_config import get_api_config
m = MemoryManager(get_api_config())
m.cleanup_old_data(days=30)
"

# Check database size
sudo -u postgres psql -d sentient_core -c "
  SELECT pg_size_pretty(pg_database_size('sentient_core'));
"
```

## Performance Optimization

### Reduce API Costs

1. **Enable Caching:**
   ```bash
   # In .env
   API_CACHE_ENABLED=true
   API_CACHE_TTL=600  # 10 minutes
   ```

2. **Use Local LLM (Ollama):**
   ```bash
   LLM_BACKEND_PRIORITY=ollama
   ```

3. **Limit Search Results:**
   ```bash
   SEARCH_MAX_RESULTS=3
   ```

4. **Increase Weather Cache TTL:**
   Weather doesn't change often - cache for 10-15 minutes.

### Improve Response Speed

1. **Use Smaller LLM:**
   ```bash
   OLLAMA_MODEL=llama3.2:3b  # Faster than 8b
   ```

2. **Reduce Context Window:**
   ```python
   # In config.py
   CONVERSATION_CONTEXT_WINDOW = 5  # Instead of 10
   ```

3. **Disable Unnecessary Features:**
   ```bash
   # In .env
   ENABLE_WEB_SEARCH=false  # If not needed
   ```

### Resource Usage

**Ollama Models:**
- `llama3.1:8b` - 5GB RAM, ~2-3s response
- `llama3.2:3b` - 2.5GB RAM, ~1-2s response
- `phi3:mini` - 2GB RAM, ~1s response

**PostgreSQL:**
- ~10-50MB for 1000 conversations
- Indexes created automatically
- Cleanup old data periodically

## Security Best Practices

1. **Never commit `.env` file:**
   ```bash
   # Already in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment-specific keys:**
   - Development: Free tier API keys
   - Production: Paid tier with higher limits

3. **Rotate API keys regularly:**
   - Every 90 days recommended
   - Immediately if exposed

4. **Limit Home Assistant token permissions:**
   - Create dedicated user for Sentient Core
   - Grant only necessary permissions

5. **Enable PostgreSQL authentication:**
   ```bash
   # Change default password
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'strong_password';"
   ```

6. **Use HTTPS for Home Assistant:**
   - Set `HOMEASSISTANT_VERIFY_SSL=true` in production
   - Use Let's Encrypt for free SSL certificates

## Advanced Configuration

### Custom LLM Prompts

Edit `llm_service.py` to customize system prompts:

```python
def _get_system_context(self) -> str:
    """Override to customize LLM behavior."""
    return "You are a helpful assistant specializing in..."
```

### Custom Search Ranking

Edit `search_service.py` to add custom result ranking:

```python
def _rank_results(self, results):
    """Custom ranking algorithm."""
    # Implement your own ranking logic
    pass
```

### Database Schema Extensions

Add custom tables to `memory_manager.py`:

```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_data (
        id SERIAL PRIMARY KEY,
        data JSONB NOT NULL
    );
""")
```

## Migration from Original Core

The enhanced core is fully backward compatible. To migrate:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Set up PostgreSQL (optional):**
   ```bash
   sudo systemctl start postgresql
   sudo -u postgres psql -c "CREATE DATABASE sentient_core;"
   ```

4. **Enable API integration:**
   ```python
   # In config.py
   ENABLE_API_INTEGRATION = True
   ```

5. **Replace core:**
   ```bash
   cd sentient_aura
   cp sentient_core.py sentient_core_original.py
   cp sentient_core_enhanced.py sentient_core.py
   ```

6. **Test:**
   ```bash
   python sentient_aura_main.py
   ```

**Rollback if needed:**
```bash
cp sentient_core_original.py sentient_core.py
```

## Support & Documentation

**Configuration Files:**
- `.env.template` - Environment variable template
- `config.py` - Feature flags and settings

**Service Modules:**
- `api_config.py` - Configuration management
- `llm_service.py` - LLM integration
- `search_service.py` - Web search
- `weather_service.py` - Weather API
- `homeassistant_bridge.py` - Smart home control
- `memory_manager.py` - Database storage
- `api_manager.py` - Unified API coordinator

**Core Integration:**
- `sentient_core_enhanced.py` - Enhanced core with API integration
- `sentient_core.py` - Original core (backup recommended)

**External Documentation:**
- Ollama: https://ollama.ai/
- Brave Search API: https://brave.com/search/api/docs
- OpenWeatherMap API: https://openweathermap.org/api/one-call-3
- Home Assistant REST API: https://developers.home-assistant.io/docs/api/rest/
- Anthropic Claude: https://docs.anthropic.com/
- OpenAI: https://platform.openai.com/docs/

## License & Credits

Sentient Core v4 API Integration System
Built for maximum capability and graceful offline operation.

**Third-party APIs:**
- Ollama (MIT License)
- Brave Search (Commercial API)
- OpenWeatherMap (Commercial API)
- Home Assistant (Apache 2.0)
- Anthropic Claude (Commercial API)
- OpenAI (Commercial API)

---

**Ready to unlock the full potential of your Sentient Core!** 🚀

For questions or issues, check the troubleshooting section or review the module documentation.
