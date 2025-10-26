#!/usr/bin/env python3
"""
Hybrid Emotion Model (Discrete + Continuous VAD)

Research-validated emotion model combining:
1. Discrete states (calm, curious, playful...) for interpretability
2. Continuous VAD dimensions (Valence-Arousal-Dominance) for granularity

Based on 2024 affective computing research showing hybrid models
provide superior emotional expressiveness and context awareness.

Reference: "Affective Computing Survey" (2024)
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import time

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """Discrete emotional states for Cortana's personality."""
    CALM = "calm"
    CURIOUS = "curious"
    PLAYFUL = "playful"
    ALERT = "alert"
    CONCERNED = "concerned"
    THINKING = "thinking"
    EXCITED = "excited"
    SAD = "sad"
    FOCUSED = "focused"
    PROTECTIVE = "protective"


@dataclass
class VADDimensions:
    """
    Continuous emotion dimensions (Valence-Arousal-Dominance model).

    Valence: 0=negative/unpleasant, 1=positive/pleasant
    Arousal: 0=calm/sleepy, 1=excited/alert
    Dominance: 0=submissive/controlled, 1=dominant/in-control
    """
    valence: float = 0.5
    arousal: float = 0.3
    dominance: float = 0.6

    def __post_init__(self):
        """Ensure values are in valid range [0, 1]."""
        self.valence = np.clip(self.valence, 0.0, 1.0)
        self.arousal = np.clip(self.arousal, 0.0, 1.0)
        self.dominance = np.clip(self.dominance, 0.0, 1.0)

    def to_dict(self) -> Dict[str, float]:
        return {
            'valence': float(self.valence),
            'arousal': float(self.arousal),
            'dominance': float(self.dominance)
        }


@dataclass
class EmotionalContext:
    """Context information for emotion inference."""
    vision_features: Dict = field(default_factory=dict)
    audio_features: Dict = field(default_factory=dict)
    pose_features: Dict = field(default_factory=dict)
    scene_understanding: Dict = field(default_factory=dict)
    temporal_memory: Dict = field(default_factory=dict)
    user_interaction: bool = False
    danger_detected: bool = False
    novel_event: bool = False


class HybridEmotionModel:
    """
    Hybrid emotion model combining discrete states with continuous VAD.

    Advantages:
    - Discrete states: Interpretable, easy to map to behaviors
    - Continuous VAD: Granular, smooth transitions, context-aware
    - Hybrid: Best of both worlds
    """

    def __init__(self):
        """Initialize hybrid emotion model."""
        # Current discrete state
        self.current_state = EmotionalState.CALM

        # Continuous VAD dimensions
        self.vad = VADDimensions(valence=0.6, arousal=0.3, dominance=0.6)

        # Mapping: discrete state → target VAD
        self.state_to_vad = {
            EmotionalState.CALM: (0.6, 0.2, 0.5),
            EmotionalState.CURIOUS: (0.7, 0.5, 0.4),
            EmotionalState.PLAYFUL: (0.9, 0.7, 0.6),
            EmotionalState.ALERT: (0.5, 0.8, 0.7),
            EmotionalState.CONCERNED: (0.3, 0.6, 0.5),
            EmotionalState.THINKING: (0.5, 0.4, 0.6),
            EmotionalState.EXCITED: (0.9, 0.9, 0.7),
            EmotionalState.SAD: (0.2, 0.3, 0.3),
            EmotionalState.FOCUSED: (0.6, 0.6, 0.7),
            EmotionalState.PROTECTIVE: (0.5, 0.7, 0.8),
        }

        # Cortana's personality traits (constant modifiers)
        self.personality_traits = {
            'curiosity': 0.8,
            'playfulness': 0.7,
            'protectiveness': 0.9,
            'sassiness': 0.6,
            'empathy': 0.8,
            'confidence': 0.7
        }

        # Temporal smoothing
        self.vad_history = []
        self.max_history = 10

        # Transition tracking
        self.last_state_change = time.time()
        self.state_duration = 0.0

        logger.info("Hybrid emotion model initialized: %s (V=%.2f, A=%.2f, D=%.2f)",
                    self.current_state.value, self.vad.valence, self.vad.arousal, self.vad.dominance)

    def update(self, context: EmotionalContext) -> Tuple[EmotionalState, VADDimensions]:
        """
        Update both discrete state and continuous VAD dimensions.

        Args:
            context: Current contextual information

        Returns:
            Tuple of (discrete_state, vad_dimensions)
        """
        # Infer new discrete state from context
        new_state = self._infer_discrete_state(context)

        # Update state if changed
        if new_state != self.current_state:
            logger.debug("Emotion state transition: %s → %s",
                        self.current_state.value, new_state.value)
            self.current_state = new_state
            self.last_state_change = time.time()
            self.state_duration = 0.0
        else:
            self.state_duration = time.time() - self.last_state_change

        # Get target VAD for current discrete state
        target_vad = VADDimensions(*self.state_to_vad[self.current_state])

        # Smooth transition to target VAD
        self._smooth_transition_to_vad(target_vad, alpha=0.15)

        # Apply contextual modulation (fine-tuning)
        self._apply_contextual_modulation(context)

        # Apply personality trait influences
        self._apply_personality_traits()

        # Store in history
        self.vad_history.append(self.vad.to_dict())
        if len(self.vad_history) > self.max_history:
            self.vad_history.pop(0)

        return self.current_state, self.vad

    def _infer_discrete_state(self, context: EmotionalContext) -> EmotionalState:
        """
        Infer discrete emotional state from context.

        Uses rule-based logic (could be replaced with learned model).
        """
        # Danger detected → ALERT or PROTECTIVE
        if context.danger_detected:
            return EmotionalState.PROTECTIVE if self.personality_traits['protectiveness'] > 0.7 else EmotionalState.ALERT

        # User interaction → context-dependent response
        if context.user_interaction:
            # Check user's emotional state from pose/audio
            user_emotion = context.pose_features.get('emotional_state', 'neutral')

            if user_emotion == 'sad' or user_emotion == 'tired':
                return EmotionalState.CONCERNED
            elif user_emotion == 'happy' or user_emotion == 'excited':
                return EmotionalState.PLAYFUL if self.personality_traits['playfulness'] > 0.6 else EmotionalState.CURIOUS
            else:
                return EmotionalState.CURIOUS

        # Novel/unexpected event → CURIOUS or ALERT
        if context.novel_event:
            # High arousal → alert, low arousal → curious
            if self.vad.arousal > 0.6:
                return EmotionalState.ALERT
            else:
                return EmotionalState.CURIOUS

        # Activity detection from scene understanding
        activity = context.scene_understanding.get('activity', 'idle')
        if activity == 'working':
            return EmotionalState.FOCUSED
        elif activity == 'playing' or activity == 'socializing':
            return EmotionalState.PLAYFUL
        elif activity == 'eating' or activity == 'relaxing':
            return EmotionalState.CALM

        # Default: remain in current state or return to calm
        if self.state_duration < 5.0:
            return self.current_state
        else:
            return EmotionalState.CALM

    def _smooth_transition_to_vad(self, target: VADDimensions, alpha: float = 0.1):
        """
        Smooth exponential transition to target VAD.

        Args:
            target: Target VAD dimensions
            alpha: Smoothing factor (0=no change, 1=instant)
        """
        self.vad.valence = (1 - alpha) * self.vad.valence + alpha * target.valence
        self.vad.arousal = (1 - alpha) * self.vad.arousal + alpha * target.arousal
        self.vad.dominance = (1 - alpha) * self.vad.dominance + alpha * target.dominance

    def _apply_contextual_modulation(self, context: EmotionalContext):
        """
        Fine-tune VAD based on context, independent of discrete state.

        Example: Cortana is "playful" but user looks tired
        → Keep playful state, but reduce arousal slightly
        """
        # User emotion influences
        user_emotion = context.pose_features.get('emotional_state')
        if user_emotion == 'sad' or user_emotion == 'tired':
            self.vad.arousal = max(0, self.vad.arousal - 0.1)  # Tone it down
            self.vad.valence = max(0, self.vad.valence - 0.05)  # Slight empathy

        # Audio emotional tone
        audio_tone = context.audio_features.get('emotional_tone')
        if audio_tone == 'angry':
            self.vad.dominance = max(0, self.vad.dominance - 0.2)  # Be less assertive
            self.vad.valence = max(0, self.vad.valence - 0.1)
        elif audio_tone == 'calm':
            self.vad.arousal = max(0, self.vad.arousal - 0.1)  # Match calmness

        # Danger modulation
        if context.danger_detected:
            self.vad.valence = max(0, self.vad.valence - 0.3)  # Less positive
            self.vad.arousal = min(1, self.vad.arousal + 0.2)  # More alert
            self.vad.dominance = min(1, self.vad.dominance + 0.1)  # Take charge

        # Novel events (curiosity boost)
        if context.novel_event:
            self.vad.arousal = min(1, self.vad.arousal + 0.15)  # Perk up
            if self.personality_traits['curiosity'] > 0.7:
                self.vad.valence = min(1, self.vad.valence + 0.1)  # Positive curiosity

    def _apply_personality_traits(self):
        """Apply Cortana's personality traits as permanent modifiers."""
        # Curiosity → slight arousal boost
        self.vad.arousal = min(1, self.vad.arousal + self.personality_traits['curiosity'] * 0.05)

        # Confidence → dominance boost
        self.vad.dominance = min(1, self.vad.dominance + self.personality_traits['confidence'] * 0.05)

        # Playfulness → valence boost
        self.vad.valence = min(1, self.vad.valence + self.personality_traits['playfulness'] * 0.05)

    def generate_particle_behaviors(self) -> Dict[str, float]:
        """
        Generate particle behavior parameters from current emotion.

        Uses discrete state for high-level behaviors,
        uses continuous VAD for parameter fine-tuning.

        Returns:
            Dictionary of 12 particle parameters for visualization
        """
        # Base behaviors from discrete state
        base_behaviors = self._get_base_behaviors_for_state()

        # Modulate with VAD for granularity
        behaviors = {
            'swarm_cohesion': base_behaviors['cohesion'] - (self.vad.arousal * 0.3),
            'flow_speed': base_behaviors['speed'] + (self.vad.arousal * 0.3),
            'turbulence': self.vad.arousal * 0.5,  # Directly tied to arousal
            'color_hue_shift': self.vad.valence,  # Valence maps to color mood
            'brightness': 0.5 + (self.vad.valence * 0.4),  # Positive = brighter
            'pulse_frequency': 0.3 + (self.vad.arousal * 0.5),  # Arousal = breathing rate
            'symmetry': base_behaviors['symmetry'],
            'vertical_bias': (self.vad.valence - 0.5) * 0.4,  # Positive = rising
            'horizontal_spread': base_behaviors['spread'],
            'depth_layering': 0.5 + (self.vad.dominance * 0.3),
            'particle_size': base_behaviors['size'],
            'glow_intensity': 0.5 + (self.vad.dominance * 0.4)  # Dominance = presence
        }

        # Ensure all values in valid ranges
        for key in behaviors:
            if key == 'vertical_bias':
                behaviors[key] = np.clip(behaviors[key], -1.0, 1.0)
            else:
                behaviors[key] = np.clip(behaviors[key], 0.0, 1.0)

        return behaviors

    def _get_base_behaviors_for_state(self) -> Dict[str, float]:
        """Get base behavior parameters for current discrete state."""
        state_behaviors = {
            EmotionalState.CALM: {
                'cohesion': 0.7, 'speed': 0.3, 'symmetry': 0.6, 'spread': 0.5, 'size': 0.7
            },
            EmotionalState.CURIOUS: {
                'cohesion': 0.6, 'speed': 0.5, 'symmetry': 0.5, 'spread': 0.6, 'size': 0.6
            },
            EmotionalState.PLAYFUL: {
                'cohesion': 0.5, 'speed': 0.7, 'symmetry': 0.4, 'spread': 0.7, 'size': 0.5
            },
            EmotionalState.ALERT: {
                'cohesion': 0.8, 'speed': 0.6, 'symmetry': 0.7, 'spread': 0.4, 'size': 0.6
            },
            EmotionalState.CONCERNED: {
                'cohesion': 0.7, 'speed': 0.4, 'symmetry': 0.6, 'spread': 0.5, 'size': 0.7
            },
            EmotionalState.THINKING: {
                'cohesion': 0.8, 'speed': 0.3, 'symmetry': 0.7, 'spread': 0.4, 'size': 0.6
            },
            EmotionalState.EXCITED: {
                'cohesion': 0.4, 'speed': 0.9, 'symmetry': 0.3, 'spread': 0.8, 'size': 0.5
            },
            EmotionalState.SAD: {
                'cohesion': 0.8, 'speed': 0.2, 'symmetry': 0.7, 'spread': 0.4, 'size': 0.8
            },
            EmotionalState.FOCUSED: {
                'cohesion': 0.9, 'speed': 0.4, 'symmetry': 0.8, 'spread': 0.3, 'size': 0.7
            },
            EmotionalState.PROTECTIVE: {
                'cohesion': 0.9, 'speed': 0.5, 'symmetry': 0.7, 'spread': 0.5, 'size': 0.7
            }
        }

        return state_behaviors.get(self.current_state, state_behaviors[EmotionalState.CALM])

    def get_gesture_for_state(self) -> str:
        """
        Get recommended gesture/animation for current state.

        Used by Cortana visualization to select appropriate movement pattern.
        """
        state_gestures = {
            EmotionalState.CALM: 'idle_sway',
            EmotionalState.CURIOUS: 'tilt_head',
            EmotionalState.PLAYFUL: 'bounce',
            EmotionalState.ALERT: 'step_back',
            EmotionalState.CONCERNED: 'lean_forward',
            EmotionalState.THINKING: 'hand_to_chin',
            EmotionalState.EXCITED: 'jump',
            EmotionalState.SAD: 'slump',
            EmotionalState.FOCUSED: 'lean_in',
            EmotionalState.PROTECTIVE: 'arms_wide'
        }

        return state_gestures.get(self.current_state, 'idle_sway')

    def get_state_info(self) -> Dict:
        """Get current emotional state information for debugging/UI."""
        return {
            'discrete_state': self.current_state.value,
            'vad': self.vad.to_dict(),
            'state_duration': self.state_duration,
            'personality': self.personality_traits,
            'gesture': self.get_gesture_for_state()
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create emotion model
    emotion = HybridEmotionModel()

    # Simulate contexts
    contexts = [
        EmotionalContext(user_interaction=True,
                        pose_features={'emotional_state': 'happy'}),
        EmotionalContext(novel_event=True),
        EmotionalContext(danger_detected=True),
        EmotionalContext(scene_understanding={'activity': 'working'}),
    ]

    print("\nHybrid Emotion Model Test\n" + "=" * 60)

    for i, ctx in enumerate(contexts):
        state, vad = emotion.update(ctx)
        behaviors = emotion.generate_particle_behaviors()

        print(f"\nContext {i+1}:")
        print(f"  State: {state.value}")
        print(f"  VAD: V={vad.valence:.2f}, A={vad.arousal:.2f}, D={vad.dominance:.2f}")
        print(f"  Gesture: {emotion.get_gesture_for_state()}")
        print(f"  Sample behaviors:")
        print(f"    Turbulence: {behaviors['turbulence']:.2f}")
        print(f"    Flow speed: {behaviors['flow_speed']:.2f}")
        print(f"    Color hue: {behaviors['color_hue_shift']:.2f}")
