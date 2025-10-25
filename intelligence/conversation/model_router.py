#!/usr/bin/env python3
"""
Intelligent Model Router for Aura

Automatically selects the best LLM model based on query type, context,
and performance requirements. Routes between multiple Ollama models:

- qwen2.5-coder:7b → Technical queries (sensors, hardware, debugging, code)
- llama3.1:8b → Complex reasoning and nuanced conversation
- llama3.2:3b → Fast casual conversation
- mistral → Alternative general purpose
- llama3.2:1b → Ultra-fast simple responses

Uses keyword detection, context analysis, and conversation history
to make intelligent routing decisions in real-time.
"""

import logging
import re
import ollama
import psutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .ollama_engine import OllamaEngine, PersonalityTraits

logger = logging.getLogger("ModelRouter")


@dataclass
class ModelProfile:
    """Profile for an available model."""
    name: str
    size_gb: float
    speed_rating: int  # 1-5, 5=fastest
    quality_rating: int  # 1-5, 5=best
    specialization: str  # "code", "reasoning", "casual", "general"
    keywords: List[str]  # Trigger keywords for this model


class ModelRouter:
    """
    Intelligent model router for multi-model conversation.

    Analyzes incoming messages and context to select the optimal
    model for each response, balancing speed, quality, and specialization.
    """

    # Model profiles (ordered by preference for each category)
    MODELS = {
        "qwen2.5-coder:7b": ModelProfile(
            name="qwen2.5-coder:7b",
            size_gb=4.7,
            speed_rating=3,
            quality_rating=5,
            specialization="code",
            keywords=[
                "code", "python", "function", "class", "debug", "error",
                "sensor", "hardware", "arduino", "flipper", "coral", "tpu",
                "api", "database", "sql", "algorithm", "program", "script",
                "gpio", "i2c", "spi", "uart", "peripheral", "circuit"
            ]
        ),
        "llama3.1:8b": ModelProfile(
            name="llama3.1:8b",
            size_gb=4.7,
            speed_rating=3,
            quality_rating=5,
            specialization="reasoning",
            keywords=[
                "why", "how does", "explain", "understand", "think about",
                "analyze", "compare", "difference between", "relationship",
                "philosophy", "ethics", "meaning", "purpose", "complex"
            ]
        ),
        "llama3.2:3b": ModelProfile(
            name="llama3.2:3b",
            size_gb=2.0,
            speed_rating=5,
            quality_rating=4,
            specialization="casual",
            keywords=[
                "hello", "hi", "thanks", "thank you", "bye", "how are you",
                "weather", "time", "tell me about", "what's up", "chat"
            ]
        ),
        "mistral:latest": ModelProfile(
            name="mistral:latest",
            size_gb=4.1,
            speed_rating=4,
            quality_rating=4,
            specialization="general",
            keywords=[]  # Fallback model
        ),
        "llama3.2:1b": ModelProfile(
            name="llama3.2:1b",
            size_gb=1.3,
            speed_rating=5,
            quality_rating=3,
            specialization="fast",
            keywords=[
                "quick", "fast", "simple", "yes", "no", "ok", "sure"
            ]
        )
    }

    def __init__(
        self,
        personality: Optional[PersonalityTraits] = None,
        default_model: str = "llama3.2:3b",
        enable_routing: bool = True,
        max_loaded_models: int = 2  # Limit loaded models to prevent OOM
    ):
        """
        Initialize model router.

        Args:
            personality: Personality traits for all models
            default_model: Fallback model if routing fails
            enable_routing: Enable intelligent routing (False = always use default)
            max_loaded_models: Maximum number of models to keep loaded (default: 2 for 8GB RAM)
        """
        self.personality = personality or PersonalityTraits()
        self.default_model = default_model
        self.enable_routing = enable_routing
        self.max_loaded_models = max_loaded_models

        # Model engines (lazy-loaded)
        self._engines: Dict[str, OllamaEngine] = {}

        # LRU tracking: model_name -> last_access_time
        self._model_access_times: Dict[str, float] = {}

        # Routing statistics
        self.route_counts = {model: 0 for model in self.MODELS.keys()}
        self.total_routes = 0

        # Verify Ollama service is running
        self._check_ollama_health()

        logger.info(f"Model Router initialized (default: {default_model}, routing: {enable_routing})")

    def _get_engine(self, model_name: str) -> OllamaEngine:
        """
        Get or create engine for a model (lazy loading with LRU eviction).

        If model is not loaded and we're at max_loaded_models limit,
        evicts the least recently used model first.
        """
        import time

        # Check if model needs to be loaded
        if model_name not in self._engines:
            # Get model size and check memory availability
            model_size_gb = self.MODELS[model_name].size_gb
            self._ensure_memory_available(model_size_gb)

            # Check if we need to evict a model first (count-based)
            if len(self._engines) >= self.max_loaded_models:
                self._evict_lru_model()

            logger.info(f"Lazy-loading engine for model: {model_name}")
            self._engines[model_name] = OllamaEngine(
                model=model_name,
                personality=self.personality
            )

        # Update access time
        self._model_access_times[model_name] = time.time()

        return self._engines[model_name]

    def _evict_lru_model(self) -> None:
        """Evict the least recently used model to free memory."""
        if not self._model_access_times:
            return

        # Find least recently used model
        lru_model = min(
            self._model_access_times.items(),
            key=lambda x: x[1]
        )[0]

        logger.info(
            f"Evicting LRU model: {lru_model} "
            f"(loaded models: {len(self._engines)}/{self.max_loaded_models})"
        )

        # Remove engine and access time
        del self._engines[lru_model]
        del self._model_access_times[lru_model]

    def _ensure_memory_available(self, required_gb: float) -> None:
        """
        Ensure sufficient memory is available before loading a model.

        Args:
            required_gb: Model size in GB

        Raises:
            MemoryError: If insufficient memory even after evictions
        """
        # Get available memory
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024**3)

        # Require 1GB buffer
        needed_gb = required_gb + 1.0

        logger.debug(
            f"Memory check: {available_gb:.2f}GB available, "
            f"{needed_gb:.2f}GB needed (model={required_gb:.2f}GB + 1GB buffer)"
        )

        # If insufficient, try evicting models
        while available_gb < needed_gb and len(self._engines) > 0:
            logger.warning(
                f"Insufficient memory ({available_gb:.2f}GB < {needed_gb:.2f}GB). "
                "Evicting model..."
            )
            self._evict_lru_model()

            # Re-check memory after eviction
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)

        # Final check
        if available_gb < needed_gb:
            raise MemoryError(
                f"Insufficient memory to load model: {available_gb:.2f}GB available, "
                f"{needed_gb:.2f}GB required (model + buffer)"
            )

    def _check_ollama_health(self) -> None:
        """
        Verify Ollama service is running and accessible.

        Raises:
            ConnectionError: If Ollama service is not accessible
        """
        try:
            # Test connection by listing models
            available_models = ollama.list()

            # Handle both dict and object responses
            models = available_models.get('models', []) if isinstance(available_models, dict) else available_models['models']

            # Extract model names (handle both dict and object formats)
            model_names = []
            for m in models:
                if isinstance(m, dict):
                    model_names.append(m.get('name', m.get('model', 'unknown')))
                else:
                    model_names.append(getattr(m, 'name', getattr(m, 'model', 'unknown')))

            logger.debug(f"Ollama health check passed ({len(model_names)} models available)")

        except Exception as e:
            error_msg = (
                f"Ollama service health check failed: {e}. "
                "Ensure Ollama is running (systemctl status ollama or ollama serve)"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    def select_model(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Select the best model for a given message and context.

        Args:
            user_message: User's message
            context: Current sensor/world state context

        Returns:
            Tuple of (model_name, reason)
        """
        if not self.enable_routing:
            return (self.default_model, "routing disabled")

        message_lower = user_message.lower()
        scores: Dict[str, float] = {}

        # Score each model
        for model_name, profile in self.MODELS.items():
            score = 0.0

            # Keyword matching (primary signal)
            keyword_matches = sum(
                1 for keyword in profile.keywords
                if keyword in message_lower
            )
            score += keyword_matches * 10

            # Context-based routing
            if context:
                # Sensor/hardware context → prefer code model
                if "intelligence" in context or "coral" in str(context).lower():
                    if profile.specialization == "code":
                        score += 15

                # Complex activity detected → prefer reasoning model
                if "activity" in str(context) and profile.specialization == "reasoning":
                    score += 5

            # Message complexity analysis
            word_count = len(user_message.split())
            if word_count > 20 and profile.quality_rating >= 4:
                score += 5  # Complex query → higher quality model
            elif word_count < 5 and profile.speed_rating >= 4:
                score += 5  # Simple query → faster model

            # Question detection
            if any(q in message_lower for q in ["why", "how", "what", "when", "where"]):
                if profile.specialization == "reasoning":
                    score += 8

            # Code-related patterns
            if re.search(r'\b(def |class |import |function|variable|array|loop)\b', message_lower):
                if profile.specialization == "code":
                    score += 20

            scores[model_name] = score

        # Select highest scoring model
        best_model = max(scores.items(), key=lambda x: x[1])

        if best_model[1] == 0:
            # No clear winner → use default
            reason = "no strong signals, using default"
            return (self.default_model, reason)

        # Build reasoning string
        reason = f"score={best_model[1]:.1f} ({self.MODELS[best_model[0]].specialization})"

        return (best_model[0], reason)

    def generate(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        force_model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response using intelligently selected model.

        Args:
            user_message: User's message
            context: Current sensor/world state context
            force_model: Override routing and use specific model
            **kwargs: Additional arguments for OllamaEngine.generate()

        Returns:
            AI response string
        """
        # Select model
        if force_model:
            selected_model = force_model
            reason = "forced"
        else:
            selected_model, reason = self.select_model(user_message, context)

        # Update statistics
        self.route_counts[selected_model] = self.route_counts.get(selected_model, 0) + 1
        self.total_routes += 1

        logger.info(
            f"Routing to {selected_model} (reason: {reason}) "
            f"[total routes: {self.total_routes}]"
        )

        # Get engine and generate
        engine = self._get_engine(selected_model)
        response = engine.generate(user_message, context, **kwargs)

        return response

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        percentages = {
            model: (count / self.total_routes * 100) if self.total_routes > 0 else 0
            for model, count in self.route_counts.items()
        }

        return {
            "total_routes": self.total_routes,
            "route_counts": self.route_counts,
            "route_percentages": percentages,
            "available_models": list(self.MODELS.keys()),
            "loaded_models": list(self._engines.keys())
        }

    def clear_all_history(self):
        """Clear conversation history from all loaded engines."""
        for engine in self._engines.values():
            engine.clear_history()
        logger.info("Cleared history from all loaded engines")


# Convenience function for quick testing
def chat(message: str, context: Optional[Dict] = None) -> str:
    """Quick chat function with intelligent routing."""
    router = ModelRouter()
    return router.generate(message, context)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "="*60)
    print("INTELLIGENT MODEL ROUTER TEST")
    print("="*60 + "\n")

    # Create router
    router = ModelRouter(enable_routing=True)

    # Test context
    test_context = {
        "intelligence": {
            "inference": {
                "presence": {"detected": True, "confidence": 0.95},
                "activity": {"activity": "working", "confidence": 0.89}
            }
        }
    }

    # Test different query types
    test_queries = [
        ("Hello! How are you?", "casual greeting"),
        ("Can you explain how the Coral TPU sensor fusion works?", "technical query"),
        ("Why do you think presence detection is important?", "reasoning question"),
        ("def calculate_features(): pass - help me debug this", "code query"),
        ("What's the temperature right now?", "simple query"),
    ]

    print("Testing intelligent model routing:\n")

    for query, expected_type in test_queries:
        print(f"\nQuery: \"{query}\"")
        print(f"Expected type: {expected_type}")

        # Show routing decision
        selected_model, reason = router.select_model(query, test_context)
        print(f"→ Selected: {selected_model} ({reason})")
        print(f"  Specialization: {router.MODELS[selected_model].specialization}")

    # Show routing statistics
    print("\n" + "="*60)
    print("ROUTING STATISTICS")
    print("="*60)
    stats = router.get_routing_stats()
    for key, value in stats.items():
        if key != "loaded_models" and key != "available_models":
            print(f"{key}: {value}")

    print("\n✓ Model router test complete\n")
