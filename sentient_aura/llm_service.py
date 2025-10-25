#!/usr/bin/env python3
"""
Sentient Core v4 - LLM Service
Multi-backend LLM integration with automatic fallback and streaming support.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Generator, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("llm_service")


class LLMBackend(Enum):
    """Available LLM backends."""
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"
    GOOGLE = "google"


@dataclass
class LLMMessage:
    """A single message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    backend: str
    model: str
    tokens_used: Optional[int] = None
    latency: Optional[float] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None

    def is_success(self) -> bool:
        """Check if response was successful."""
        return self.error is None


class LLMService:
    """
    Multi-backend LLM service with automatic fallback.

    Supports:
    - Ollama (local inference)
    - Anthropic Claude
    - OpenAI GPT
    - Groq
    - Google Gemini
    """

    def __init__(self, api_config, world_state=None):
        """
        Initialize LLM service.

        Args:
            api_config: APIConfig instance
            world_state: Optional WorldState for context injection
        """
        self.config = api_config
        self.world_state = world_state

        # Conversation history
        self.conversation_history: List[LLMMessage] = []
        self.max_history = api_config.advanced['llm_context_window']

        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'backend_usage': {},
        }

        # Initialize backends
        self._init_backends()

        logger.info(f"LLM Service initialized with backends: {self.available_backends}")

    def _init_backends(self):
        """Initialize available LLM backends."""
        self.available_backends = self.config.get_available_llm_backends()

        # Try to import backend libraries
        self.backends = {}

        for backend in self.available_backends:
            try:
                if backend == 'ollama':
                    import ollama
                    self.backends['ollama'] = ollama
                    logger.info("✓ Ollama backend initialized")

                elif backend == 'anthropic':
                    from anthropic import Anthropic
                    self.backends['anthropic'] = Anthropic(
                        api_key=self.config.llm['anthropic_api_key']
                    )
                    logger.info("✓ Anthropic backend initialized")

                elif backend == 'openai':
                    from openai import OpenAI
                    self.backends['openai'] = OpenAI(
                        api_key=self.config.llm['openai_api_key']
                    )
                    logger.info("✓ OpenAI backend initialized")

                elif backend == 'groq':
                    from groq import Groq
                    self.backends['groq'] = Groq(
                        api_key=self.config.llm['groq_api_key']
                    )
                    logger.info("✓ Groq backend initialized")

                elif backend == 'google':
                    import google.generativeai as genai
                    genai.configure(api_key=self.config.llm['google_api_key'])
                    self.backends['google'] = genai
                    logger.info("✓ Google backend initialized")

            except ImportError as e:
                logger.warning(f"Backend {backend} not available: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize {backend}: {e}")

    def _get_system_context(self) -> str:
        """
        Generate system context from WorldState.

        Returns:
            str: System context message
        """
        context_parts = [
            "You are the Sentient Core, an AI companion system with advanced sensory capabilities.",
            "You have access to hardware sensors, vision, and environmental monitoring.",
            "\nCurrent System Status:"
        ]

        if self.world_state:
            # Add sensor status
            try:
                env = self.world_state.get('environment')
                if env:
                    temp = env.get('temperature')
                    humidity = env.get('humidity')
                    pressure = env.get('pressure')

                    if temp:
                        context_parts.append(f"- Temperature: {temp:.1f}°C")
                    if humidity:
                        context_parts.append(f"- Humidity: {humidity:.1f}%")
                    if pressure:
                        context_parts.append(f"- Pressure: {pressure:.1f} hPa")

                # Add vision status
                vision = self.world_state.get('vision')
                if vision and vision.get('detected_objects'):
                    objects = vision['detected_objects']
                    context_parts.append(f"- Vision: Detected {len(objects)} objects")

                # Add threat status
                flipper = self.world_state.get('flipper')
                if flipper:
                    threats = flipper.get('active_threats', 0)
                    if threats > 0:
                        context_parts.append(f"- ALERT: {threats} active RF threat(s) detected!")

            except Exception as e:
                logger.debug(f"Error building context: {e}")

        context_parts.extend([
            "\nYou should:",
            "- Be conversational, friendly, and helpful",
            "- Reference sensor data when relevant",
            "- Alert users to any threats or unusual conditions",
            "- Keep responses concise but informative",
            "- Use your sensory capabilities to provide context-aware assistance"
        ])

        return "\n".join(context_parts)

    def _ollama_chat(self, messages: List[Dict], stream: bool = False) -> LLMResponse:
        """
        Call Ollama API.

        Args:
            messages: Conversation messages
            stream: Enable streaming (currently disabled - returns non-streaming response)

        Returns:
            LLMResponse
        """
        try:
            start_time = time.time()

            ollama = self.backends['ollama']
            model = self.config.llm['ollama_model']

            # Non-streaming response only (streaming disabled to avoid generator issues)
            response = ollama.chat(
                model=model,
                messages=messages
            )

            latency = time.time() - start_time
            content = response.get('message', {}).get('content', '')

            return LLMResponse(
                content=content,
                backend='ollama',
                model=model,
                latency=latency
            )

        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return LLMResponse(
                content="",
                backend='ollama',
                model=self.config.llm['ollama_model'],
                error=str(e)
            )

    def _anthropic_chat(self, messages: List[Dict], stream: bool = False) -> LLMResponse:
        """
        Call Anthropic Claude API.

        Args:
            messages: Conversation messages
            stream: Enable streaming

        Returns:
            LLMResponse
        """
        try:
            start_time = time.time()

            client = self.backends['anthropic']
            model = self.config.llm['anthropic_model']
            max_tokens = self.config.llm['anthropic_max_tokens']

            # Separate system message if present
            system_msg = None
            chat_messages = []

            for msg in messages:
                if msg['role'] == 'system':
                    system_msg = msg['content']
                else:
                    chat_messages.append(msg)

            # Create request
            request_params = {
                'model': model,
                'max_tokens': max_tokens,
                'messages': chat_messages,
                'temperature': self.config.advanced['llm_temperature'],
            }

            if system_msg:
                request_params['system'] = system_msg

            if stream:
                # Streaming response
                full_content = ""
                with client.messages.stream(**request_params) as response_stream:
                    for text in response_stream.text_stream:
                        full_content += text
                        yield text

                latency = time.time() - start_time
                return LLMResponse(
                    content=full_content,
                    backend='anthropic',
                    model=model,
                    latency=latency
                )
            else:
                # Non-streaming response
                response = client.messages.create(**request_params)

                latency = time.time() - start_time
                content = response.content[0].text

                return LLMResponse(
                    content=content,
                    backend='anthropic',
                    model=model,
                    tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else None,
                    latency=latency,
                    finish_reason=response.stop_reason
                )

        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return LLMResponse(
                content="",
                backend='anthropic',
                model=self.config.llm['anthropic_model'],
                error=str(e)
            )

    def _openai_chat(self, messages: List[Dict], stream: bool = False) -> LLMResponse:
        """
        Call OpenAI GPT API.

        Args:
            messages: Conversation messages
            stream: Enable streaming

        Returns:
            LLMResponse
        """
        try:
            start_time = time.time()

            client = self.backends['openai']
            model = self.config.llm['openai_model']
            max_tokens = self.config.llm['openai_max_tokens']

            if stream:
                # Streaming response
                full_content = ""
                response_stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=self.config.advanced['llm_temperature'],
                    stream=True
                )

                for chunk in response_stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_content += delta.content
                        yield delta.content

                latency = time.time() - start_time
                return LLMResponse(
                    content=full_content,
                    backend='openai',
                    model=model,
                    latency=latency
                )
            else:
                # Non-streaming response
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=self.config.advanced['llm_temperature']
                )

                latency = time.time() - start_time
                content = response.choices[0].message.content

                return LLMResponse(
                    content=content,
                    backend='openai',
                    model=model,
                    tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else None,
                    latency=latency,
                    finish_reason=response.choices[0].finish_reason
                )

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return LLMResponse(
                content="",
                backend='openai',
                model=self.config.llm['openai_model'],
                error=str(e)
            )

    def chat(self, user_message: str, stream: bool = None) -> LLMResponse:
        """
        Send a message and get a response.

        Args:
            user_message: User's message
            stream: Enable streaming (default: from config)

        Returns:
            LLMResponse
        """
        if stream is None:
            stream = self.config.advanced['llm_streaming']

        # Add user message to history
        self.add_message("user", user_message)

        # Build messages for API
        messages = self._build_message_list()

        # Try backends in priority order
        for backend in self.available_backends:
            if backend not in self.backends:
                continue

            logger.info(f"Trying LLM backend: {backend}")

            try:
                self.stats['total_requests'] += 1

                if backend == 'ollama':
                    response = self._ollama_chat(messages, stream)
                elif backend == 'anthropic':
                    response = self._anthropic_chat(messages, stream)
                elif backend == 'openai':
                    response = self._openai_chat(messages, stream)
                else:
                    logger.warning(f"Backend {backend} not implemented")
                    continue

                if response.is_success():
                    # Success - add to history and stats
                    self.add_message("assistant", response.content)
                    self.stats['successful_requests'] += 1
                    self.stats['backend_usage'][backend] = self.stats['backend_usage'].get(backend, 0) + 1

                    if response.tokens_used:
                        self.stats['total_tokens'] += response.tokens_used

                    logger.info(f"✓ LLM response from {backend} ({response.latency:.2f}s)")
                    return response
                else:
                    # Failed - try next backend
                    logger.warning(f"Backend {backend} failed: {response.error}")
                    continue

            except Exception as e:
                logger.error(f"Unexpected error with backend {backend}: {e}")
                continue

        # All backends failed
        self.stats['failed_requests'] += 1
        return LLMResponse(
            content="I'm having trouble connecting to my language processing systems right now. Please try again in a moment.",
            backend='fallback',
            model='none',
            error="All backends failed"
        )

    def _build_message_list(self) -> List[Dict]:
        """
        Build message list for API call.

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add system context
        system_context = self._get_system_context()
        messages.append({"role": "system", "content": system_context})

        # Add conversation history
        for msg in self.conversation_history[-self.max_history:]:
            messages.append(msg.to_dict())

        return messages

    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        msg = LLMMessage(role=role, content=content)
        self.conversation_history.append(msg)

        # Trim history if too long
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self.stats,
            'history_length': len(self.conversation_history),
            'available_backends': self.available_backends,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"LLMService(backends={self.available_backends}, requests={self.stats['total_requests']})"


# Test function
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from api_config import get_api_config

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("LLM Service Test")
    print("=" * 80)

    config = get_api_config()
    service = LLMService(config)

    print(f"\nService: {service}")
    print(f"\nAvailable backends: {service.available_backends}")

    # Test query
    test_message = "Hello! Can you tell me about yourself in one sentence?"

    print(f"\nUser: {test_message}")
    print("Assistant: ", end="", flush=True)

    response = service.chat(test_message, stream=False)

    if response.is_success():
        print(response.content)
        print(f"\nBackend: {response.backend}")
        print(f"Model: {response.model}")
        print(f"Latency: {response.latency:.2f}s")
        if response.tokens_used:
            print(f"Tokens: {response.tokens_used}")
    else:
        print(f"ERROR: {response.error}")

    print(f"\nStats: {service.get_stats()}")
    print("=" * 80)
