"""
Train a scam-detection ML model on large CSVs using chunked / streaming training.

Usage:
    cd backend
    python -m app.ml.train

Saves model.joblib and vectorizer.joblib into app/ml/data/
"""

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, precision_recall_curve
import joblib
from scipy.sparse import hstack

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = DATA_DIR / "sample_scams.csv"
CLEAN_CSV_PATH = DATA_DIR / "sample_scams_clean.csv"
MODEL_PATH = DATA_DIR / "model.joblib"
VECTORIZER_PATH = DATA_DIR / "vectorizer.joblib"
HOLDOUT_PATH = DATA_DIR / "holdout_first_chunk.csv"


class CombinedHashingVectorizer:
    """Pickle-friendly vectorizer combining word and char hashing features."""

    def __init__(self, *, n_features_word: int, n_features_char: int):
        self.word = HashingVectorizer(
            n_features=n_features_word,
            ngram_range=(1, 2),
            stop_words="english",
            lowercase=True,
            alternate_sign=False,
        )
        self.char = HashingVectorizer(
            n_features=n_features_char,
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
            alternate_sign=False,
        )

    def transform(self, X):
        return hstack([self.word.transform(X), self.char.transform(X)], format="csr")


def load_data() -> pd.DataFrame:
    """Load and validate the training CSV."""
    # Prefer cleaned dataset if available
    path = CLEAN_CSV_PATH if CLEAN_CSV_PATH.exists() else CSV_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Training data not found at {path}. "
            "Please create sample_scams.csv (or sample_scams_clean.csv) "
            "with columns: text, label (0=safe, 1=scam)"
        )
    if path == CLEAN_CSV_PATH:
        print(f"Using cleaned dataset: {CLEAN_CSV_PATH.name}")
    else:
        print(f"Using raw dataset: {CSV_PATH.name}")

    # Allow both comma- and tab-separated CSVs.
    # sep=None with engine="python" lets pandas auto-detect the delimiter.
    df = pd.read_csv(path, sep=None, engine="python")
    assert "text" in df.columns and "label" in df.columns, (
        "CSV must have 'text' and 'label' columns."
    )

    # Compute label stats robustly (some rows may be malformed).
    labels_num = pd.to_numeric(df["label"], errors="coerce")
    scam = int((labels_num == 1).sum())
    safe = int((labels_num == 0).sum())
    print(f"Loaded {len(df)} samples  |  scam={scam}  safe={safe}")
    return df


def train():
    """Full training pipeline using chunked streaming over the CSV.

    Strategy:
    - Print basic stats once via load_data (sanity check).
    - Re-read the CSV in chunks to avoid loading everything into RAM.
    - Use a HashingVectorizer (stateless) + SGDClassifier with partial_fit.
    - Use a small hold-out split from the first chunk for evaluation.
    """
    # This prints stats and validates columns, but we won't keep df in memory.
    load_data()

    # Re-read from disk in chunks for memory efficiency.
    path = CLEAN_CSV_PATH if CLEAN_CSV_PATH.exists() else CSV_PATH

    # Chunked iterator over the CSV
    chunksize = 100_000

    # Stronger features: word(1,2) + char_wb(3,5) with a larger hash space
    vectorizer = CombinedHashingVectorizer(
        n_features_word=2**16,
        n_features_char=2**16,
    )

    model = SGDClassifier(
        loss="log_loss",
        max_iter=5,
        random_state=42,
    )

    first_chunk = True
    X_val = y_val = None
    total_samples = 0
    epochs = 1

    for epoch in range(1, epochs + 1):
        reader = pd.read_csv(path, sep=None, engine="python", chunksize=chunksize)
        print(f"\n== Training epoch {epoch}/{epochs} =====================")

        for i, chunk in enumerate(reader, start=1):
            # Drop rows without mandatory fields, and coerce label to numeric 0/1
            chunk = chunk.dropna(subset=["text", "label"])
            if chunk.empty:
                continue

            chunk["label"] = pd.to_numeric(chunk["label"], errors="coerce")
            chunk = chunk[chunk["label"].isin([0, 1])]
            if chunk.empty:
                continue

            X_chunk = chunk["text"].astype(str)
            y_chunk = chunk["label"].astype(int)

            if first_chunk:
                # Create a holdout split from the first chunk (and persist it)
                X_train, X_val, y_train, y_val = train_test_split(
                    X_chunk, y_chunk, test_size=0.2, random_state=42, stratify=y_chunk
                )
                try:
                    pd.DataFrame({"text": X_val, "label": y_val}).to_csv(HOLDOUT_PATH, index=False)
                    print(f"Saved holdout set to {HOLDOUT_PATH}")
                except Exception as e:
                    print(f"[WARN] Could not save holdout CSV: {e}")

                X_vec = vectorizer.transform(X_train)
                classes = [0, 1]
                model.partial_fit(X_vec, y_train, classes=classes)
                first_chunk = False
                total_samples += len(X_train)
                print(f"Trained on first chunk: {len(X_train)} samples")
            else:
                X_vec = vectorizer.transform(X_chunk)
                model.partial_fit(X_vec, y_chunk)
                total_samples += len(X_chunk)
                if i % 2 == 0:
                    print(f"Trained on chunk {i}: {len(X_chunk)} samples (total so far: {total_samples})")

    # Evaluation on held-out validation set from first chunk (if available)
    if X_val is not None and y_val is not None:
        X_val_vec = vectorizer.transform(X_val)
        y_pred = model.predict(X_val_vec)
        print("\n== Evaluation (on first-chunk holdout) =====")
        print(f"  Accuracy:  {accuracy_score(y_val, y_pred):.4f}")
        print(f"  Precision: {precision_score(y_val, y_pred):.4f}")
        print(f"  Recall:    {recall_score(y_val, y_pred):.4f}")
        print(f"  F1 Score:  {f1_score(y_val, y_pred):.4f}")
        print("\n" + classification_report(y_val, y_pred, target_names=["Safe", "Scam"]))

        # Threshold tuning to improve Scam recall/F1 if desired
        try:
            y_score = model.predict_proba(X_val_vec)[:, 1]
            p, r, t = precision_recall_curve(y_val, y_score)
            f1 = (2 * p * r) / (p + r + 1e-12)
            best_idx = int(f1.argmax())
            best_thr = float(t[max(0, best_idx - 1)]) if len(t) else 0.5
            print(f"\nSuggested scam threshold (max F1 on holdout): {best_thr:.3f}")
        except Exception as e:
            print(f"[WARN] Threshold tuning skipped: {e}")
    else:
        print("No validation split available; training completed without evaluation.")

    # Save artefacts
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_PATH}")


if __name__ == "__main__":
    train()
