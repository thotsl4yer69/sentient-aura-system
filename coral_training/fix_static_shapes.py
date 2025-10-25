#!/usr/bin/env python3
"""
Fix TFLite Model for Edge TPU - Static Tensor Shapes

The Edge TPU requires all tensor dimensions to be static (no None/dynamic sizes).
This script loads the trained Keras model and converts it with explicit static shapes.
"""

import sys
import tensorflow as tf
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_with_static_shapes(keras_model_path: Path, output_path: Path, representative_data: np.ndarray):
    """
    Convert Keras model to TFLite with fully static shapes for Edge TPU.

    Args:
        keras_model_path: Path to .h5 Keras model
        output_path: Path for output .tflite file
        representative_data: Sample inputs for quantization calibration
    """
    logger.info("="*70)
    logger.info("FIXING MODEL FOR EDGE TPU - STATIC SHAPES")
    logger.info("="*70)

    # Load Keras model
    logger.info(f"Loading Keras model: {keras_model_path}")
    model = tf.keras.models.load_model(keras_model_path)

    logger.info("\nOriginal model summary:")
    model.summary(print_fn=logger.info)

    # Create a concrete function with fixed batch size
    logger.info("\nCreating concrete function with batch_size=1 (static shape)...")

    # Get the model's call function
    run_model = tf.function(lambda x: model(x))

    # Create concrete function with explicit input shape [1, 68]
    concrete_func = run_model.get_concrete_function(
        tf.TensorSpec(shape=[1, 68], dtype=tf.float32, name='input')
    )

    logger.info("✓ Concrete function created with static input shape: [1, 68]")
    logger.info(f"✓ Output shape: {concrete_func.outputs[0].shape}")

    # Convert to TFLite using concrete function
    logger.info("\nConverting to TFLite with INT8 quantization...")
    converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])

    # Representative dataset for quantization
    def representative_dataset():
        """Provide sample inputs for quantization calibration."""
        for i in range(min(100, len(representative_data))):
            # Must match the concrete function's input shape: [1, 68]
            yield [representative_data[i:i+1].astype(np.float32)]

    # Configure for Edge TPU
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

    # CRITICAL: Use float32 I/O (Edge TPU will handle conversion)
    converter.inference_input_type = tf.float32
    converter.inference_output_type = tf.float32

    # Convert
    logger.info("Converting model...")
    tflite_model = converter.convert()

    # Save
    logger.info(f"\nSaving fixed TFLite model: {output_path}")
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    size_kb = len(tflite_model) / 1024
    size_mb = size_kb / 1024

    logger.info("="*70)
    logger.info("✓ FIXED MODEL CREATED")
    logger.info(f"  Size: {size_kb:.2f} KB ({size_mb:.2f} MB)")
    logger.info(f"  Input shape: [1, 68] (STATIC)")
    logger.info(f"  Output shape: [1, 10000, 3] (STATIC)")
    logger.info(f"  Saved to: {output_path}")
    logger.info("="*70)

    # Verify shapes
    logger.info("\nVerifying tensor shapes...")
    interpreter = tf.lite.Interpreter(model_path=str(output_path))
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    logger.info(f"  Input shape:  {input_details[0]['shape']}")
    logger.info(f"  Input dtype:  {input_details[0]['dtype']}")
    logger.info(f"  Output shape: {output_details[0]['shape']}")
    logger.info(f"  Output dtype: {output_details[0]['dtype']}")

    # Check for dynamic dimensions
    has_dynamic = False
    for dim in input_details[0]['shape']:
        if dim == -1 or dim is None:
            has_dynamic = True
    for dim in output_details[0]['shape']:
        if dim == -1 or dim is None:
            has_dynamic = True

    if has_dynamic:
        logger.error("❌ Model still has dynamic dimensions!")
        return False
    else:
        logger.info("✓ All tensor dimensions are STATIC (no -1 or None)")
        logger.info("\n✓ Model is ready for Edge TPU compilation!")
        return True


def main():
    models_dir = Path(__file__).parent / 'models'
    dataset_dir = Path(__file__).parent / 'dataset'

    # Find latest Keras model
    keras_models = sorted(models_dir.glob('sentient_viz_*.h5'))
    if not keras_models:
        logger.error("No Keras models found!")
        return 1

    latest_keras = keras_models[-1]
    logger.info(f"Using latest Keras model: {latest_keras.name}")

    # Find dataset for representative data
    companion_datasets = sorted(dataset_dir.glob('inputs_companion_*.npy'))
    if companion_datasets:
        dataset_path = companion_datasets[-1]
    else:
        rich_datasets = sorted(dataset_dir.glob('inputs_rich_*.npy'))
        if not rich_datasets:
            logger.error("No dataset found for representative data!")
            return 1
        dataset_path = rich_datasets[-1]

    logger.info(f"Loading representative data: {dataset_path.name}")
    representative_data = np.load(dataset_path)

    # Output path
    timestamp = latest_keras.stem.replace('sentient_viz_', '')
    output_path = models_dir / f'sentient_viz_{timestamp}_fixed.tflite'

    # Convert with static shapes
    success = convert_with_static_shapes(latest_keras, output_path, representative_data)

    if success:
        logger.info("\n" + "="*70)
        logger.info("NEXT STEP: UPLOAD TO GOOGLE COLAB")
        logger.info("="*70)
        logger.info(f"\nUpload this file to Colab: {output_path.name}")
        logger.info("\nThen run:")
        logger.info(f"  !edgetpu_compiler {output_path.name} --show_operations")
        logger.info("\nExpected output:")
        logger.info("  ✓ Number of Edge TPU subgraphs: 1")
        logger.info("  ✓ Operations mapped to Edge TPU: 100%")
        logger.info("  ✓ Off-chip memory used: 0.00B")
        logger.info("="*70)
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
