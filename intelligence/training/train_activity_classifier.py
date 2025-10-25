#!/usr/bin/env python3
"""
Activity Classification Model Trainer

Trains a multi-class classifier to recognize user activities from 120-dimensional sensor features.
Optimized for Google Coral Edge TPU deployment.

Input: 120 features (Flipper Zero, WiFi, Bluetooth, Computer Vision, etc.)
Output: Activity classification (working, relaxing, moving, absent)
"""

import tensorflow as tf
import numpy as np
import os
from datetime import datetime
from pathlib import Path

# Activity classes
ACTIVITIES = ['working', 'relaxing', 'moving', 'absent']
NUM_CLASSES = len(ACTIVITIES)


class ActivityClassificationModel:
    """Multi-class classifier for activity recognition."""

    def __init__(self, input_features=120, num_classes=NUM_CLASSES):
        self.input_features = input_features
        self.num_classes = num_classes
        self.model = None

    def build_model(self):
        """
        Build optimized neural network for activity classification.

        Architecture designed for Edge TPU efficiency:
        - Compact for fast inference
        - ReLU activations (TPU optimized)
        - Softmax output for multi-class
        """
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=(self.input_features,), name='feature_input'),

            # Hidden layers
            tf.keras.layers.Dense(128, activation='relu', name='dense1'),
            tf.keras.layers.Dropout(0.4, name='dropout1'),

            tf.keras.layers.Dense(64, activation='relu', name='dense2'),
            tf.keras.layers.Dropout(0.3, name='dropout2'),

            tf.keras.layers.Dense(32, activation='relu', name='dense3'),
            tf.keras.layers.Dropout(0.2, name='dropout3'),

            # Output layer - 4 classes
            tf.keras.layers.Dense(self.num_classes, activation='softmax', name='activity_output')
        ], name='activity_classifier')

        # Compile with categorical cross-entropy for multi-class
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=2, name='top2_accuracy')]
        )

        self.model = model
        return model

    def generate_synthetic_data(self, num_samples=10000):
        """
        Generate synthetic training data for initial testing.

        Activities:
        0: working - high keyboard/mouse activity, stationary, screen active
        1: relaxing - low activity, stationary, media consumption
        2: moving - motion detected, variable signals
        3: absent - minimal activity across all sensors
        """
        X = np.zeros((num_samples, self.input_features), dtype=np.float32)
        y = np.zeros((num_samples, self.num_classes), dtype=np.float32)

        samples_per_class = num_samples // self.num_classes

        for i in range(num_samples):
            activity_idx = i // samples_per_class
            if activity_idx >= self.num_classes:
                activity_idx = self.num_classes - 1

            if activity_idx == 0:  # working
                # High keyboard/mouse signals (features 40-59: motion/input)
                X[i, 40:60] = np.random.uniform(0.6, 1.0, 20)
                # Strong WiFi (active connection)
                X[i, 0:20] = np.random.uniform(0.7, 1.0, 20)
                # Bluetooth devices (headphones, mouse)
                X[i, 20:40] = np.random.uniform(0.5, 0.9, 20)
                # Computer vision: seated at desk
                X[i, 60:80] = np.random.uniform(0.6, 0.9, 20)
                # Thermal: person present
                X[i, 80:100] = np.random.uniform(0.5, 0.8, 20)
                # Low Sub-GHz
                X[i, 100:120] = np.random.uniform(0.0, 0.3, 20)

            elif activity_idx == 1:  # relaxing
                # Low input activity
                X[i, 40:60] = np.random.uniform(0.0, 0.4, 20)
                # WiFi present (streaming)
                X[i, 0:20] = np.random.uniform(0.5, 0.8, 20)
                # Bluetooth (headphones)
                X[i, 20:40] = np.random.uniform(0.3, 0.7, 20)
                # Vision: person seated/reclining
                X[i, 60:80] = np.random.uniform(0.4, 0.7, 20)
                # Thermal: person present
                X[i, 80:100] = np.random.uniform(0.4, 0.7, 20)
                # Low Sub-GHz
                X[i, 100:120] = np.random.uniform(0.0, 0.2, 20)

            elif activity_idx == 2:  # moving
                # High motion
                X[i, 40:60] = np.random.uniform(0.7, 1.0, 20)
                # Variable WiFi (changing location)
                X[i, 0:20] = np.random.uniform(0.3, 0.8, 20)
                # Bluetooth variable
                X[i, 20:40] = np.random.uniform(0.2, 0.6, 20)
                # Vision: person in frame, moving
                X[i, 60:80] = np.random.uniform(0.5, 0.9, 20)
                # Thermal: changing
                X[i, 80:100] = np.random.uniform(0.4, 0.8, 20)
                # Some Sub-GHz activity
                X[i, 100:120] = np.random.uniform(0.0, 0.5, 20)

            else:  # absent (3)
                # All low signals
                X[i, :] = np.random.uniform(0.0, 0.3, self.input_features)

            # One-hot encode label
            y[i, activity_idx] = 1.0

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
        print("Training Activity Classification Model")
        print(f"{'='*60}")
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Classes: {ACTIVITIES}")
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

        loss, accuracy, top2_accuracy = self.model.evaluate(X_test, y_test, verbose=0)

        print(f"Test Loss: {loss:.4f}")
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"Top-2 Accuracy: {top2_accuracy:.4f}\n")

        # Per-class accuracy
        y_pred = self.model.predict(X_test, verbose=0)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)

        print("Per-Class Accuracy:")
        for i, activity in enumerate(ACTIVITIES):
            mask = y_true_classes == i
            if mask.sum() > 0:
                class_acc = (y_pred_classes[mask] == i).mean()
                print(f"  {activity}: {class_acc*100:.1f}%")

        print()

        return {
            'loss': loss,
            'accuracy': accuracy,
            'top2_accuracy': top2_accuracy
        }

    def convert_to_tflite(self, output_path, representative_dataset=None):
        """Convert model to TensorFlow Lite format with Edge TPU optimization."""
        print(f"\n{'='*60}")
        print("Converting to TensorFlow Lite")
        print(f"{'='*60}\n")

        # Create TFLite converter
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)

        # Edge TPU requires full integer quantization with float I/O
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        if representative_dataset is not None:
            converter.representative_dataset = representative_dataset
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
        """Compile TFLite model for Edge TPU using edgetpu_compiler."""
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
    """Train and deploy activity classification model."""

    print("\n" + "="*60)
    print("ACTIVITY CLASSIFICATION MODEL TRAINER")
    print("="*60 + "\n")

    # Create output directory
    output_dir = Path("intelligence/models")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize model
    model = ActivityClassificationModel(input_features=120, num_classes=NUM_CLASSES)

    # Generate synthetic training data
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
    tflite_path = output_dir / f"activity_classifier_{timestamp}.tflite"

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

    print(f"\nModel Performance:")
    print(f"  Accuracy: {metrics['accuracy']*100:.1f}%")
    print(f"  Top-2 Accuracy: {metrics['top2_accuracy']*100:.1f}%")
    print(f"\nActivity Classes: {', '.join(ACTIVITIES)}")
    print()


if __name__ == "__main__":
    main()
