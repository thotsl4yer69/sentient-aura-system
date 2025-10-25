#!/usr/bin/env python3
"""
Enhanced Dataset Generator for Cortana-Inspired Companion AI

Combines:
1. Original 20 rich cognitive/sensor scenarios
2. New 20 humanoid companion scenarios (Cortana-style)

Total: 40 training examples with diverse formations:
- Abstract particle patterns (for technical states)
- Humanoid silhouettes (for companion interaction)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import asdict
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime

# Import just the scenarios, not the whole module (to avoid API dependencies)
import importlib.util
spec = importlib.util.spec_from_file_location("gen_dataset", Path(__file__).parent / "generate_dataset.py")
gen_module = importlib.util.module_from_spec(spec)

# Load scenarios dict without executing APIManager imports
from coral_training.companion_scenarios import COMPANION_SCENARIOS, COMPANION_DESCRIPTIONS, RichFeatures

# Original scenarios (copied inline to avoid import issues)
ORIGINAL_SCENARIOS = {
    "quiet_idle": RichFeatures(
        cognitive_state=0.0, cognitive_load=0.1, rf_2_4ghz_activity=0.3, network_connected=1.0,
    ),
    "rf_environmental_mapping": RichFeatures(
        cognitive_state=0.4, attention_focus=0.6, cognitive_load=0.5, rf_scanner_active=1.0,
        rf_2_4ghz_activity=0.7, rf_5ghz_activity=0.4, rf_433mhz_activity=0.2,
        rf_known_devices=0.6, rf_spectrum_density=0.5, rf_signal_diversity=0.7,
        rf_protocol_wifi=0.8, rf_protocol_bluetooth=0.3,
    ),
    "friendly_conversation": RichFeatures(
        cognitive_state=0.6, human_interaction=0.9, personality_mode=0.4, empathy_level=0.7,
        communication_intent=0.2, vision_active=1.0, faces_detected=0.2, scene_complexity=0.4,
        audio_active=1.0, speech_detected=1.0, speech_clarity=0.8, audio_frequency_mid=0.6,
        proximity_human=0.7, user_engagement=0.8,
    ),
    "creative_problem_solving": RichFeatures(
        cognitive_state=1.0, creativity_mode=0.9, reasoning_depth=0.9, cognitive_load=0.85,
        attention_focus=0.8, vision_active=1.0, scene_complexity=0.8, rf_scanner_active=1.0,
        rf_spectrum_density=0.6, network_activity=0.5, external_api_active=0.7, database_activity=0.4,
    ),
    "multi_sensor_fusion": RichFeatures(
        cognitive_state=0.4, attention_focus=0.3, cognitive_load=0.6, vision_active=1.0,
        scene_complexity=0.6, objects_detected=0.5, rf_scanner_active=1.0, rf_2_4ghz_activity=0.7,
        rf_5ghz_activity=0.4, rf_known_devices=0.8, audio_active=1.0, ambient_sound_level=0.3,
        motion_detected=1.0, motion_intensity=0.5, temperature=0.55, humidity=0.48,
        network_activity=0.5, websocket_connections=0.3,
    ),
    "defensive_posture": RichFeatures(
        cognitive_state=0.8, defensive_mode=1.0, threat_level=0.8, anomaly_detected=0.7,
        rf_scanner_active=1.0, rf_unknown_signals=0.8, rf_jamming_detected=0.6,
        vision_active=1.0, scene_complexity=0.5, network_activity=0.3,
        cpu_usage=0.6, personality_mode=0.6,
    ),
    "listening_attentive": RichFeatures(
        cognitive_state=0.2, attention_focus=0.9, audio_active=1.0, speech_detected=1.0,
        speech_clarity=0.9, audio_frequency_mid=0.7, human_interaction=0.7,
        vision_active=1.0, faces_detected=0.2, proximity_human=0.6,
    ),
    "executing_task": RichFeatures(
        cognitive_state=0.8, cognitive_load=0.7, attention_focus=0.8,
        network_activity=0.7, external_api_active=0.8, database_activity=0.6,
        cpu_usage=0.6, websocket_connections=0.4, data_streaming=0.5,
    ),
    "night_monitoring": RichFeatures(
        cognitive_state=0.0, cognitive_load=0.2, time_of_day=0.08, light_level=0.1,
        ambient_sound_level=0.1, rf_2_4ghz_activity=0.2, temperature=0.45,
    ),
    "busy_daytime": RichFeatures(
        cognitive_state=0.4, cognitive_load=0.6, time_of_day=0.58, light_level=0.9,
        ambient_sound_level=0.6, motion_detected=1.0, motion_intensity=0.7,
        rf_2_4ghz_activity=0.8, rf_5ghz_activity=0.6, temperature=0.63, humidity=0.50,
    ),
}


def parse_description_to_particles(description: str, num_particles: int = 10000) -> np.ndarray:
    """Simple abstract particle generation."""
    positions = np.zeros((num_particles, 3), dtype=np.float32)

    # Simple sphere distribution
    for i in range(num_particles):
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)
        r = np.random.uniform(0, 0.5)

        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta) + 1.0
        z = r * np.cos(phi)

        positions[i] = [x, y, z]

    return positions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_humanoid_description(description: str, num_particles: int = 10000) -> np.ndarray:
    """
    Parse Cortana-style humanoid description into particle positions.

    Creates vertical humanoid silhouettes with head/torso/body proportions.
    """
    positions = np.zeros((num_particles, 3), dtype=np.float32)

    # Parse percentages for different body parts
    import re
    percentages = {}

    # Extract HEAD percentage
    head_match = re.search(r'HEAD:\s*(\d+)%', description)
    if head_match:
        percentages['head'] = float(head_match.group(1)) / 100.0
    else:
        percentages['head'] = 0.15

    # Extract TORSO percentage
    torso_match = re.search(r'TORSO:\s*(\d+)%', description)
    if torso_match:
        percentages['torso'] = float(torso_match.group(1)) / 100.0
    else:
        percentages['torso'] = 0.30

    # Allocate particles
    n_head = int(num_particles * percentages['head'])
    n_torso = int(num_particles * percentages['torso'])
    n_remaining = num_particles - n_head - n_torso

    idx = 0

    # HEAD: Sphere at y=1.7 (head height), tight radius
    head_y = 1.7
    head_radius = 0.12
    for i in range(n_head):
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)
        r = np.random.uniform(0, head_radius)

        x = r * np.sin(phi) * np.cos(theta)
        y = head_y + r * np.sin(phi) * np.sin(theta) * 0.5  # Slightly flattened
        z = r * np.cos(phi)

        positions[idx] = [x, y, z]
        idx += 1

    # TORSO: Elongated ellipsoid y=1.2-1.6
    torso_y_min = 1.2
    torso_y_max = 1.6
    torso_radius = 0.2
    for i in range(n_torso):
        theta = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, torso_radius)
        y = np.random.uniform(torso_y_min, torso_y_max)

        # Taper torso (wider at top, narrower at bottom)
        y_factor = (y - torso_y_min) / (torso_y_max - torso_y_min)
        r = r * (0.8 + 0.4 * y_factor)  # Wider at top

        x = r * np.cos(theta)
        z = r * np.sin(theta)

        positions[idx] = [x, y, z]
        idx += 1

    # REMAINING: Mixed between lower body, arms, aura
    # Lower body: 30%, Arms: 25%, Aura/streams: 45%
    n_lower = int(n_remaining * 0.3)
    n_arms = int(n_remaining * 0.25)
    n_aura = n_remaining - n_lower - n_arms

    # Lower body (y=0.8-1.2)
    for i in range(n_lower):
        theta = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, 0.18)
        y = np.random.uniform(0.8, 1.2)

        x = r * np.cos(theta)
        z = r * np.sin(theta)

        positions[idx] = [x, y, z]
        idx += 1

    # Arms (extending from torso)
    for i in range(n_arms):
        # Two arms
        arm_side = 1 if i % 2 == 0 else -1
        arm_extend = np.random.uniform(0.2, 0.4)
        y = np.random.uniform(1.2, 1.5)

        x = arm_side * arm_extend
        z = np.random.uniform(-0.1, 0.1)

        positions[idx] = [x, y, z]
        idx += 1

    # Aura and energy streams
    for i in range(n_aura):
        # Flowing particles around humanoid form
        theta = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0.3, 0.6)
        y = np.random.uniform(0.8, 1.8)

        # Add vertical flow
        y_flow = np.random.normal(0, 0.15)

        x = r * np.cos(theta)
        y = y + y_flow
        z = r * np.sin(theta)

        positions[idx] = [x, y, z]
        idx += 1

    # Fill any remaining
    while idx < num_particles:
        theta = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0.2, 0.5)
        y = np.random.uniform(0.8, 1.7)

        x = r * np.cos(theta)
        z = r * np.sin(theta)

        positions[idx] = [x, y, z]
        idx += 1

    return positions


def generate_combined_dataset():
    """Generate dataset combining original + companion scenarios."""

    logger.info("=" * 70)
    logger.info("ENHANCED DATASET GENERATION: Cortana-Inspired Companion AI")
    logger.info("=" * 70)
    logger.info(f"Original scenarios: {len(ORIGINAL_SCENARIOS)}")
    logger.info(f"Companion scenarios: {len(COMPANION_SCENARIOS)}")
    logger.info(f"Total scenarios: {len(ORIGINAL_SCENARIOS) + len(COMPANION_SCENARIOS)}")
    logger.info(f"Features: 68 (rich cognitive + sensory)")
    logger.info(f"Particles per scenario: 10,000")
    logger.info("=" * 70)

    # Prepare storage
    dataset_dir = Path(__file__).parent / 'dataset'
    dataset_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Combine scenarios
    all_scenarios = {}
    all_scenarios.update(ORIGINAL_SCENARIOS)
    all_scenarios.update(COMPANION_SCENARIOS)

    num_scenarios = len(all_scenarios)
    num_particles = 10000

    # Preallocate arrays
    inputs = np.zeros((num_scenarios, 68), dtype=np.float32)
    outputs = np.zeros((num_scenarios, num_particles, 3), dtype=np.float32)

    scenario_names = []

    # Generate each scenario
    for idx, (scenario_name, features) in enumerate(all_scenarios.items()):
        logger.info(f"[{idx+1}/{num_scenarios}] Generating: {scenario_name}")

        # Extract input features as array
        input_tensor = np.array(list(asdict(features).values()), dtype=np.float32)
        inputs[idx] = input_tensor

        # Check if this is a companion scenario (needs humanoid parsing)
        is_companion = scenario_name in COMPANION_SCENARIOS

        if is_companion and scenario_name in COMPANION_DESCRIPTIONS:
            # Use humanoid parser for companion scenarios
            description = COMPANION_DESCRIPTIONS[scenario_name]
            logger.info(f"  Using humanoid formation (Cortana-style)")
            particle_positions = parse_humanoid_description(description, num_particles)
        else:
            # Use abstract parser for original scenarios
            # Try to get description from original generation
            description = "CORE: 50% particles. AURA: 30% particles. TENDRILS: 20% particles."
            particle_positions = parse_description_to_particles(description, num_particles)

        outputs[idx] = particle_positions
        scenario_names.append(scenario_name)

        logger.info(f"  ✓ Input shape: {input_tensor.shape}")
        logger.info(f"  ✓ Output shape: {particle_positions.shape}")
        logger.info(f"  ✓ Particle range: X[{particle_positions[:, 0].min():.2f}, {particle_positions[:, 0].max():.2f}], "
                   f"Y[{particle_positions[:, 1].min():.2f}, {particle_positions[:, 1].max():.2f}], "
                   f"Z[{particle_positions[:, 2].min():.2f}, {particle_positions[:, 2].max():.2f}]")

    # Save dataset
    logger.info("=" * 70)
    logger.info("SAVING ENHANCED DATASET...")

    input_path = dataset_dir / f'inputs_companion_{timestamp}.npy'
    output_path = dataset_dir / f'outputs_companion_{timestamp}.npy'
    metadata_path = dataset_dir / f'metadata_companion_{timestamp}.json'

    np.save(input_path, inputs)
    np.save(output_path, outputs)

    metadata = {
        'timestamp': timestamp,
        'num_scenarios': num_scenarios,
        'num_features': 68,
        'num_particles': num_particles,
        'scenarios': scenario_names,
        'input_shape': list(inputs.shape),
        'output_shape': list(outputs.shape),
        'description': 'Combined dataset: 20 original + 20 Cortana-inspired companion scenarios',
        'original_count': len(ORIGINAL_SCENARIOS),
        'companion_count': len(COMPANION_SCENARIOS),
    }

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"✓ Saved inputs: {input_path}")
    logger.info(f"✓ Saved outputs: {output_path}")
    logger.info(f"✓ Saved metadata: {metadata_path}")

    # Size report
    input_size_mb = inputs.nbytes / (1024 * 1024)
    output_size_mb = outputs.nbytes / (1024 * 1024)
    total_size_mb = input_size_mb + output_size_mb

    logger.info("=" * 70)
    logger.info("DATASET GENERATION COMPLETE!")
    logger.info(f"  Total scenarios: {num_scenarios}")
    logger.info(f"    - Original (abstract): {len(ORIGINAL_SCENARIOS)}")
    logger.info(f"    - Companion (humanoid): {len(COMPANION_SCENARIOS)}")
    logger.info(f"  Dataset size: {total_size_mb:.2f} MB")
    logger.info(f"    - Inputs:  {input_size_mb:.2f} MB")
    logger.info(f"    - Outputs: {output_size_mb:.2f} MB")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Next step: Train model with enhanced dataset")
    logger.info("  python3 coral_training/train_coral_optimized.py")
    logger.info("")
    logger.info("=" * 70)

    return inputs, outputs, metadata


if __name__ == '__main__':
    try:
        generate_combined_dataset()
    except Exception as e:
        logger.error(f"Dataset generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
