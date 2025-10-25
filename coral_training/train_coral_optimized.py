#!/usr/bin/env python3
"""
Edge TPU Optimized Training Script for Sentient Core Particle Visualization

This script trains a TensorFlow Lite model optimized for Coral Edge TPU deployment.
Follows all official Coral best practices for maximum performance.

Target Specifications:
- Model size: <6 MB (fits in Edge TPU SRAM cache)
- Inference speed: 2-5ms per frame (200+ FPS capability)
- 100% Edge TPU operation mapping (no CPU fallback)
- INT8 quantization for optimal performance

Training Workflow:
1. Train on CPU/GPU (Raspberry Pi or Google Colab)
2. Convert to TFLite with INT8 quantization
3. Compile for Edge TPU on Google Colab (x86_64 required)
4. Deploy to Raspberry Pi for inference

Author: Sentient Core Project
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Tuple, List
import tensorflow as tf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CoralOptimizedTrainer:
    """
    Edge TPU-optimized trainer for particle visualization model.

    Design Principles:
    - Small architecture (<6MB) for full Edge TPU caching
    - Only supported operations (Dense, ReLU, Reshape)
    - No BatchNormalization (adds complexity)
    - No Dropout at inference
    - INT8 quantization with representative dataset
    """

    def __init__(self,
                 dataset_path: Path,
                 num_features: int = 68,
                 num_particles: int = 10000):
        """
        Initialize trainer.

        Args:
            dataset_path: Path to dataset directory containing .npy files
            num_features: Number of input features (68 for rich features)
            num_particles: Number of particles to generate (10,000)
        """
        self.dataset_path = Path(dataset_path)
        self.num_features = num_features
        self.num_particles = num_particles
        self.num_outputs = num_particles * 3  # x, y, z coordinates

        # Model paths
        self.models_dir = Path(__file__).parent / 'models'
        self.models_dir.mkdir(exist_ok=True)

        # Training configuration
        self.batch_size = 4  # Small batch for limited data
        self.epochs = 100  # More epochs for small dataset
        self.learning_rate = 0.001
        self.validation_split = 0.2

        # For quantization
        self.representative_data = None

    def find_latest_dataset(self) -> Tuple[Path, Path, Path]:
        """
        Find the most recent dataset files.

        Returns:
            Tuple of (inputs_path, outputs_path, metadata_path)
        """
        logger.info(f"Searching for dataset in {self.dataset_path}")

        # Find all input files (prefer companion dataset over rich dataset)
        companion_files = sorted(self.dataset_path.glob('inputs_companion_*.npy'))
        rich_files = sorted(self.dataset_path.glob('inputs_rich_*.npy'))

        if companion_files:
            input_files = companion_files
            logger.info("  Using Cortana-inspired companion dataset")
        else:
            input_files = rich_files
            logger.info("  Using original rich feature dataset")

        if not input_files:
            raise FileNotFoundError(f"No dataset files found in {self.dataset_path}")

        # Get latest
        latest_input = input_files[-1]
        timestamp = latest_input.stem.replace('inputs_companion_', '').replace('inputs_rich_', '')

        # Check for companion or rich dataset
        latest_output = self.dataset_path / f'outputs_companion_{timestamp}.npy'
        latest_metadata = self.dataset_path / f'metadata_companion_{timestamp}.json'

        if not latest_output.exists():
            latest_output = self.dataset_path / f'outputs_rich_{timestamp}.npy'
            latest_metadata = self.dataset_path / f'metadata_rich_{timestamp}.json'

        logger.info(f"Found dataset: {timestamp}")
        logger.info(f"  Inputs:  {latest_input}")
        logger.info(f"  Outputs: {latest_output}")
        logger.info(f"  Metadata: {latest_metadata}")

        return latest_input, latest_output, latest_metadata

    def load_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load training dataset from .npy files.

        Returns:
            Tuple of (inputs, outputs) as numpy arrays
        """
        inputs_path, outputs_path, metadata_path = self.find_latest_dataset()

        logger.info("Loading dataset...")

        # Load arrays
        inputs = np.load(inputs_path).astype(np.float32)
        outputs = np.load(outputs_path).astype(np.float32)

        logger.info(f"  Inputs shape:  {inputs.shape} (dtype: {inputs.dtype})")
        logger.info(f"  Outputs shape: {outputs.shape} (dtype: {outputs.dtype})")

        # Keep outputs in (num_examples, 10000, 3) shape to match model output
        num_examples = outputs.shape[0]

        # Verify shapes
        assert inputs.shape == (num_examples, self.num_features), \
            f"Expected inputs shape ({num_examples}, {self.num_features}), got {inputs.shape}"
        assert outputs.shape == (num_examples, self.num_particles, 3), \
            f"Expected outputs shape ({num_examples}, {self.num_particles}, 3), got {outputs.shape}"

        logger.info(f"✓ Loaded {num_examples} training examples")

        return inputs, outputs

    def build_model(self) -> tf.keras.Model:
        """
        Build Edge TPU-optimized neural network.

        Architecture Design:
        - Target model size: <6 MB for full Edge TPU caching
        - Only use supported operations: Dense, ReLU, Reshape
        - No BatchNormalization (adds complexity)
        - Small layer sizes to minimize parameters

        Three architecture options (uncomment to try):

        OPTION 1: Minimal (3.8MB) - Fastest, simplest
        68 → 128 → 30,000

        OPTION 2: Small (5-6MB) - Better learning capacity
        68 → 96 → 128 → 256 → 30,000

        OPTION 3: Medium (7-8MB) - Best accuracy (may exceed cache)
        68 → 128 → 256 → 512 → 30,000

        Returns:
            Compiled Keras model
        """
        logger.info("Building Edge TPU-optimized model...")

        # OPTION 1: Minimal architecture (~3.8MB) - RECOMMENDED
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.num_features,), name='input'),
            tf.keras.layers.Dense(128, activation='relu', name='dense1'),
            tf.keras.layers.Dense(self.num_outputs, name='output'),
            tf.keras.layers.Reshape((self.num_particles, 3), name='reshape_particles')
        ], name='sentient_core_viz')

        # OPTION 2: Small architecture (~5-6MB) - Uncomment to use
        # model = tf.keras.Sequential([
        #     tf.keras.layers.Input(shape=(self.num_features,), name='input'),
        #     tf.keras.layers.Dense(96, activation='relu', name='dense1'),
        #     tf.keras.layers.Dense(128, activation='relu', name='dense2'),
        #     tf.keras.layers.Dense(256, activation='relu', name='dense3'),
        #     tf.keras.layers.Dense(self.num_outputs, name='output'),
        #     tf.keras.layers.Reshape((self.num_particles, 3), name='reshape_particles')
        # ], name='sentient_core_viz')

        # OPTION 3: Medium architecture (~7-8MB) - May exceed cache
        # model = tf.keras.Sequential([
        #     tf.keras.layers.Input(shape=(self.num_features,), name='input'),
        #     tf.keras.layers.Dense(128, activation='relu', name='dense1'),
        #     tf.keras.layers.Dense(256, activation='relu', name='dense2'),
        #     tf.keras.layers.Dense(512, activation='relu', name='dense3'),
        #     tf.keras.layers.Dense(self.num_outputs, name='output'),
        #     tf.keras.layers.Reshape((self.num_particles, 3), name='reshape_particles')
        # ], name='sentient_core_viz')

        # Compile
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',  # Mean squared error for coordinate regression
            metrics=['mae']  # Mean absolute error
        )

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL ARCHITECTURE")
        logger.info("="*70)
        model.summary(print_fn=logger.info)
        logger.info("="*70 + "\n")

        # Calculate estimated model size
        total_params = model.count_params()
        estimated_size_mb = (total_params * 1) / (1024 * 1024)  # INT8 = 1 byte per param

        logger.info(f"Total parameters: {total_params:,}")
        logger.info(f"Estimated model size (INT8): {estimated_size_mb:.2f} MB")

        if estimated_size_mb > 6:
            logger.warning("⚠️  Model may exceed 6MB - might not fit in Edge TPU cache!")
            logger.warning("    Consider using smaller architecture (OPTION 1)")
        else:
            logger.info(f"✓ Model size {estimated_size_mb:.2f} MB < 6 MB target")

        return model

    def train(self, inputs: np.ndarray, outputs: np.ndarray) -> tf.keras.Model:
        """
        Train the model.

        Args:
            inputs: Input feature tensors (num_examples, 68)
            outputs: Target particle positions (num_examples, 30000)

        Returns:
            Trained model
        """
        logger.info("\n" + "="*70)
        logger.info("TRAINING")
        logger.info("="*70)

        model = self.build_model()

        # Callbacks
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                filepath=str(self.models_dir / f'best_model_{timestamp}.h5'),
                save_best_only=True,
                monitor='val_loss',
                verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,  # More patience for small dataset
                restore_best_weights=True,
                verbose=1
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=8,
                min_lr=0.00001,
                verbose=1
            )
        ]

        # Train
        logger.info(f"Training with {len(inputs)} examples...")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Epochs: {self.epochs}")
        logger.info(f"Validation split: {self.validation_split}")

        history = model.fit(
            inputs,
            outputs,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=2
        )

        logger.info("\n" + "="*70)
        logger.info("TRAINING COMPLETE")
        logger.info("="*70)
        logger.info(f"Best validation loss: {min(history.history['val_loss']):.6f}")
        logger.info(f"Final training loss: {history.history['loss'][-1]:.6f}")
        logger.info("="*70 + "\n")

        # Store for quantization
        self.representative_data = inputs

        return model

    def convert_to_tflite(self, model: tf.keras.Model) -> bytes:
        """
        Convert to TensorFlow Lite with full INT8 quantization.

        This follows Coral best practices:
        - INT8 quantization for all operations
        - Representative dataset for calibration
        - Target Edge TPU operation set

        Args:
            model: Trained Keras model

        Returns:
            Quantized TFLite model as bytes
        """
        logger.info("\n" + "="*70)
        logger.info("CONVERTING TO TENSORFLOW LITE")
        logger.info("="*70)

        # Create converter
        converter = tf.lite.TFLiteConverter.from_keras_model(model)

        # Representative dataset generator for quantization calibration
        def representative_dataset():
            """
            Provides sample inputs for quantization calibration.
            Uses actual training data for best results.
            """
            for i in range(min(100, len(self.representative_data))):
                yield [self.representative_data[i:i+1].astype(np.float32)]

        logger.info("Applying INT8 quantization...")
        logger.info("  Using representative dataset for calibration")

        # Configure quantization (Coral best practices)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = representative_dataset
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

        # Option 1: Float I/O (easier to use, slight latency penalty)
        converter.inference_input_type = tf.float32
        converter.inference_output_type = tf.float32

        # Option 2: INT8 I/O (best performance, requires scaling)
        # converter.inference_input_type = tf.int8
        # converter.inference_output_type = tf.int8

        # Convert
        logger.info("Converting model...")
        tflite_model = converter.convert()

        # Report size
        size_kb = len(tflite_model) / 1024
        size_mb = size_kb / 1024

        logger.info("="*70)
        logger.info(f"✓ TFLite model size: {size_kb:.2f} KB ({size_mb:.2f} MB)")

        if size_mb > 6:
            logger.warning("⚠️  Model exceeds 6MB Edge TPU cache limit!")
            logger.warning("    Performance may be degraded due to CPU fallback")
        else:
            logger.info(f"✓ Model fits in Edge TPU cache ({size_mb:.2f} MB < 6 MB)")

        logger.info("="*70 + "\n")

        return tflite_model

    def save_models(self, model: tf.keras.Model, tflite_model: bytes, timestamp: str):
        """
        Save all model formats.

        Args:
            model: Keras model
            tflite_model: TFLite model bytes
            timestamp: Timestamp string for filenames
        """
        logger.info("Saving models...")

        # Save Keras model
        keras_path = self.models_dir / f'sentient_viz_{timestamp}.h5'
        model.save(str(keras_path))
        logger.info(f"  ✓ Keras model: {keras_path}")

        # Save TFLite model
        tflite_path = self.models_dir / f'sentient_viz_{timestamp}.tflite'
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        logger.info(f"  ✓ TFLite model: {tflite_path}")

        # Create symlinks to latest
        latest_h5 = self.models_dir / 'latest.h5'
        latest_tflite = self.models_dir / 'latest.tflite'

        for link in [latest_h5, latest_tflite]:
            if link.exists() or link.is_symlink():
                link.unlink()

        latest_h5.symlink_to(keras_path.name)
        latest_tflite.symlink_to(tflite_path.name)

        logger.info(f"  ✓ Symlinks: latest.h5, latest.tflite")

        return tflite_path

    def print_next_steps(self, tflite_path: Path):
        """Print instructions for Edge TPU compilation."""
        logger.info("\n" + "="*70)
        logger.info("NEXT STEPS: COMPILE FOR EDGE TPU")
        logger.info("="*70)
        logger.info("")
        logger.info("The model is ready for Edge TPU compilation!")
        logger.info("")
        logger.info("⚠️  IMPORTANT: Edge TPU Compiler requires x86_64 (not ARM64)")
        logger.info("   You must compile on Google Colab or x86_64 Linux desktop")
        logger.info("")
        logger.info("=" * 70)
        logger.info("OPTION 1: Compile on Google Colab (Recommended)")
        logger.info("=" * 70)
        logger.info("")
        logger.info("1. Open: https://colab.research.google.com/")
        logger.info("2. Create new notebook")
        logger.info("3. Run these commands:")
        logger.info("")
        logger.info("   # Install Edge TPU Compiler")
        logger.info("   !curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -")
        logger.info("   !echo \"deb https://packages.cloud.google.com/apt coral-edgetpu-stable main\" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list")
        logger.info("   !sudo apt-get update")
        logger.info("   !sudo apt-get install -y edgetpu-compiler")
        logger.info("")
        logger.info("   # Upload your .tflite file when prompted")
        logger.info("   from google.colab import files")
        logger.info("   uploaded = files.upload()")
        logger.info("")
        logger.info("   # Compile for Edge TPU")
        logger.info(f"   !edgetpu_compiler {tflite_path.name}")
        logger.info("")
        logger.info("   # Download compiled model")
        logger.info(f"   files.download('{tflite_path.stem}_edgetpu.tflite')")
        logger.info("")
        logger.info("4. Transfer compiled model back to Raspberry Pi:")
        logger.info(f"   scp {tflite_path.stem}_edgetpu.tflite mz1312@<raspberry-pi-ip>:{self.models_dir}/")
        logger.info("")
        logger.info("=" * 70)
        logger.info("OPTION 2: Use Provided Colab Guide")
        logger.info("=" * 70)
        logger.info("")
        logger.info(f"   See: {Path(__file__).parent / 'COLAB_COMPILE.md'}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("VERIFY COMPILATION SUCCESS")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Look for these indicators in compiler output:")
        logger.info("  ✓ Number of Edge TPU subgraphs: 1")
        logger.info("  ✓ Operations mapped to Edge TPU: 100%")
        logger.info("  ✓ Off-chip memory used: 0.00B")
        logger.info("")
        logger.info("If you see multiple subgraphs or CPU operations:")
        logger.info("  ⚠️  Model has unsupported operations - some will run on CPU")
        logger.info("  ⚠️  Performance will be significantly degraded")
        logger.info("")
        logger.info("=" * 70)
        logger.info("TEST INFERENCE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("After compilation, test on Raspberry Pi:")
        logger.info("")
        logger.info("   python3 coral_training/test_coral_inference.py")
        logger.info("")
        logger.info("Expected performance: 2-5ms per inference (200+ FPS)")
        logger.info("")
        logger.info("=" * 70)


def main():
    """Main training workflow."""

    logger.info("\n")
    logger.info("=" * 70)
    logger.info(" SENTIENT CORE - EDGE TPU OPTIMIZED TRAINING")
    logger.info("=" * 70)
    logger.info("  Project: AI Particle Visualization System")
    logger.info("  Target: Coral Edge TPU (USB Accelerator)")
    logger.info("  Goal: 60+ FPS real-time particle generation")
    logger.info("=" * 70)
    logger.info("\n")

    # Configuration
    dataset_path = Path(__file__).parent / 'dataset'

    # Create trainer
    trainer = CoralOptimizedTrainer(
        dataset_path=dataset_path,
        num_features=68,
        num_particles=10000
    )

    try:
        # Load dataset
        inputs, outputs = trainer.load_dataset()

        # Train model
        model = trainer.train(inputs, outputs)

        # Convert to TFLite
        tflite_model = trainer.convert_to_tflite(model)

        # Save everything
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tflite_path = trainer.save_models(model, tflite_model, timestamp)

        # Print next steps
        trainer.print_next_steps(tflite_path)

        logger.info("\n✓ Training pipeline complete!\n")
        return 0

    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
