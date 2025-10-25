#!/usr/bin/env python3
"""
Presence Detection Model Trainer

Trains a binary classifier to detect human presence from 120-dimensional sensor features.
Optimized for Google Coral Edge TPU deployment.

Input: 120 features (Flipper Zero, WiFi, Bluetooth, Computer Vision, etc.)
Output: Binary classification (present=1, absent=0)
"""

import tensorflow as tf
import numpy as np
import os
from datetime import datetime
from pathlib import Path

# Coral TPU quantization requirements
QUANTIZATION_TYPE = tf.float32  # Input/output must be float32 for Edge TPU


class PresenceDetectionModel:
    """Binary classifier for human presence detection."""

    def __init__(self, input_features=120):
        self.input_features = input_features
        self.model = None

    def build_model(self):
        """
        Build optimized neural network for presence detection.

        Architecture designed for Edge TPU efficiency:
        - Small model (fast inference)
        - ReLU activations (TPU optimized)
        - Dense layers only (fully connected)
        """
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=(self.input_features,), name='feature_input'),

            # Hidden layers - compact for fast Edge TPU inference
            tf.keras.layers.Dense(64, activation='relu', name='dense1'),
            tf.keras.layers.Dropout(0.3, name='dropout1'),

            tf.keras.layers.Dense(32, activation='relu', name='dense2'),
            tf.keras.layers.Dropout(0.2, name='dropout2'),

            tf.keras.layers.Dense(16, activation='relu', name='dense3'),

            # Output layer - single neuron for binary classification
            tf.keras.layers.Dense(1, activation='sigmoid', name='presence_output')
        ], name='presence_detector')

        # Compile with binary cross-entropy for binary classification
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )

        self.model = model
        return model

    def generate_synthetic_data(self, num_samples=10000):
        """
        Generate synthetic training data for initial testing.

        In production, replace with real collected sensor data.

        Presence indicators (features with higher values when present):
        - WiFi signal strength (features 0-19)
        - Bluetooth devices (features 20-39)
        - Motion sensors (features 40-59)
        - Computer vision (features 60-79)
        - IR/thermal (features 80-99)
        - Sub-GHz activity (features 100-119)
        """
        X = np.zeros((num_samples, self.input_features), dtype=np.float32)
        y = np.zeros((num_samples, 1), dtype=np.float32)

        # Half samples: person present
        present_samples = num_samples // 2

        for i in range(present_samples):
            # Simulate presence: higher values in relevant features
            # WiFi signals stronger
            X[i, 0:20] = np.random.uniform(0.5, 1.0, 20)
            # Bluetooth devices detected
            X[i, 20:40] = np.random.uniform(0.4, 1.0, 20)
            # Motion detected
            X[i, 40:60] = np.random.uniform(0.6, 1.0, 20)
            # Vision sees person
            X[i, 60:80] = np.random.uniform(0.5, 1.0, 20)
            # IR/thermal signature
            X[i, 80:100] = np.random.uniform(0.5, 0.9, 20)
            # Some Sub-GHz activity
            X[i, 100:120] = np.random.uniform(0.0, 0.4, 20)

            y[i] = 1.0  # Present

        # Half samples: no person present
        for i in range(present_samples, num_samples):
            # Simulate absence: lower values in relevant features
            # Weaker WiFi
            X[i, 0:20] = np.random.uniform(0.0, 0.3, 20)
            # No personal Bluetooth devices
            X[i, 20:40] = np.random.uniform(0.0, 0.2, 20)
            # No motion
            X[i, 40:60] = np.random.uniform(0.0, 0.2, 20)
            # No person in vision
            X[i, 60:80] = np.random.uniform(0.0, 0.3, 20)
            # No thermal signature
            X[i, 80:100] = np.random.uniform(0.0, 0.2, 20)
            # Minimal Sub-GHz
            X[i, 100:120] = np.random.uniform(0.0, 0.2, 20)

            y[i] = 0.0  # Absent

        # Shuffle data
        indices = np.arange(num_samples)
        np.random.shuffle(indices)
        X = X[indices]
        y = y[indices]

        return X, y

    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """Train the model."""
        if self.model is None:
            self.build_model()

        print(f"\n{'='*60}")
        print("Training Presence Detection Model")
        print(f"{'='*60}")
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}\n")

        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001
            )
        ]

        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )

        return history

    def evaluate(self, X_test, y_test):
        """Evaluate model performance."""
        print(f"\n{'='*60}")
        print("Evaluating Model")
        print(f"{'='*60}\n")

        loss, accuracy, precision, recall = self.model.evaluate(X_test, y_test, verbose=0)

        print(f"Test Loss: {loss:.4f}")
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"Test Precision: {precision:.4f}")
        print(f"Test Recall: {recall:.4f}")
        print(f"F1 Score: {2 * (precision * recall) / (precision + recall):.4f}\n")

        return {
            'loss': loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall
        }

    def convert_to_tflite(self, output_path, representative_dataset=None):
        """
        Convert model to TensorFlow Lite format with Edge TPU optimization.

        Args:
            output_path: Path to save .tflite file
            representative_dataset: Generator function for quantization
        """
        print(f"\n{'='*60}")
        print("Converting to TensorFlow Lite")
        print(f"{'='*60}\n")

        # Create TFLite converter
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)

        # Edge TPU requires full integer quantization with float I/O
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        if representative_dataset is not None:
            converter.representative_dataset = representative_dataset
            # Ensure float32 input/output for Edge TPU compatibility
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS_INT8
            ]
            converter.inference_input_type = tf.float32
            converter.inference_output_type = tf.float32

        # Convert
        print("Converting model...")
        tflite_model = converter.convert()

        # Save
        with open(output_path, 'wb') as f:
            f.write(tflite_model)

        size_kb = len(tflite_model) / 1024
        print(f"✓ TFLite model saved: {output_path}")
        print(f"✓ Model size: {size_kb:.1f} KB\n")

        return tflite_model

    def compile_for_edgetpu(self, tflite_path, output_dir):
        """
        Compile TFLite model for Edge TPU using edgetpu_compiler.

        Args:
            tflite_path: Path to .tflite model
            output_dir: Directory to save compiled model
        """
        print(f"\n{'='*60}")
        print("Compiling for Edge TPU")
        print(f"{'='*60}\n")

        import subprocess

        # Check if edgetpu_compiler is available
        try:
            result = subprocess.run(
                ['edgetpu_compiler', '--version'],
                capture_output=True,
                text=True
            )
            print(f"Edge TPU Compiler version: {result.stdout.strip()}\n")
        except FileNotFoundError:
            print("ERROR: edgetpu_compiler not found!")
            print("Install with: sudo apt-get install edgetpu-compiler")
            print("Or download from: https://coral.ai/docs/edgetpu/compiler/")
            return None

        # Compile model
        print(f"Compiling {tflite_path}...")
        result = subprocess.run(
            ['edgetpu_compiler', '-s', '-o', output_dir, tflite_path],
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        # Check for compiled model
        compiled_path = Path(output_dir) / f"{Path(tflite_path).stem}_edgetpu.tflite"
        if compiled_path.exists():
            print(f"\n✓ Edge TPU model compiled: {compiled_path}\n")
            return str(compiled_path)
        else:
            print("\n✗ Edge TPU compilation failed\n")
            return None


def main():
    """Train and deploy presence detection model."""

    print("\n" + "="*60)
    print("PRESENCE DETECTION MODEL TRAINER")
    print("="*60 + "\n")

    # Create output directory
    output_dir = Path("intelligence/models")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize model
    model = PresenceDetectionModel(input_features=120)

    # Generate synthetic training data
    # TODO: Replace with real collected sensor data
    print("Generating synthetic training data...")
    X, y = model.generate_synthetic_data(num_samples=10000)

    # Split into train/val/test
    train_size = int(0.7 * len(X))
    val_size = int(0.15 * len(X))

    X_train = X[:train_size]
    y_train = y[:train_size]

    X_val = X[train_size:train_size+val_size]
    y_val = y[train_size:train_size+val_size]

    X_test = X[train_size+val_size:]
    y_test = y[train_size+val_size:]

    print(f"✓ Generated {len(X)} samples")
    print(f"  Train: {len(X_train)}")
    print(f"  Validation: {len(X_val)}")
    print(f"  Test: {len(X_test)}\n")

    # Build and train model
    model.build_model()
    model.model.summary()

    history = model.train(X_train, y_train, X_val, y_val, epochs=50, batch_size=32)

    # Evaluate
    metrics = model.evaluate(X_test, y_test)

    # Convert to TFLite
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tflite_path = output_dir / f"presence_detector_{timestamp}.tflite"

    # Create representative dataset for quantization
    def representative_dataset():
        for i in range(100):
            yield [X_train[i:i+1].astype(np.float32)]

    model.convert_to_tflite(tflite_path, representative_dataset=representative_dataset)

    # Compile for Edge TPU
    edgetpu_path = model.compile_for_edgetpu(str(tflite_path), str(output_dir))

    # Summary
    print("="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"\n✓ Standard TFLite model: {tflite_path}")
    if edgetpu_path:
        print(f"✓ Edge TPU compiled model: {edgetpu_path}")
        print(f"\nReady for deployment on Coral TPU!")
    else:
        print(f"\n⚠ Edge TPU compilation skipped (compiler not available)")
        print(f"Standard TFLite model can still run on CPU")

    print(f"\nModel Performance:")
    print(f"  Accuracy: {metrics['accuracy']*100:.1f}%")
    print(f"  Precision: {metrics['precision']*100:.1f}%")
    print(f"  Recall: {metrics['recall']*100:.1f}%")
    print()


if __name__ == "__main__":
    main()
