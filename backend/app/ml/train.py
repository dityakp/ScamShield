"""
Train a scam-detection ML model (TF-IDF + Logistic Regression).

Usage:
    cd backend
    python -m app.ml.train

Saves model.joblib and vectorizer.joblib into app/ml/data/
"""

import os
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = DATA_DIR / "sample_scams.csv"
MODEL_PATH = DATA_DIR / "model.joblib"
VECTORIZER_PATH = DATA_DIR / "vectorizer.joblib"


def load_data() -> pd.DataFrame:
    """Load and validate the training CSV."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Training data not found at {CSV_PATH}. "
            "Please create sample_scams.csv with columns: text, label (0=safe, 1=scam)"
        )
    df = pd.read_csv(CSV_PATH)
    assert "text" in df.columns and "label" in df.columns, (
        "CSV must have 'text' and 'label' columns."
    )
    print(f"Loaded {len(df)} samples  |  scam={df['label'].sum()}  safe={len(df) - df['label'].sum()}")
    return df


def train():
    """Full training pipeline."""
    df = load_data()

    # Text preprocessing (lowercasing handled by TF-IDF)
    X = df["text"].astype(str)
    y = df["label"].astype(int)

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words="english",
        lowercase=True,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model training
    model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train_vec, y_train)

    # Evaluation
    y_pred = model.predict(X_test_vec)
    print("\n── Evaluation ──────────────────────────────")
    print(f"  Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"  Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"  Recall:    {recall_score(y_test, y_pred):.4f}")
    print(f"  F1 Score:  {f1_score(y_test, y_pred):.4f}")
    print("\n" + classification_report(y_test, y_pred, target_names=["Safe", "Scam"]))

    # Save artefacts
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_PATH}")


if __name__ == "__main__":
    train()
