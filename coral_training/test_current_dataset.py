#!/usr/bin/env python3
"""
Test and inspect the currently generated dataset
"""

import numpy as np
import json
from pathlib import Path
import sys

def test_dataset():
    """Test the dataset generated so far."""

    dataset_dir = Path(__file__).parent / 'dataset'

    # Find latest files
    input_files = sorted(dataset_dir.glob('inputs_rich_*.npy'))
    output_files = sorted(dataset_dir.glob('outputs_rich_*.npy'))
    metadata_files = sorted(dataset_dir.glob('metadata_rich_*.json'))

    if not input_files:
        print("❌ No dataset files found yet")
        return

    # Load latest dataset
    inputs = np.load(input_files[-1])
    outputs = np.load(output_files[-1])

    with open(metadata_files[-1], 'r') as f:
        metadata = json.load(f)

    print("=" * 70)
    print("CORAL TPU TRAINING DATASET INSPECTION")
    print("=" * 70)
    print()

    print(f"📊 Dataset Shape Information:")
    print(f"   Inputs:  {inputs.shape} (examples × features)")
    print(f"   Outputs: {outputs.shape} (examples × particles × coords)")
    print()

    print(f"📈 Dataset Statistics:")
    num_examples = inputs.shape[0] if inputs.ndim > 0 else 0
    print(f"   Examples generated: {num_examples}")
    print(f"   Features per example: {inputs.shape[1] if num_examples > 0 else 0}")

    if num_examples > 0:
        particles_per_example = outputs.shape[1] if outputs.ndim > 1 else 0
        print(f"   Particles per example: {particles_per_example}")
        print()

        # Feature analysis
        print(f"🔬 Feature Value Ranges (first example):")
        first_input = inputs[0]
        print(f"   Min:  {first_input.min():.4f}")
        print(f"   Max:  {first_input.max():.4f}")
        print(f"   Mean: {first_input.mean():.4f}")
        print()

        # Particle analysis
        print(f"🎨 Particle Coordinate Ranges (first example):")
        first_output = outputs[0]
        print(f"   X: [{first_output[:, 0].min():.2f}, {first_output[:, 0].max():.2f}]")
        print(f"   Y: [{first_output[:, 1].min():.2f}, {first_output[:, 1].max():.2f}]")
        print(f"   Z: [{first_output[:, 2].min():.2f}, {first_output[:, 2].max():.2f}]")
        print()

        # Scenario info
        print(f"📋 Scenarios Generated:")
        if 'scenarios' in metadata:
            for i, scenario in enumerate(metadata['scenarios'][:num_examples]):
                print(f"   {i+1:2d}. {scenario}")
        print()

        # Data quality checks
        print(f"✅ Data Quality Checks:")
        print(f"   No NaN values in inputs:  {not np.isnan(inputs).any()}")
        print(f"   No NaN values in outputs: {not np.isnan(outputs).any()}")
        print(f"   No Inf values in inputs:  {not np.isinf(inputs).any()}")
        print(f"   No Inf values in outputs: {not np.isinf(outputs).any()}")
        print()

        # Size estimates
        input_size_mb = inputs.nbytes / (1024 * 1024)
        output_size_mb = outputs.nbytes / (1024 * 1024)
        total_size_mb = input_size_mb + output_size_mb

        print(f"💾 Dataset Size:")
        print(f"   Inputs:  {input_size_mb:.2f} MB")
        print(f"   Outputs: {output_size_mb:.2f} MB")
        print(f"   Total:   {total_size_mb:.2f} MB")
        print()

        print("✓ Dataset test complete!")
        print()

    else:
        print("⚠️  Dataset files exist but are empty - generation still in progress")
        print()

if __name__ == '__main__':
    try:
        test_dataset()
    except Exception as e:
        print(f"❌ Error testing dataset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
