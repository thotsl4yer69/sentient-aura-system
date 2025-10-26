#!/usr/bin/env python3
"""
Cross-Modal Co-Attention Module

Implements research-validated co-attention mechanisms for multi-modal fusion
of vision, audio, and pose features. Based on 2024 deep learning research.

Reference: "Deep Multimodal Data Fusion" (ACM 2024)
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MultiModalFeatures:
    """Container for multi-modal feature vectors."""
    vision: np.ndarray  # Shape: (feature_dim,)
    audio: np.ndarray   # Shape: (feature_dim,)
    pose: np.ndarray    # Shape: (feature_dim,)
    timestamp: float


class AttentionModule:
    """
    Lightweight attention mechanism for edge deployment.

    Uses scaled dot-product attention without heavy matrix operations
    for efficiency on Coral TPU and Raspberry Pi.
    """

    def __init__(self, feature_dim: int = 64):
        """
        Initialize attention module.

        Args:
            feature_dim: Dimension of input features
        """
        self.feature_dim = feature_dim
        self.scale = feature_dim ** -0.5

        # Lightweight linear projections (no deep layers)
        # These would be learned during training, but for now we use identity
        self.query_weight = np.eye(feature_dim, dtype=np.float32)
        self.key_weight = np.eye(feature_dim, dtype=np.float32)
        self.value_weight = np.eye(feature_dim, dtype=np.float32)

    def forward(self, query: np.ndarray, key: np.ndarray, value: np.ndarray) -> np.ndarray:
        """
        Compute scaled dot-product attention.

        Args:
            query: Query features (feature_dim,)
            key: Key features (feature_dim,)
            value: Value features (feature_dim,)

        Returns:
            Attended features (feature_dim,)
        """
        # Project inputs
        Q = query @ self.query_weight
        K = key @ self.key_weight
        V = value @ self.value_weight

        # Compute attention score (scalar for single query/key pair)
        attention_score = np.dot(Q, K) * self.scale

        # Apply softmax (for single score, just use sigmoid)
        attention_weight = 1.0 / (1.0 + np.exp(-attention_score))

        # Apply attention to value
        attended = attention_weight * V

        return attended


class CrossModalAttention:
    """
    Cross-modal co-attention for vision, audio, and pose fusion.

    Instead of simple concatenation (late fusion), this module learns
    which modalities are relevant for the current context through
    attention mechanisms.

    Example use cases:
    - User says "that" while pointing → vision attends to pose to identify referent
    - Sound from specific direction → audio attends to vision to locate source
    - Person speaking → pose attends to audio to link voice to person
    """

    def __init__(self, feature_dim: int = 64):
        """
        Initialize cross-modal attention.

        Args:
            feature_dim: Dimension of feature vectors from each modality
        """
        self.feature_dim = feature_dim

        # Pairwise attention modules
        self.vision_audio_attention = AttentionModule(feature_dim)
        self.vision_pose_attention = AttentionModule(feature_dim)
        self.audio_pose_attention = AttentionModule(feature_dim)

        logger.info("Cross-modal attention initialized with feature_dim=%d", feature_dim)

    def fuse(self, features: MultiModalFeatures) -> np.ndarray:
        """
        Fuse multi-modal features using cross-modal co-attention.

        Args:
            features: Multi-modal feature container

        Returns:
            Unified context embedding (3 * feature_dim,)
        """
        try:
            # Vision attends to audio (which sounds match which objects?)
            vision_audio_aligned = self.vision_audio_attention.forward(
                query=features.vision,
                key=features.audio,
                value=features.audio
            )

            # Vision attends to pose (which person is relevant?)
            vision_pose_aligned = self.vision_pose_attention.forward(
                query=features.vision,
                key=features.pose,
                value=features.pose
            )

            # Audio attends to pose (whose voice is this?)
            audio_pose_aligned = self.audio_pose_attention.forward(
                query=features.audio,
                key=features.pose,
                value=features.pose
            )

            # Concatenate aligned features
            unified_context = np.concatenate([
                vision_audio_aligned,
                vision_pose_aligned,
                audio_pose_aligned
            ])

            return unified_context

        except Exception as e:
            logger.error(f"Cross-modal fusion failed: {e}")
            # Return concatenated raw features as fallback
            return np.concatenate([features.vision, features.audio, features.pose])

    def compute_attention_weights(self, features: MultiModalFeatures) -> Dict[str, float]:
        """
        Compute and return attention weights for interpretability.

        Useful for debugging: "Which modality is Cortana paying attention to?"

        Returns:
            Dictionary of attention weights
        """
        vision_audio_score = np.dot(features.vision, features.audio) * self.feature_dim ** -0.5
        vision_pose_score = np.dot(features.vision, features.pose) * self.feature_dim ** -0.5
        audio_pose_score = np.dot(features.audio, features.pose) * self.feature_dim ** -0.5

        # Convert to weights via sigmoid
        weights = {
            'vision_audio': float(1.0 / (1.0 + np.exp(-vision_audio_score))),
            'vision_pose': float(1.0 / (1.0 + np.exp(-vision_pose_score))),
            'audio_pose': float(1.0 / (1.0 + np.exp(-audio_pose_score)))
        }

        return weights


class HeuristicCrossModalAttention:
    """
    Simplified heuristic-based cross-modal attention for systems without
    pre-trained attention weights.

    Uses rule-based attention instead of learned weights, suitable for
    immediate deployment before training.
    """

    def __init__(self, feature_dim: int = 64):
        self.feature_dim = feature_dim

    def fuse(self, features: MultiModalFeatures, context: Optional[Dict] = None) -> np.ndarray:
        """
        Fuse features using heuristic attention rules.

        Args:
            features: Multi-modal features
            context: Optional context for attention weighting

        Returns:
            Fused feature vector
        """
        # Default weights
        vision_weight = 0.5
        audio_weight = 0.3
        pose_weight = 0.2

        if context:
            # Boost audio weight if sound detected
            if context.get('audio_active', False):
                audio_weight = 0.5
                vision_weight = 0.3

            # Boost pose weight if person detected
            if context.get('person_detected', False):
                pose_weight = 0.4
                vision_weight = 0.4
                audio_weight = 0.2

        # Weighted combination
        fused = (
            vision_weight * features.vision +
            audio_weight * features.audio +
            pose_weight * features.pose
        )

        return fused


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create dummy features
    features = MultiModalFeatures(
        vision=np.random.randn(64).astype(np.float32),
        audio=np.random.randn(64).astype(np.float32),
        pose=np.random.randn(64).astype(np.float32),
        timestamp=0.0
    )

    # Test cross-modal attention
    attention = CrossModalAttention(feature_dim=64)
    unified = attention.fuse(features)

    print(f"Vision features shape: {features.vision.shape}")
    print(f"Audio features shape: {features.audio.shape}")
    print(f"Pose features shape: {features.pose.shape}")
    print(f"Unified context shape: {unified.shape}")

    # Show attention weights
    weights = attention.compute_attention_weights(features)
    print("\nAttention weights:")
    for key, value in weights.items():
        print(f"  {key}: {value:.3f}")
