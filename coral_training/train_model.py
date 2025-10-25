#!/usr/bin/env python3
"""
Coral TPU Model Training Script

Trains a TensorFlow Lite model to generate particle visualizations
from rich cognitive and sensory inputs. The model learns from LLM-generated examples.

Input: Rich Features (68 dimensions covering cognitive state, sensors, RF, vision, audio, etc.)
Output: Particle positions (10,000 particles × 3D coordinates) = 30,000 values
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import tensorflow as tf
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualizationModelTrainer:
    """Train TensorFlow Lite model for Coral TPU particle generation."""

    def __init__(self, dataset_path: str, num_particles: int = 10000):
        """
        Initialize trainer.

        Args:
            dataset_path: Path to training dataset JSON
            num_particles: Number of particles (must match dataset)
        """
        self.dataset_path = Path(dataset_path)
        self.num_particles = num_particles

        # Model paths
        self.models_dir = Path(__file__).parent / 'models'
        self.models_dir.mkdir(exist_ok=True)

        # Training config
        self.input_shape = (68,)  # 68 rich features (cognitive + sensory)
        self.output_shape = (num_particles, 3)  # N particles × (x, y, z)

        # Hyperparameters
        self.batch_size = 8
        self.epochs = 50
        self.learning_rate = 0.001
        self.validation_split = 0.2

    def load_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load training dataset from JSON.

        Returns:
            Tuple of (inputs, outputs) as numpy arrays
        """
        logger.info(f"Loading dataset from {self.dataset_path}")

        with open(self.dataset_path, 'r') as f:
            dataset = json.load(f)

        num_examples = len(dataset)
        logger.info(f"Loaded {num_examples} training examples")

        # Initialize arrays
        inputs = np.zeros((num_examples, self.input_shape[0]), dtype=np.float32)
        outputs = np.zeros((num_examples, *self.output_shape), dtype=np.float32)

        # Load data
        for i, example in enumerate(dataset):
            inputs[i] = np.array(example['input_tensor']).flatten()
            outputs[i] = np.array(example['particle_positions'])

        logger.info(f"Input shape: {inputs.shape}")
        logger.info(f"Output shape: {outputs.shape}")

        return inputs, outputs

    def build_model(self) -> tf.keras.Model:
        """
        Build neural network for particle generation.

        Architecture:
        - Input: State + sensors (9 features)
        - Dense layers with ReLU activation
        - Output: Particle positions (30,000 values)

        Returns:
            Compiled Keras model
        """
        logger.info("Building model architecture...")

        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=self.input_shape),

            # Dense layers for feature extraction
            tf.keras.layers.Dense(256, activation='relu', name='dense1'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),

            tf.keras.layers.Dense(512, activation='relu', name='dense2'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),

            tf.keras.layers.Dense(1024, activation='relu', name='dense3'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),

            tf.keras.layers.Dense(2048, activation='relu', name='dense4'),
            tf.keras.layers.BatchNormalization(),

            # Output layer - particle positions
            tf.keras.layers.Dense(self.num_particles * 3, name='output'),

            # Reshape to (num_particles, 3)
            tf.keras.layers.Reshape(self.output_shape, name='reshape_particles')
        ])

        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',  # Mean squared error for coordinate prediction
            metrics=['mae']  # Mean absolute error for monitoring
        )

        logger.info("Model architecture:")
        model.summary(print_fn=logger.info)

        return model

    def train(self, inputs: np.ndarray, outputs: np.ndarray) -> tf.keras.Model:
        """
        Train the model.

        Args:
            inputs: Input tensors (state + sensors)
            outputs: Target particle positions

        Returns:
            Trained model
        """
        logger.info("Starting training...")

        # Build model
        model = self.build_model()

        # Callbacks
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_path = self.models_dir / f'checkpoint_{timestamp}.h5'

        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                filepath=str(checkpoint_path),
                save_best_only=True,
                monitor='val_loss',
                verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            )
        ]

        # Train
        history = model.fit(
            inputs,
            outputs,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=1
        )

        logger.info("Training complete!")
        logger.info(f"Best validation loss: {min(history.history['val_loss']):.6f}")

        return model

    def convert_to_tflite(self, model: tf.keras.Model, quantize: bool = True) -> bytes:
        """
        Convert Keras model to TensorFlow Lite format.

        Args:
            model: Trained Keras model
            quantize: Whether to apply quantization for Coral TPU

        Returns:
            TFLite model as bytes
        """
        logger.info("Converting to TensorFlow Lite...")

        # Create converter
        converter = tf.lite.TFLiteConverter.from_keras_model(model)

        if quantize:
            logger.info("Applying quantization for Coral TPU...")

            # Enable quantization
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS_INT8
            ]
            converter.inference_input_type = tf.float32
            converter.inference_output_type = tf.float32

        # Convert
        tflite_model = converter.convert()

        logger.info(f"TFLite model size: {len(tflite_model) / 1024:.2f} KB")

        return tflite_model

    def compile_for_edgetpu(self, tflite_model_path: str) -> str:
        """
        Compile TFLite model for Edge TPU using edgetpu_compiler.

        Args:
            tflite_model_path: Path to TFLite model

        Returns:
            Path to compiled Edge TPU model

        IMPORTANT - ARM64 Limitation (Raspberry Pi):
            Edge TPU compiler is NOT available for ARM64 systems as of version 2.1.
            Google has abandoned Coral project (no updates since 2021).

            Recommended compilation methods:
            1. Google Colab (free, web-based) - See coral_training/COLAB_COMPILE.md
            2. x86_64 Linux desktop
            3. Ultralytics Docker container

            This method will attempt local compilation but will gracefully fail
            on ARM64 systems. Compile the .tflite model on another system, then
            transfer the _edgetpu.tflite file back to this directory.

            For local inference only (no compilation needed):
            sudo apt-get install python3-edgetpu libedgetpu1-std
        """
        logger.info("Compiling for Edge TPU...")

        import subprocess

        output_dir = os.path.dirname(tflite_model_path)

        cmd = [
            'edgetpu_compiler',
            tflite_model_path,
            '-o', output_dir
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(result.stdout)

            # Edge TPU compiler appends "_edgetpu.tflite" to the filename
            base_name = os.path.splitext(os.path.basename(tflite_model_path))[0]
            edgetpu_model_path = os.path.join(output_dir, f"{base_name}_edgetpu.tflite")

            logger.info(f"Edge TPU model saved to: {edgetpu_model_path}")
            return edgetpu_model_path

        except subprocess.CalledProcessError as e:
            logger.error(f"Edge TPU compilation failed: {e.stderr}")
            logger.warning("Falling back to standard TFLite model (will run on CPU)")
            return tflite_model_path

    def save_models(self, model: tf.keras.Model, tflite_model: bytes):
        """
        Save trained models to disk.

        Args:
            model: Keras model
            tflite_model: TFLite model bytes
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save Keras model
        keras_path = self.models_dir / f'visualization_model_{timestamp}.h5'
        model.save(str(keras_path))
        logger.info(f"Keras model saved to: {keras_path}")

        # Save TFLite model
        tflite_path = self.models_dir / f'visualization_model_{timestamp}.tflite'
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        logger.info(f"TFLite model saved to: {tflite_path}")

        # Try to compile for Edge TPU
        try:
            edgetpu_path = self.compile_for_edgetpu(str(tflite_path))
            logger.info(f"Edge TPU model: {edgetpu_path}")
        except Exception as e:
            logger.warning(f"Could not compile for Edge TPU: {e}")
            logger.info("You can compile manually with: edgetpu_compiler {tflite_path}")

        # Save latest symlink
        latest_keras = self.models_dir / 'latest.h5'
        latest_tflite = self.models_dir / 'latest.tflite'

        if latest_keras.exists():
            latest_keras.unlink()
        if latest_tflite.exists():
            latest_tflite.unlink()

        latest_keras.symlink_to(keras_path.name)
        latest_tflite.symlink_to(tflite_path.name)

        logger.info("Symlinks created: latest.h5, latest.tflite")


def main():
    """Train visualization model."""
    logger.info("=" * 70)
    logger.info("Coral TPU Visualization Model Training")
    logger.info("=" * 70)

    # Dataset path
    dataset_path = Path(__file__).parent / 'datasets' / 'training_dataset.json'

    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.error("Run generate_dataset.py first to create training data")
        return 1

    # Create trainer
    trainer = VisualizationModelTrainer(
        dataset_path=str(dataset_path),
        num_particles=10000
    )

    # Load dataset
    inputs, outputs = trainer.load_dataset()

    # Train model
    model = trainer.train(inputs, outputs)

    # Convert to TFLite
    tflite_model = trainer.convert_to_tflite(model, quantize=True)

    # Save models
    trainer.save_models(model, tflite_model)

    logger.info("=" * 70)
    logger.info("Training complete!")
    logger.info("=" * 70)
    logger.info("Next steps:")
    logger.info("1. Test model: python3 coral_training/test_inference.py")
    logger.info("2. Deploy to daemon: python3 coral_daemon.py")
    logger.info("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
