"""
train_model.py – MobileNetV2 Transfer-Learning trainer for PlantVillage (38 classes)

Usage (auto-download via kagglehub – recommended):
    python train_model.py --epochs 20

Usage (local dataset):
    python train_model.py --data_dir /path/to/dataset --epochs 20

The script:
1. Downloads the PlantVillage dataset via kagglehub (if --data_dir not given).
2. Loads MobileNetV2 (ImageNet weights, no top).
3. Freezes base layers; adds custom classifier head.
4. Trains with ImageDataGenerator augmentation.
5. Evaluates on validation set.
6. Saves best model → mobilenetv2_best.keras
"""

import argparse
import os
import json
from pathlib import Path
from typing import Optional

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (EarlyStopping, ModelCheckpoint,
                                         ReduceLROnPlateau)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
NUM_CLASSES = 38
LR          = 1e-4
SEED        = 42

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Train MobileNetV2 on PlantVillage")
    p.add_argument("--data_dir", default=None,
                   help="Root folder of dataset (must contain 'train' and 'valid' sub-folders). "
                        "If omitted, the dataset is downloaded automatically via kagglehub.")
    p.add_argument("--epochs",    type=int, default=20,
                   help="Number of fine-tuning epochs (default 20)")
    p.add_argument("--batch",     type=int, default=BATCH_SIZE,
                   help="Batch size (default 32)")
    p.add_argument("--fine_tune", type=int, default=0,
                   help="Num of base layers to unfreeze for fine-tuning (0 = disabled)")
    p.add_argument("--output",    default="mobilenetv2_best.keras",
                   help="Output model filename")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Dataset resolution  (kagglehub download or local path)
# ─────────────────────────────────────────────────────────────────────────────
def resolve_data_dir(data_dir_arg: str) -> str:
    """Return the path that directly contains 'train/' and 'valid/' folders."""
    if data_dir_arg:
        # User provided a path — verify it
        if not os.path.isdir(data_dir_arg):
            raise FileNotFoundError(f"data_dir not found: {data_dir_arg}")
        root = _find_split_root(data_dir_arg)
        if root:
            return root
        raise FileNotFoundError(
            f"Could not find 'train' and 'valid' sub-folders inside: {data_dir_arg}"
        )

    # ── Auto-download via kagglehub ──────────────────────────────────────────
    print("\n📥  No --data_dir supplied. Downloading dataset via kagglehub …")
    try:
        import kagglehub
    except ImportError:
        raise ImportError(
            "kagglehub is not installed. Run: pip install kagglehub\n"
            "Or supply the dataset path manually with --data_dir."
        )

    download_root = kagglehub.dataset_download("vipoooool/new-plant-diseases-dataset")
    print(f"✅  Dataset downloaded to: {download_root}")

    root = _find_split_root(download_root)
    if root:
        print(f"📂  Using split root: {root}")
        return root

    raise FileNotFoundError(
        f"Downloaded dataset at '{download_root}' does not contain 'train'/'valid' folders. "
        "Please inspect the folder and supply --data_dir manually."
    )


def _find_split_root(base: str) -> Optional[str]:
    """
    Walk up to 3 levels deep inside *base* to find the directory that
    directly contains both 'train' and 'valid' sub-folders.
    """
    base = Path(base)
    # Check base itself first, then recurse up to depth 3
    for depth in range(4):
        for candidate in _walk_depth(base, depth):
            if (candidate / "train").is_dir() and (candidate / "valid").is_dir():
                return str(candidate)
    return None


def _walk_depth(root: Path, depth: int):
    """Yield all directories exactly *depth* levels below root."""
    if depth == 0:
        yield root
        return
    for child in root.iterdir():
        if child.is_dir():
            yield from _walk_depth(child, depth - 1)




# ─────────────────────────────────────────────────────────────────────────────
# Data generators
# ─────────────────────────────────────────────────────────────────────────────
def build_generators(data_dir: str, batch: int):
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.25,
        brightness_range=[0.75, 1.25],
        horizontal_flip=True,
        vertical_flip=False,
        fill_mode="nearest",
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, "train"),
        target_size=IMG_SIZE,
        batch_size=batch,
        class_mode="categorical",
        shuffle=True,
        seed=SEED,
    )

    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, "valid"),
        target_size=IMG_SIZE,
        batch_size=batch,
        class_mode="categorical",
        shuffle=False,
    )

    print(f"\n📂  Training samples : {train_gen.samples}")
    print(f"📂  Validation samples: {val_gen.samples}")
    print(f"🏷️   Classes          : {train_gen.num_classes}")

    # Save class indices for inference consistency
    class_indices_path = Path("class_indices.json")
    import json
    with open(class_indices_path, "w") as f:
        json.dump(train_gen.class_indices, f, indent=2)
    print(f"✅  Class indices saved → {class_indices_path}")

    return train_gen, val_gen


# ─────────────────────────────────────────────────────────────────────────────
# Model builder
# ─────────────────────────────────────────────────────────────────────────────
def build_model(num_classes: int = NUM_CLASSES, fine_tune_layers: int = 0) -> Model:
    # 1. Load base model
    base = MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # Freeze all by default

    # Optionally unfreeze last N layers for fine-tuning
    if fine_tune_layers > 0:
        for layer in base.layers[-fine_tune_layers:]:
            if not isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = True
        print(f"🔓  Fine-tuning last {fine_tune_layers} base layers.")

    # 2. Custom head
    x = base.output
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dropout(0.3, name="drop1")(x)
    x = layers.Dense(256, activation="relu", name="fc256")(x)
    x = layers.Dropout(0.2, name="drop2")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = Model(inputs=base.input, outputs=outputs, name="PlantCareAI_MobileNetV2")

    # 3. Compile
    model.compile(
        optimizer=Adam(learning_rate=LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    trainable_count = sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    total_count = sum(tf.keras.backend.count_params(w) for w in model.weights)
    print(f"\n🧠  Trainable params : {trainable_count:,}")
    print(f"🧠  Total params     : {total_count:,}")

    return model


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────
def train(args):
    tf.random.set_seed(SEED)
    np.random.seed(SEED)

    print("\n" + "=" * 60)
    print("   🌿  PlantCare AI — MobileNetV2 Trainer")
    print("=" * 60)

    data_dir = resolve_data_dir(args.data_dir)
    train_gen, val_gen = build_generators(data_dir, args.batch)
    
    dynamic_num_classes = train_gen.num_classes
    print(f"🛠️  Building model for {dynamic_num_classes} classes...")
    model = build_model(num_classes=dynamic_num_classes, fine_tune_layers=args.fine_tune)

    callbacks = [
        ModelCheckpoint(
            filepath=args.output,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    print(f"\n🚀  Starting training for {args.epochs} epoch(s)…\n")
    history = model.fit(
        train_gen,
        epochs=args.epochs,
        validation_data=val_gen,
        callbacks=callbacks,
    )

    # ── Evaluate ──────────────────────────────────────────────────────────────
    print("\n📊  Final evaluation on validation set:")
    loss, acc = model.evaluate(val_gen, verbose=0)
    print(f"    Loss     : {loss:.4f}")
    print(f"    Accuracy : {acc * 100:.2f}%")

    print(f"\n✅  Best model saved → {args.output}")
    return history


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args()
    train(args)
