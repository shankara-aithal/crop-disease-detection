"""
Image Preprocessing Module
Crop Disease Detection System

Handles: resize, normalize, augment, validate uploads.
"""

import os
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import tensorflow as tf
from config import Config


# ── Constants ─────────────────────────────────────────────────────────────────
IMG_SIZE   = Config.IMAGE_SIZE           # (224, 224)
MEAN       = np.array([0.485, 0.456, 0.406])   # ImageNet mean (RGB)
STD        = np.array([0.229, 0.224, 0.225])   # ImageNet std


def allowed_file(filename: str) -> bool:
    """Return True if filename has an allowed image extension."""
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def load_and_preprocess(image_path: str,
                        normalize: bool = True) -> np.ndarray:
    """
    Load an image from disk and preprocess it for model input.

    Steps:
        1. Open with PIL and convert to RGB.
        2. Resize to IMG_SIZE using LANCZOS resampling.
        3. Convert to float32 numpy array in [0, 1].
        4. Apply ImageNet mean/std normalisation (optional).
        5. Add batch dimension → shape (1, H, W, 3).

    Args:
        image_path: Absolute path to the image file.
        normalize:  Apply ImageNet normalisation if True.

    Returns:
        Numpy array of shape (1, 224, 224, 3).
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMG_SIZE, Image.LANCZOS)

    arr = np.array(img, dtype=np.float32) / 255.0

    if normalize:
        arr = (arr - MEAN) / STD

    return np.expand_dims(arr, axis=0)    # (1, 224, 224, 3)


def preprocess_from_bytes(image_bytes: bytes,
                          normalize: bool = True) -> np.ndarray:
    """Preprocess from raw bytes (e.g., request.files stream)."""
    from io import BytesIO
    img = Image.open(BytesIO(image_bytes)).convert('RGB')
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    if normalize:
        arr = (arr - MEAN) / STD
    return np.expand_dims(arr, axis=0)


def validate_leaf_image(image_path: str) -> tuple[bool, str]:
    """
    Basic validation that the uploaded image looks like a leaf photo.
    Checks: file exists, can be opened, minimum resolution.

    Returns:
        (is_valid: bool, message: str)
    """
    if not os.path.exists(image_path):
        return False, "File not found."

    try:
        img = Image.open(image_path)
        img.verify()                  # checks file integrity
    except Exception as e:
        return False, f"Corrupt image: {e}"

    img = Image.open(image_path)      # re-open after verify()
    w, h = img.size
    if w < 32 or h < 32:
        return False, f"Image too small ({w}×{h}). Minimum 32×32 required."

    return True, "OK"


# ── Data Augmentation (used during training) ───────────────────────────────────
def get_augmentation_layer():
    """
    Keras sequential augmentation pipeline for training data.
    Applied on-the-fly on GPU during model.fit().
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.15),
        tf.keras.layers.RandomContrast(0.1),
        tf.keras.layers.RandomBrightness(0.1),
    ], name="augmentation")


def build_tf_dataset(data_dir: str,
                     batch_size: int = 32,
                     augment: bool = True,
                     validation_split: float = 0.2,
                     seed: int = 42):
    """
    Build TensorFlow datasets from a directory structured as:

        data_dir/
            ClassName1/
                img001.jpg
                ...
            ClassName2/
                ...

    Args:
        data_dir:         Path to the PlantVillage dataset directory.
        batch_size:       Number of images per batch.
        augment:          Apply augmentation to training set.
        validation_split: Fraction of data to use for validation.
        seed:             Random seed for reproducibility.

    Returns:
        (train_ds, val_ds, class_names)
    """
    img_height, img_width = IMG_SIZE

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=validation_split,
        subset='training',
        seed=seed,
        image_size=(img_height, img_width),
        batch_size=batch_size,
        label_mode='categorical',
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=validation_split,
        subset='validation',
        seed=seed,
        image_size=(img_height, img_width),
        batch_size=batch_size,
        label_mode='categorical',
    )

    class_names = train_ds.class_names

    # Normalise pixel values to [0, 1]
    normalization_layer = tf.keras.layers.Rescaling(1. / 255)

    if augment:
        aug_layer = get_augmentation_layer()
        train_ds = train_ds.map(
            lambda x, y: (aug_layer(normalization_layer(x), training=True), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )
    else:
        train_ds = train_ds.map(
            lambda x, y: (normalization_layer(x), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )

    val_ds = val_ds.map(
        lambda x, y: (normalization_layer(x), y),
        num_parallel_calls=tf.data.AUTOTUNE
    )

    # Cache and prefetch for performance
    train_ds = train_ds.cache().shuffle(1000).prefetch(tf.data.AUTOTUNE)
    val_ds   = val_ds.cache().prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, class_names
