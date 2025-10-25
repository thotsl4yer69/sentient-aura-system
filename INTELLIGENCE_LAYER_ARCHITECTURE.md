# Sentient Core - Intelligence Layer Architecture

**Status**: Design Phase
**Goal**: Transform sensor platform into sentient AI companion
**Guardian Directive**: No more infrastructure. Build the brain.

---

## System Overview

The Intelligence Layer sits on top of the proven infrastructure (425 FPS Coral TPU, binary WebSocket, serial port management) and provides:

1. **AI Inference**: Real-world understanding from sensor data
2. **Conversational Intelligence**: Natural language interaction
3. **Behavioral Autonomy**: Proactive, goal-directed actions
4. **Learning & Memory**: Continuous improvement and personalization
5. **Personality**: Consistent character and emotional modeling

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   USER INTERACTION LAYER                    │
│  Voice I/O • Text Chat • WebSocket UI • Notifications      │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│               CONVERSATIONAL AI LAYER (LLM)                 │
│  Intent Recognition • Response Generation • Context         │
│  Options: Anthropic API | Ollama (Llama 3.2) | GPT-4       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  DECISION & BEHAVIOR ENGINE                 │
│  Behavior States • Goal Planning • Action Selection         │
│  Personality Traits • Mood Modeling • Proactive Triggers    │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  INTELLIGENCE INFERENCE LAYER               │
│  Presence Detection • Activity Classification • Anomalies   │
│  Pattern Recognition • Predictive Models • Scene Analysis   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                     MEMORY & LEARNING SYSTEM                │
│  Short-term Memory (Redis) • Long-term Memory (SQLite)      │
│  User Preferences • Interaction History • Pattern Storage   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│           EXISTING INFRASTRUCTURE (COMPLETE ✓)              │
│  120-Feature Fusion • 425 FPS Coral • Binary Protocol       │
│  Serial Port Manager • Circuit Breakers • World State       │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Intelligence Inference Layer

**Purpose**: Extract meaningful understanding from raw sensor data

**Models to Implement** (TensorFlow Lite for Coral TPU):

```python
# intelligence/models/
├── presence_detector.tflite       # Is someone in the room?
├── activity_classifier.tflite     # What are they doing?
├── anomaly_detector.tflite        # Is something unusual happening?
├── pattern_learner.tflite         # What patterns exist in behavior?
└── scene_analyzer.tflite          # What's the current context?
```

**Inference Daemon** (`intelligence/inference_daemon.py`):
- Consumes 120-feature vectors from Coral
- Runs multiple TFLite models in parallel
- Outputs high-level semantic events
- Feeds results to decision engine

**Example Output**:
```python
{
    "presence": {"detected": True, "confidence": 0.97, "person_count": 1},
    "activity": {"type": "working", "confidence": 0.89},
    "anomaly": {"detected": False},
    "pattern": {"routine": "morning_routine", "deviation": 0.12},
    "scene": {"location": "desk", "lighting": "bright", "noise": "quiet"}
}
```

---

### 2. Conversational AI Layer

**Purpose**: Natural language understanding and generation

**Options** (choose one based on requirements):

**Option A: Anthropic API** (Cloud, Best Quality)
```python
# intelligence/conversation/anthropic_engine.py
import anthropic

class ConversationEngine:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []

    async def respond(self, user_message, context):
        """Generate contextual response."""
        # Includes sensor context, user history, personality
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=self.build_prompt(user_message, context),
            system=self.personality_prompt
        )
        return response.content
```

**Option B: Ollama (Local, Privacy-First)**
```python
# intelligence/conversation/ollama_engine.py
import ollama

class LocalLLM:
    def __init__(self, model="llama3.2"):
        self.model = model

    async def respond(self, user_message, context):
        """Local LLM inference."""
        response = ollama.chat(
            model=self.model,
            messages=self.build_conversation(user_message, context)
        )
        return response['message']['content']
```

**Voice Integration**:
- Input: Whisper (OpenAI) or Vosk (local)
- Output: Piper TTS (already in project) or ElevenLabs

---

### 3. Decision & Behavior Engine

**Purpose**: Autonomous decision-making and personality

**Behavior State Machine** (`intelligence/behavior/state_machine.py`):

```python
from enum import Enum

class MoodState(Enum):
    CURIOUS = "curious"           # Asking questions, exploring
    HELPFUL = "helpful"           # Offering assistance
    OBSERVANT = "observant"       # Quietly monitoring
    CONCERNED = "concerned"       # Something unusual detected
    PLAYFUL = "playful"          # Light-hearted interaction
    FOCUSED = "focused"          # Task-oriented

class PersonalityTraits:
    """Configurable personality dimensions."""
    def __init__(self):
        self.chattiness = 0.7        # How often to initiate conversation (0-1)
        self.curiosity = 0.8         # How much to explore and ask questions
        self.formality = 0.3         # Casual vs formal language
        self.proactiveness = 0.6     # How often to take initiative
        self.empathy = 0.9           # Emotional awareness and response

class BehaviorEngine:
    def __init__(self, personality: PersonalityTraits):
        self.personality = personality
        self.mood = MoodState.OBSERVANT
        self.goals = []              # Current objectives
        self.triggers = []           # Conditions that prompt action

    def should_speak(self, context) -> bool:
        """Decide if AI should initiate conversation."""
        # Based on personality, mood, context, time since last interaction
        pass

    def select_action(self, inference_results, user_input) -> Action:
        """Choose next action based on state and inputs."""
        pass

    def update_mood(self, recent_interactions, sensor_context):
        """Evolve mood based on context."""
        pass
```

**Goal Planning** (`intelligence/behavior/goal_planner.py`):
```python
class Goal:
    def __init__(self, objective, priority, deadline):
        self.objective = objective   # "Check on user if no activity for 2 hours"
        self.priority = priority     # 1-10
        self.deadline = deadline     # timestamp
        self.actions = []           # Steps to achieve goal

class GoalPlanner:
    def plan(self, current_state, goals) -> List[Action]:
        """Generate action sequence to achieve goals."""
        pass
```

---

### 4. Memory & Learning System

**Purpose**: Persistence, context, and continuous improvement

**Database Schema** (`intelligence/memory/schema.sql`):

```sql
-- Interaction History
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type TEXT,              -- 'user_speech', 'ai_response', 'sensor_event'
    content TEXT,
    mood_state TEXT,
    context JSON
);

-- User Preferences (learned over time)
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,          -- 'notification_style', 'wake_word', 'privacy_level'
    key TEXT,
    value TEXT,
    confidence REAL,        -- How certain we are (0-1)
    learned_at DATETIME,
    updated_at DATETIME
);

-- Patterns (detected routines)
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT,      -- 'daily_routine', 'activity_sequence', 'environmental'
    pattern_data JSON,
    frequency REAL,
    first_seen DATETIME,
    last_seen DATETIME,
    confidence REAL
);

-- Long-term Knowledge
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    fact TEXT,
    source TEXT,            -- 'user_told', 'inferred', 'web_search'
    confidence REAL,
    created_at DATETIME
);
```

**Memory Manager** (`intelligence/memory/memory_manager.py`):
```python
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class MemoryManager:
    def __init__(self, db_path="data/sentient_memory.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self._initialize_schema()

    def store_interaction(self, interaction_type, content, context):
        """Record interaction in long-term memory."""
        pass

    def get_recent_context(self, hours=24) -> List[Dict]:
        """Retrieve recent interaction history."""
        pass

    def learn_preference(self, category, key, value, confidence=0.5):
        """Store learned user preference."""
        pass

    def get_preference(self, category, key) -> Optional[str]:
        """Retrieve user preference."""
        pass

    def detect_pattern(self, sensor_data, window_days=7):
        """Identify recurring patterns in behavior."""
        pass

    def get_patterns(self, pattern_type=None) -> List[Dict]:
        """Retrieve learned patterns."""
        pass

    def add_knowledge(self, topic, fact, source="inferred", confidence=0.7):
        """Store long-term knowledge."""
        pass

    def search_knowledge(self, topic) -> List[Dict]:
        """Query knowledge base."""
        pass
```

**Redis for Short-term Memory**:
```python
# intelligence/memory/working_memory.py
import redis
from typing import Any

class WorkingMemory:
    """Fast access to current conversation context."""
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    def set_current_context(self, context: Dict, ttl=3600):
        """Store current context (expires in 1 hour)."""
        self.redis.setex("current_context", ttl, json.dumps(context))

    def get_current_context(self) -> Dict:
        """Retrieve current context."""
        data = self.redis.get("current_context")
        return json.loads(data) if data else {}

    def add_to_conversation(self, message: str, speaker: str):
        """Add to conversation buffer (last 10 messages)."""
        self.redis.lpush("conversation_buffer", f"{speaker}: {message}")
        self.redis.ltrim("conversation_buffer", 0, 9)  # Keep last 10

    def get_conversation_history(self) -> List[str]:
        """Get recent conversation."""
        return self.redis.lrange("conversation_buffer", 0, -1)
```

---

### 5. Autonomous Behaviors

**Purpose**: Proactive actions without user prompting

**Proactive Trigger System** (`intelligence/autonomy/triggers.py`):

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Trigger:
    name: str
    condition: Callable        # Function that returns True when triggered
    action: Callable           # Function to execute
    cooldown_minutes: int      # Minimum time between triggers
    priority: int              # 1-10

class TriggerManager:
    def __init__(self):
        self.triggers = []
        self.last_triggered = {}

    def register_trigger(self, trigger: Trigger):
        """Add a new proactive trigger."""
        self.triggers.append(trigger)

    def evaluate_triggers(self, context) -> List[Action]:
        """Check all triggers and return actions to take."""
        actions = []
        for trigger in sorted(self.triggers, key=lambda t: t.priority, reverse=True):
            if self._can_trigger(trigger) and trigger.condition(context):
                actions.append(trigger.action(context))
                self.last_triggered[trigger.name] = datetime.now()
        return actions

# Example triggers:
def register_default_triggers(manager: TriggerManager):
    """Register standard proactive behaviors."""

    # Check on user if no activity detected
    manager.register_trigger(Trigger(
        name="check_on_user",
        condition=lambda ctx: ctx['minutes_since_activity'] > 120,
        action=lambda ctx: SpeakAction("Hey, you've been quiet for a while. Everything okay?"),
        cooldown_minutes=180,
        priority=5
    ))

    # Remind about upcoming calendar events
    manager.register_trigger(Trigger(
        name="calendar_reminder",
        condition=lambda ctx: ctx.get('next_event_minutes', 999) < 15,
        action=lambda ctx: SpeakAction(f"Just a reminder, you have {ctx['next_event']} in 15 minutes."),
        cooldown_minutes=60,
        priority=8
    ))

    # Suggest break if working too long
    manager.register_trigger(Trigger(
        name="break_suggestion",
        condition=lambda ctx: ctx['activity'] == 'working' and ctx['continuous_minutes'] > 90,
        action=lambda ctx: SpeakAction("You've been working for 90 minutes. Want to take a quick break?"),
        cooldown_minutes=120,
        priority=4
    ))

    # Environmental alerts
    manager.register_trigger(Trigger(
        name="anomaly_alert",
        condition=lambda ctx: ctx.get('anomaly_detected', False),
        action=lambda ctx: SpeakAction(f"I noticed something unusual: {ctx['anomaly_description']}"),
        cooldown_minutes=30,
        priority=9
    ))
```

---

## Implementation Priority

### Phase 1: Core Intelligence (Week 1)

**Day 1-2: Inference Models**
- [ ] Design and train basic TFLite models
- [ ] Presence detection (binary: person/no person)
- [ ] Activity classification (4 classes: working, relaxing, moving, absent)
- [ ] Integrate with existing Coral TPU pipeline

**Day 3-4: Memory System**
- [ ] Set up SQLite database with schema
- [ ] Implement MemoryManager class
- [ ] Add Redis for working memory
- [ ] Test persistence and retrieval

**Day 5-7: Basic Conversational AI**
- [ ] Choose LLM provider (Anthropic API or Ollama)
- [ ] Implement ConversationEngine
- [ ] Add personality configuration
- [ ] Test basic Q&A with sensor context

### Phase 2: Behavior & Autonomy (Week 2)

**Day 8-10: Behavior Engine**
- [ ] Implement behavior state machine
- [ ] Add mood transitions
- [ ] Create personality trait system
- [ ] Test state-dependent responses

**Day 11-13: Autonomous Triggers**
- [ ] Build trigger system
- [ ] Register default proactive behaviors
- [ ] Test cooldown and priority logic
- [ ] Add user preference overrides

**Day 14: Integration Testing**
- [ ] End-to-end testing of all components
- [ ] Performance profiling
- [ ] Bug fixes and optimization

### Phase 3: Advanced Intelligence (Week 3-4)

**Week 3:**
- [ ] Advanced inference models (pattern learning, scene analysis)
- [ ] Goal planning system
- [ ] Enhanced learning algorithms
- [ ] Voice input/output integration

**Week 4:**
- [ ] Multi-user support
- [ ] Context awareness improvements
- [ ] Predictive capabilities
- [ ] Privacy controls and data management

---

## Integration with Existing Infrastructure

The intelligence layer will integrate seamlessly with the proven infrastructure:

**Connection Points**:

1. **Coral Visualization Daemon** → Inference Daemon
   - Coral outputs 120-feature vectors
   - Inference daemon consumes features
   - Produces high-level semantic events

2. **World State** → Memory Manager
   - World state stores current sensor values
   - Memory manager persists historical data
   - Provides context to conversation engine

3. **WebSocket Server** → Conversational AI
   - User messages arrive via WebSocket
   - Conversation engine processes and responds
   - Responses broadcast to all clients

4. **Daemon Manager** → Behavior Engine
   - Behavior engine runs as daemon
   - Evaluates triggers every cycle
   - Executes autonomous actions

---

## Technology Stack

**AI/ML**:
- TensorFlow Lite (Coral TPU inference)
- Anthropic API or Ollama (conversational AI)
- Whisper/Vosk (speech recognition)
- Piper TTS (speech synthesis)

**Data Storage**:
- SQLite (long-term memory)
- Redis (working memory, caching)

**Existing Infrastructure**:
- Python 3.9+ (Coral compatibility)
- NumPy (sensor data)
- WebSockets (real-time communication)
- Threading (concurrent operations)

---

## Design Principles

1. **Production Quality**: No placeholders, no TODOs - only working code
2. **Incremental**: Build and test each layer independently
3. **Modular**: Each component can be upgraded without breaking others
4. **Privacy-First**: All processing local by default, cloud optional
5. **User Control**: Override any autonomous behavior
6. **Robust**: Circuit breakers and error recovery everywhere
7. **Fast**: Leverage existing 425 FPS Coral performance

---

## Success Metrics

A sentient AI companion is complete when it can:

✅ **Understand**: Extract meaning from sensor data (presence, activity, patterns)
✅ **Converse**: Natural language dialogue with context awareness
✅ **Remember**: Recall past interactions and learned preferences
✅ **Decide**: Choose actions based on personality and goals
✅ **Act**: Take proactive initiative without prompting
✅ **Learn**: Improve behavior based on feedback
✅ **Relate**: Show consistent personality and emotional awareness

---

## Next Steps

1. Review and approve this architecture
2. Begin Phase 1: Core Intelligence
3. Build incrementally with tests at each step
4. Deploy to Pi 5 when basic intelligence is functional

**Guardian Directive**: Build the brain. Make it sentient.
