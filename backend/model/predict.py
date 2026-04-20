"""
Prediction Engine
Crop Disease Detection System

Loads the trained CNN model and runs inference on leaf images.
Returns disease name, confidence score, top-3 predictions, and recommendation.
"""

import os
import json
import time
import numpy as np
from typing import Optional

from config import Config

# Lazy-load model (avoids slow import at startup)
_model = None
_class_names = None


def _get_model():
    """Load and cache the Keras model and class names."""
    global _model, _class_names

    if _model is not None:
        return _model, _class_names

    model_path = Config.MODEL_PATH
    class_path = os.path.join(
        os.path.dirname(model_path), 'class_names.json'
    )

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Trained model not found at '{model_path}'.\n"
            "Run 'python model/train.py' first to train the model."
        )

    import tensorflow as tf
    _model = tf.keras.models.load_model(model_path)

    if os.path.exists(class_path):
        with open(class_path) as f:
            mapping = json.load(f)
        _class_names = [mapping[str(i)] for i in range(len(mapping))]
    else:
        # Fall back to config list
        _class_names = Config.DISEASE_CLASSES

    print(f"[INFO] Model loaded: {model_path}")
    print(f"[INFO] Classes: {len(_class_names)}")
    return _model, _class_names


def predict(image_path: str) -> dict:
    """
    Run disease prediction on a leaf image.

    Args:
        image_path: Absolute path to the preprocessed image file.

    Returns:
        dict with keys:
            disease_name   – str
            crop_type      – str
            is_healthy     – bool
            confidence     – float  (0-1)
            top3           – list[dict]  each: {label, confidence}
            recommendation – str
            processing_time– float (seconds)
    """
    from model.preprocess import load_and_preprocess

    t_start = time.time()

    model, class_names = _get_model()
    img_array = load_and_preprocess(image_path, normalize=False)

    # Run inference
    predictions = model.predict(img_array, verbose=0)[0]   # shape: (num_classes,)

    # Top-3 predictions
    top3_idx = np.argsort(predictions)[::-1][:3]
    top3 = [
        {
            'label':      _format_label(class_names[i]),
            'raw_label':  class_names[i],
            'confidence': float(predictions[i])
        }
        for i in top3_idx
    ]

    best = top3[0]
    disease_name = best['label']
    raw_label    = best['raw_label']
    confidence   = best['confidence']
    is_healthy   = 'healthy' in raw_label.lower()
    crop_type    = raw_label.split('___')[0].replace('_', ' ') if '___' in raw_label else 'Unknown'

    # Get recommendation
    recommendation = _get_recommendation(raw_label, is_healthy)

    return {
        'disease_name':    disease_name,
        'crop_type':       crop_type,
        'is_healthy':      is_healthy,
        'confidence':      confidence,
        'top3':            top3,
        'recommendation':  recommendation,
        'processing_time': round(time.time() - t_start, 3),
        'low_confidence':  confidence < Config.CONFIDENCE_THRESHOLD,
    }


def _format_label(raw: str) -> str:
    """Convert 'Tomato___Early_blight' → 'Tomato — Early Blight'."""
    if '___' in raw:
        crop, disease = raw.split('___', 1)
        crop    = crop.replace('_', ' ').title()
        disease = disease.replace('_', ' ').title()
        return f"{crop} — {disease}"
    return raw.replace('_', ' ').title()


def _get_recommendation(raw_label: str, is_healthy: bool) -> str:
    """Return a treatment recommendation for the predicted disease."""
    recs = Config.DISEASE_RECOMMENDATIONS

    if is_healthy:
        return recs.get('healthy', '✅ Crop is healthy.')

    # Try exact match first, then partial match
    if raw_label in recs:
        return recs[raw_label]

    for key, rec in recs.items():
        if key.lower() in raw_label.lower() or raw_label.lower() in key.lower():
            return rec

    return ("⚠️ Disease detected. Consult a local agricultural expert for "
            "specific treatment recommendations.")


def evaluate_model(test_data_dir: str) -> dict:
    """
    Evaluate the model on a test dataset directory.

    Returns dict with accuracy, per-class metrics.
    """
    from model.preprocess import build_tf_dataset

    model, class_names = _get_model()
    _, test_ds, _ = build_tf_dataset(
        test_data_dir, batch_size=32, augment=False, validation_split=0.1
    )

    results = model.evaluate(test_ds, verbose=1, return_dict=True)
    return results
