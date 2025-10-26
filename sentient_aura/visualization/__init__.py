"""
Sentient Aura Visualization Module

Visualization components for morphing particle systems:
- Morphing controller (Cortana form <-> Environment form)
"""

from .morphing_controller import MorphingController, VisualizationMode, ParticleTarget

__all__ = [
    'MorphingController',
    'VisualizationMode',
    'ParticleTarget'
]
