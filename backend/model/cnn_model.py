"""
CNN Model Architecture
Crop Disease Detection System

Architecture: Custom CNN + Transfer Learning option (MobileNetV2 / ResNet50)
Dataset: PlantVillage (38 classes)
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from config import Config


def build_custom_cnn(num_classes: int = 38,
                     input_shape: tuple = (224, 224, 3),
                     dropout_rate: float = 0.5) -> keras.Model:
    """
    Custom CNN architecture for crop disease classification.

    Architecture:
        Input → Conv Block × 4 → GlobalAvgPool → Dense → Dropout → Output

    Args:
        num_classes:   Number of disease classes (38 for PlantVillage).
        input_shape:   Image dimensions (H, W, C).
        dropout_rate:  Dropout probability before final dense layer.

    Returns:
        Compiled Keras Model.
    """
    inputs = keras.Input(shape=input_shape, name='leaf_image')

    # ── Block 1 ──────────────────────────────────────────────────────────────
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu',
                      name='conv1_1')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu',
                      name='conv1_2')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # ── Block 2 ──────────────────────────────────────────────────────────────
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu',
                      name='conv2_1')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu',
                      name='conv2_2')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # ── Block 3 ──────────────────────────────────────────────────────────────
    x = layers.Conv2D(128, (3, 3), padding='same', activation='relu',
                      name='conv3_1')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(128, (3, 3), padding='same', activation='relu',
                      name='conv3_2')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # ── Block 4 ──────────────────────────────────────────────────────────────
    x = layers.Conv2D(256, (3, 3), padding='same', activation='relu',
                      name='conv4_1')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(256, (3, 3), padding='same', activation='relu',
                      name='conv4_2')(x)
    x = layers.GlobalAveragePooling2D()(x)

    # ── Classifier Head ───────────────────────────────────────────────────────
    x = layers.Dense(512, activation='relu', name='fc1')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(256, activation='relu', name='fc2')(x)
    x = layers.Dropout(dropout_rate * 0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax', name='predictions')(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name='CropDiseaseCNN')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy',
                 keras.metrics.TopKCategoricalAccuracy(k=3, name='top3_accuracy')]
    )

    return model


def build_mobilenet_model(num_classes: int = 38,
                          input_shape: tuple = (224, 224, 3),
                          fine_tune_at: int = 100) -> keras.Model:
    """
    Transfer learning model using MobileNetV2 (ImageNet pretrained).
    Recommended for production — higher accuracy with fewer training images.

    Args:
        num_classes:   Number of disease classes.
        input_shape:   Input image shape.
        fine_tune_at:  Layer index from which to unfreeze for fine-tuning.

    Returns:
        Compiled Keras Model.
    """
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    # Freeze base initially for feature extraction
    base_model.trainable = False

    inputs = keras.Input(shape=input_shape)
    x = keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = keras.Model(inputs, outputs, name='CropDisease_MobileNetV2')
    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy',
                 keras.metrics.TopKCategoricalAccuracy(k=3, name='top3_accuracy')]
    )

    return model, base_model


def get_callbacks(checkpoint_path: str, patience: int = 5):
    """Training callbacks: checkpoint, early stopping, learning rate reduction."""
    return [
        keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_path,
            save_best_only=True,
            monitor='val_accuracy',
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        keras.callbacks.TensorBoard(
            log_dir='./logs',
            histogram_freq=1
        )
    ]


def load_model(model_path: str = None) -> keras.Model:
    """Load a saved model from disk."""
    path = model_path or Config.MODEL_PATH
    return keras.models.load_model(path)
