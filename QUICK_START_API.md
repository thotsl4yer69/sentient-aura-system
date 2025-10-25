# Sentient Core v4 - API Integration Quick Start

**Goal:** Get the enhanced Sentient Core running with API integration in under 10 minutes.

## Prerequisites

- Sentient Core v4 already installed
- Virtual environment activated
- Internet connection

## 5-Minute Setup (Local LLM Only)

### Step 1: Install Dependencies (2 min)

```bash
cd ~/Sentient-Core-v4
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 min)

```bash
# Create .env file
cp .env.template .env

# Edit with nano
nano .env
```

**Minimum configuration - paste this:**

```bash
# Ollama (Local LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# PostgreSQL (Local Memory)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sentient_core
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Feature Flags
ENABLE_LLM_API=true
ENABLE_MEMORY_STORAGE=true
ENABLE_WEATHER_API=true
ENABLE_WEB_SEARCH=false
ENABLE_HOMEASSISTANT_API=false
```

Save and exit (Ctrl+X, Y, Enter)

### Step 3: Start Services (1 min)

```bash
# Start Ollama (if not running)
ollama serve &

# Verify Ollama is running
sleep 2
curl http://localhost:11434/api/tags

# Pull model if needed (only first time - may take 3-5 min)
ollama pull llama3.1:8b

# Start PostgreSQL
sudo systemctl start postgresql

# Create database (first time only)
sudo -u postgres psql -c "CREATE DATABASE sentient_core;" 2>/dev/null || true
```

### Step 4: Test Integration (1 min)

```bash
# Run test suite
python test_api_integration.py
```

**Expected output:**
```
✓ CONFIG: passed
✓ LLM: passed
⚠ SEARCH: skipped (no API key)
✓ WEATHER: passed (sensors)
⚠ HOMEASSISTANT: skipped
✓ MEMORY: passed
✓ API_MANAGER: passed
```

If you see 3+ passed tests, you're ready!

### Step 5: Deploy Enhanced Core (30 sec)

```bash
cd sentient_aura

# Backup original
cp sentient_core.py sentient_core_original.py

# Deploy enhanced version
cp sentient_core_enhanced.py sentient_core.py

cd ..
```

### Step 6: Launch! (30 sec)

```bash
python sentient_aura_main.py
```

**Try saying:**
- "Hello, how are you?" → LLM-powered response
- "What's the temperature?" → Sensor reading
- "Tell me about yourself" → Intelligent conversation

**Done! 🎉**

---

## 10-Minute Setup (Full Features)

Follow steps 1-5 above, then add these optional API keys:

### Add Brave Search (Free)

1. **Get API key:**
   - Visit: https://brave.com/search/api/
   - Sign up (free tier: 2000 queries/month)
   - Copy API key

2. **Add to .env:**
   ```bash
   nano .env
   ```

   Add line:
   ```bash
   BRAVE_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxxx
   ENABLE_WEB_SEARCH=true
   ```

3. **Test:**
   ```bash
   python sentient_aura/search_service.py
   ```

### Add Weather API (Free)

1. **Get API key:**
   - Visit: https://openweathermap.org/api
   - Sign up (free tier: 1000 calls/day)
   - Copy API key

2. **Add to .env:**
   ```bash
   OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   DEFAULT_LATITUDE=your_latitude
   DEFAULT_LONGITUDE=your_longitude
   ```

3. **Test:**
   ```bash
   python sentient_aura/weather_service.py
   ```

### Add Home Assistant (Optional)

1. **Get token:**
   - Open http://localhost:8123
   - Profile → Long-Lived Access Tokens
   - Create Token
   - Copy token

2. **Add to .env:**
   ```bash
   HOMEASSISTANT_URL=http://localhost:8123
   HOMEASSISTANT_TOKEN=your_token_here
   ENABLE_HOMEASSISTANT_API=true
   ```

3. **Test:**
   ```bash
   python sentient_aura/homeassistant_bridge.py
   ```

---

## Verification Checklist

After setup, verify each component:

```bash
# 1. Configuration loaded
python -c "from sentient_aura.api_config import get_api_config; print(get_api_config())"
# Should print: APIConfig(llm_backends=['ollama'], ...)

# 2. Ollama running
curl http://localhost:11434/api/tags
# Should return JSON with models

# 3. PostgreSQL accessible
PGPASSWORD=postgres psql -U postgres -d sentient_core -c "SELECT 1"
# Should print: 1

# 4. Enhanced core imported
python -c "from sentient_aura.sentient_core_enhanced import SentientCoreEnhanced; print('OK')"
# Should print: OK

# 5. API Manager works
python sentient_aura/api_manager.py
# Should show service health check
```

All checks passed? **You're ready to go!**

---

## Quick Commands

### Start System

```bash
cd ~/Sentient-Core-v4
source venv/bin/activate
python sentient_aura_main.py
```

### Test LLM

```bash
python -c "
from sentient_aura.api_manager import APIManager
api = APIManager()
response = api.chat('Say hello in 3 words')
print(response.content)
"
```

### Check Health

```bash
python -c "
from sentient_aura.api_manager import APIManager
health = APIManager().health_check()
print(f'LLM: {health.llm_available}')
print(f'Search: {health.search_available}')
print(f'Weather: {health.weather_available}')
print(f'Memory: {health.memory_available}')
"
```

### View Conversations

```bash
python -c "
from sentient_aura.memory_manager import MemoryManager
from sentient_aura.api_config import get_api_config
m = MemoryManager(get_api_config())
recent = m.get_recent_conversations(5)
for entry in recent:
    print(f'[{entry.role}] {entry.content}')
m.close()
"
```

### Clear Cache

```bash
python -c "
from sentient_aura.api_manager import APIManager
api = APIManager()
if api.search: api.search.clear_cache()
print('Cache cleared')
api.shutdown()
"
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
pip install -r requirements.txt
```

### "Connection refused to Ollama"

```bash
# Start Ollama
ollama serve &

# Wait 2 seconds
sleep 2

# Test
curl http://localhost:11434/api/tags
```

### "PostgreSQL connection failed"

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE sentient_core;"

# Test
PGPASSWORD=postgres psql -U postgres -d sentient_core -c "SELECT 1"
```

### "LLM responses are too slow"

```bash
# Use smaller/faster model
ollama pull llama3.2:3b

# Update .env
nano .env
# Change: OLLAMA_MODEL=llama3.2:3b
```

### "All tests skipped"

Edit `.env` file and enable at least:
- `ENABLE_LLM_API=true`
- `ENABLE_MEMORY_STORAGE=true`

Then restart Ollama and PostgreSQL.

---

## Usage Examples

### Ask a Question

```python
from sentient_aura.api_manager import APIManager

api = APIManager()
response = api.chat("What is quantum computing?")
print(response.content)
```

### Search the Web

```python
results = api.search("latest Raspberry Pi news", max_results=5)
for result in results.results:
    print(f"- {result.title}")
    print(f"  {result.url}")
```

### Get Weather

```python
weather = api.get_weather()
if weather.is_success():
    w = weather.current
    print(f"Temperature: {w.temperature}°C")
    print(f"Humidity: {w.humidity}%")
    print(f"Conditions: {w.description}")
```

### Control Smart Home

```python
# Turn on light
api.smart_home_control("light.living_room", "turn_on", brightness=128)

# Get status
status = api.get_smart_home_status()
print(status)
```

### Store Memory

```python
api.remember_conversation("user", "Turn on the lights")
api.remember_conversation("assistant", "I've turned on the lights", intent="smart_home")

# Retrieve context
context = api.get_conversation_context(window=5)
for entry in context:
    print(f"[{entry.role}] {entry.content}")
```

---

## Performance Tips

1. **Use smaller LLM model for speed:**
   ```bash
   OLLAMA_MODEL=llama3.2:3b  # Faster than 8b
   ```

2. **Enable caching:**
   ```bash
   API_CACHE_ENABLED=true
   API_CACHE_TTL=600  # 10 minutes
   ```

3. **Limit context window:**
   ```bash
   LLM_CONTEXT_WINDOW=5  # Fewer messages = faster
   ```

4. **Disable unused features:**
   ```bash
   ENABLE_WEB_SEARCH=false  # If not needed
   ```

---

## Next Steps

1. **Read full documentation:**
   ```bash
   cat API_SETUP.md | less
   ```

2. **Explore services:**
   ```bash
   ls sentient_aura/*_service.py
   ```

3. **Review configuration:**
   ```bash
   cat .env.template
   ```

4. **Check logs:**
   ```bash
   tail -f logs/sentient_aura.log
   ```

5. **Join development:**
   - Add new API services
   - Improve intent detection
   - Enhance natural language processing

---

## Rollback (if needed)

```bash
cd sentient_aura
cp sentient_core_original.py sentient_core.py
cd ..
```

System will revert to original behavior (no API integration).

---

## Support

- **Full Setup Guide:** `API_SETUP.md`
- **Summary:** `API_INTEGRATION_SUMMARY.md`
- **Test Suite:** `test_api_integration.py`

**Ready to unleash the full power of Sentient Core v4!** 🚀
