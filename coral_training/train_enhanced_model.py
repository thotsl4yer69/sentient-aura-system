#!/usr/bin/env python3
"""
Train Enhanced Sentient Core Model - 120 Features
Complete multi-sensor fusion for comprehensive environmental awareness

Architecture: 120 features → 128 → 30,000 → reshape(10,000, 3)
Dataset: 50 scenarios (30 multi-sensor + 20 companion)
Target: Edge TPU deployment (<6MB model)
"""

import sys
import tensorflow as tf
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedCoralTrainer:
    """Enhanced trainer for 120-feature multi-sensor model."""

    def __init__(self, num_features=120, num_particles=10000):
        self.num_features = num_features
        self.num_particles = num_particles
        self.num_outputs = num_particles * 3  # x, y, z coordinates

    def load_dataset(self, dataset_dir: Path):
        """Load the complete 50-scenario dataset."""
        logger.info("Loading enhanced dataset...")

        # Find latest complete dataset
        input_files = sorted(dataset_dir.glob('inputs_complete_*.npy'))
        output_files = sorted(dataset_dir.glob('outputs_complete_*.npy'))

        if not input_files or not output_files:
            raise FileNotFoundError(f"No complete dataset found in {dataset_dir}")

        input_file = input_files[-1]
        output_file = output_files[-1]

        logger.info(f"  Input features: {input_file.name}")
        logger.info(f"  Output particles: {output_file.name}")

        # Load data
        inputs = np.load(input_file)
        outputs = np.load(output_file)

        logger.info(f"  Input shape: {inputs.shape}")
        logger.info(f"  Output shape: {outputs.shape}")

        # Validate shapes
        num_examples = inputs.shape[0]
        assert inputs.shape == (num_examples, self.num_features), \
            f"Expected inputs shape ({num_examples}, {self.num_features}), got {inputs.shape}"
        assert outputs.shape == (num_examples, self.num_particles, 3), \
            f"Expected outputs shape ({num_examples}, {self.num_particles}, 3), got {outputs.shape}"

        # Convert to float32
        inputs = inputs.astype(np.float32)
        outputs = outputs.astype(np.float32)

        logger.info(f"✓ Loaded {num_examples} scenarios")
        logger.info(f"  Features per scenario: {self.num_features}")
        logger.info(f"  Particles per scenario: {self.num_particles}")

        return inputs, outputs

    def create_model(self):
        """
        Create Edge TPU-optimized model for 120 features.

        Architecture:
        - Input: (120,) features
        - Dense: 128 neurons, ReLU
        - Dense: 30,000 neurons (10,000 particles × 3 coords)
        - Reshape: (10,000, 3)

        Target size: ~4-5 MB (fits in Edge TPU 8MB cache)
        """
        logger.info("Creating enhanced model architecture...")

        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.num_features,), name='input'),
            tf.keras.layers.Dense(128, activation='relu', name='dense1'),
            tf.keras.layers.Dense(self.num_outputs, name='output'),
            tf.keras.layers.Reshape((self.num_particles, 3), name='reshape_particles')
        ], name='sentient_core_enhanced')

        logger.info("✓ Model created")
        logger.info(f"  Input: {self.num_features} features")
        logger.info(f"  Hidden: 128 neurons")
        logger.info(f"  Output: {self.num_particles} particles × 3 coords")

        return model

    def train_model(self, model, inputs, outputs, epochs=200, validation_split=0.2):
        """Train the enhanced model."""
        logger.info("\n" + "="*70)
        logger.info("TRAINING ENHANCED MODEL")
        logger.info("="*70)

        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        logger.info("\nModel summary:")
        model.summary(print_fn=logger.info)

        # Calculate model size
        param_count = model.count_params()
        estimated_size_mb = (param_count * 4) / (1024 * 1024)  # float32 = 4 bytes
        logger.info(f"\nEstimated model size: {estimated_size_mb:.2f} MB")

        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=20,
                restore_best_weights=True,
                verbose=1
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=0.00001,
                verbose=1
            )
        ]

        # Train
        logger.info(f"\nTraining for up to {epochs} epochs...")
        logger.info(f"  Training samples: {int(len(inputs) * (1 - validation_split))}")
        logger.info(f"  Validation samples: {int(len(inputs) * validation_split)}")

        history = model.fit(
            inputs, outputs,
            epochs=epochs,
            batch_size=4,  # Small batch for small dataset
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )

        # Final metrics
        final_loss = history.history['loss'][-1]
        final_val_loss = history.history['val_loss'][-1]
        final_mae = history.history['mae'][-1]
        final_val_mae = history.history['val_mae'][-1]

        logger.info("\n" + "="*70)
        logger.info("TRAINING COMPLETE")
        logger.info("="*70)
        logger.info(f"  Final training loss: {final_loss:.6f}")
        logger.info(f"  Final validation loss: {final_val_loss:.6f}")
        logger.info(f"  Final training MAE: {final_mae:.6f}")
        logger.info(f"  Final validation MAE: {final_val_mae:.6f}")
        logger.info("="*70)

        return model, history

    def save_keras_model(self, model, output_dir: Path):
        """Save Keras model."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        keras_path = output_dir / f'sentient_viz_enhanced_{timestamp}.h5'

        model.save(keras_path)
        size_mb = keras_path.stat().st_size / (1024 * 1024)

        logger.info(f"\n✓ Keras model saved: {keras_path.name}")
        logger.info(f"  Size: {size_mb:.2f} MB")

        return keras_path

    def convert_to_tflite(self, keras_model_path: Path, output_dir: Path, representative_data: np.ndarray):
        """Convert Keras model to TFLite with INT8 quantization."""
        logger.info("\n" + "="*70)
        logger.info("CONVERTING TO TFLITE")
        logger.info("="*70)

        # Load Keras model
        model = tf.keras.models.load_model(keras_model_path)

        # Create concrete function with static batch size
        logger.info("Creating concrete function with batch_size=1 (static shape)...")
        run_model = tf.function(lambda x: model(x))

        concrete_func = run_model.get_concrete_function(
            tf.TensorSpec(shape=[1, self.num_features], dtype=tf.float32, name='input')
        )

        logger.info(f"✓ Input shape: {concrete_func.inputs[0].shape}")
        logger.info(f"✓ Output shape: {concrete_func.outputs[0].shape}")

        # Convert to TFLite
        converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])

        # Representative dataset for quantization
        def representative_dataset():
            for i in range(min(100, len(representative_data))):
                yield [representative_data[i:i+1].astype(np.float32)]

        # Configure for Edge TPU
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = representative_dataset
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.float32
        converter.inference_output_type = tf.float32

        logger.info("Converting with INT8 quantization...")
        tflite_model = converter.convert()

        # Save
        timestamp = keras_model_path.stem.replace('sentient_viz_enhanced_', '')
        tflite_path = output_dir / f'sentient_viz_enhanced_{timestamp}_fixed.tflite'

        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)

        size_kb = len(tflite_model) / 1024
        size_mb = size_kb / 1024

        logger.info("="*70)
        logger.info("✓ TFLITE MODEL CREATED")
        logger.info(f"  Size: {size_kb:.2f} KB ({size_mb:.2f} MB)")
        logger.info(f"  Input shape: [1, {self.num_features}] (STATIC)")
        logger.info(f"  Output shape: [1, {self.num_particles}, 3] (STATIC)")
        logger.info(f"  Saved to: {tflite_path.name}")
        logger.info("="*70)

        # Verify shapes
        logger.info("\nVerifying tensor shapes...")
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
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
            return tflite_path, False
        else:
            logger.info("✓ All tensor dimensions are STATIC")
            logger.info("✓ Model is ready for Edge TPU compilation!")
            return tflite_path, True


def main():
    # Setup paths
    script_dir = Path(__file__).parent
    dataset_dir = script_dir / 'dataset'
    models_dir = script_dir / 'models'
    models_dir.mkdir(exist_ok=True)

    logger.info("="*70)
    logger.info("ENHANCED SENTIENT CORE TRAINING")
    logger.info("Multi-Sensor Fusion - 120 Features")
    logger.info("="*70)

    # Initialize trainer
    trainer = EnhancedCoralTrainer(num_features=120, num_particles=10000)

    # Load dataset
    inputs, outputs = trainer.load_dataset(dataset_dir)

    # Create model
    model = trainer.create_model()

    # Train model
    model, history = trainer.train_model(model, inputs, outputs, epochs=200)

    # Save Keras model
    keras_path = trainer.save_keras_model(model, models_dir)

    # Convert to TFLite with static shapes
    tflite_path, success = trainer.convert_to_tflite(keras_path, models_dir, inputs)

    if success:
        logger.info("\n" + "="*70)
        logger.info("SUCCESS! READY FOR EDGE TPU COMPILATION")
        logger.info("="*70)
        logger.info(f"\n📁 Upload this file to Google Colab:")
        logger.info(f"   {tflite_path.name}")
        logger.info(f"\n🔧 Then run on Colab:")
        logger.info(f"   !edgetpu_compiler {tflite_path.name} --show_operations")
        logger.info(f"\n✅ Expected result:")
        logger.info(f"   Number of Edge TPU subgraphs: 1")
        logger.info(f"   Operations mapped to Edge TPU: 100%")
        logger.info(f"   Off-chip memory used: 0.00B")
        logger.info("\n🎨 Features:")
        logger.info(f"   • 120 input features (all peripherals)")
        logger.info(f"   • 50 training scenarios")
        logger.info(f"   • Flipper Zero, WiFi, Bluetooth, Camera")
        logger.info(f"   • Cortana-inspired companion presence")
        logger.info(f"   • Everything in the world, visualized")
        logger.info("="*70)
        return 0
    else:
        logger.error("Model has dynamic dimensions. Cannot compile for Edge TPU.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
