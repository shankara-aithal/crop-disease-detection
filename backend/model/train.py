# MUST be first — disable Intel oneDNN before TensorFlow loads
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
import json
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tensorflow as tf
from tensorflow import keras


def build_dataset(directory, batch_size=16, shuffle=True, augment=False):
    ds = tf.keras.utils.image_dataset_from_directory(
        directory,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=shuffle,
        label_mode='categorical',
        seed=42,
    )
    class_names = ds.class_names
    print(f"  Loaded {len(class_names)} classes from: {directory}")

    # MobileNetV2 preprocess_input needs raw [0,255] — do NOT rescale first
    preprocess = tf.keras.applications.mobilenet_v2.preprocess_input

    if augment:
        aug = tf.keras.Sequential([
            tf.keras.layers.RandomFlip("horizontal_and_vertical"),
            tf.keras.layers.RandomRotation(0.2),
            tf.keras.layers.RandomZoom(0.15),
        ])
        ds = ds.map(
            lambda x, y: (preprocess(aug(x, training=True)), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )
    else:
        ds = ds.map(
            lambda x, y: (preprocess(x), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )

    # prefetch only — no .cache() to save RAM
    return ds.prefetch(tf.data.AUTOTUNE), class_names


def build_model(num_classes):
    base = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base.trainable = False

    inputs  = keras.Input(shape=(224, 224, 3))
    x       = base(inputs, training=False)
    x       = keras.layers.GlobalAveragePooling2D()(x)
    x       = keras.layers.BatchNormalization()(x)
    x       = keras.layers.Dense(256, activation='relu')(x)
    x       = keras.layers.Dropout(0.4)(x)
    outputs = keras.layers.Dense(num_classes, activation='softmax')(x)

    return keras.Model(inputs, outputs, name='CropDisease_MobileNetV2'), base


def train(train_dir, val_dir, epochs=20, batch_size=16, fine_tune=False):
    print(f"\n{'='*60}")
    print("  CropGuard AI — Fixed Training Script")
    print(f"  TF version : {tf.__version__}")
    print(f"  oneDNN     : DISABLED (fixes AbortedError)")
    print(f"  Train dir  : {train_dir}")
    print(f"  Val dir    : {val_dir}")
    print(f"  Epochs     : {epochs}  |  Batch: {batch_size}")
    print(f"{'='*60}\n")

    print("[1/4] Loading training data...")
    train_ds, class_names = build_dataset(train_dir, batch_size, shuffle=True,  augment=True)

    print("[2/4] Loading validation data...")
    val_ds, _             = build_dataset(val_dir,   batch_size, shuffle=False, augment=False)

    num_classes = len(class_names)
    print(f"\n  Classes : {num_classes}")
    print(f"  First 3 : {class_names[:3]}\n")

    print("[3/4] Building model...")
    model, base_model = build_model(num_classes)
    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top3')]
    )
    print(f"  Trainable params: {model.count_params():,}\n")

    save_dir  = os.path.join(os.path.dirname(__file__), 'saved_model')
    os.makedirs(save_dir, exist_ok=True)
    ckpt      = os.path.join(save_dir, 'crop_cnn.h5')

    callbacks = [
        keras.callbacks.ModelCheckpoint(ckpt, save_best_only=True,
                                        monitor='val_accuracy', verbose=1),
        keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5,
                                      restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                          patience=3, min_lr=1e-7, verbose=1),
    ]

    print("[4/4] Phase 1 — Training head (base frozen)...")
    print("      Accuracy should jump above 70% by epoch 2\n")

    history = model.fit(train_ds, epochs=epochs,
                        validation_data=val_ds, callbacks=callbacks)

    best_val = max(history.history['val_accuracy'])

    if fine_tune and best_val > 0.80:
        print(f"\n  Fine-tuning: unfreezing top 30 MobileNetV2 layers...")
        base_model.trainable = True
        for layer in base_model.layers[:-30]:
            layer.trainable = False

        model.compile(
            optimizer=keras.optimizers.Adam(1e-5),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top3')]
        )
        model.fit(train_ds, epochs=epochs + 10,
                  initial_epoch=len(history.epoch),
                  validation_data=val_ds,
                  callbacks=[
                      keras.callbacks.ModelCheckpoint(ckpt, save_best_only=True,
                                                      monitor='val_accuracy', verbose=1),
                      keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5,
                                                    restore_best_weights=True, verbose=1),
                  ])
        best_val = max(history.history['val_accuracy'])

    # Save class names
    with open(os.path.join(save_dir, 'class_names.json'), 'w') as f:
        json.dump({str(i): n for i, n in enumerate(class_names)}, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"  Best Val Accuracy : {best_val*100:.2f}%")
    print(f"  Model saved       : {ckpt}")
    print(f"  Class names saved : {save_dir}\\class_names.json")
    print(f"{'='*60}")

    if best_val < 0.50:
        print("\n  !! Accuracy still low. Run this command to check your dataset:")
        print(f"     dir \"{train_dir}\"")
        print("     You should see 38 folders like Apple___Apple_scab inside.")

    # Plot curves
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(history.history['accuracy'],     label='Train', color='green')
        ax1.plot(history.history['val_accuracy'], label='Val',   color='red')
        ax1.set_title('Accuracy'); ax1.legend(); ax1.grid(alpha=0.3)
        ax2.plot(history.history['loss'],         label='Train', color='green')
        ax2.plot(history.history['val_loss'],     label='Val',   color='red')
        ax2.set_title('Loss');     ax2.legend(); ax2.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, 'training_curves.png'), dpi=150)
        print(f"\n  Curves saved to: {save_dir}\\training_curves.png")
    except Exception as e:
        print(f"  (Curve save skipped: {e})")

    return model


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='CropGuard AI Fixed Training')
    p.add_argument('--train_dir',  required=True)
    p.add_argument('--val_dir',    required=True)
    p.add_argument('--epochs',     type=int, default=20)
    p.add_argument('--batch_size', type=int, default=16)
    p.add_argument('--fine_tune',  action='store_true')
    a = p.parse_args()
    train(a.train_dir, a.val_dir, a.epochs, a.batch_size, a.fine_tune)