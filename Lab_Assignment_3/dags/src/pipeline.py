"""Plain Python steps for the retraining pipeline. No Airflow code in here."""
import json
import os
import shutil
from pathlib import Path

import joblib
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/opt/airflow/output"))
DATA_DIR = OUTPUT_DIR / "data"
CANDIDATE_DIR = OUTPUT_DIR / "candidates"
CHAMPION_DIR = OUTPUT_DIR / "champion"
REPORT_DIR = OUTPUT_DIR / "reports"

MODELS = {
    "logistic_regression": lambda: make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=1000)
    ),
    "random_forest": lambda: RandomForestClassifier(n_estimators=100, random_state=42),
    "gradient_boosting": lambda: GradientBoostingClassifier(random_state=42),
}


def ingest():
    """Save the breast cancer data as a csv. Returns the csv path."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = load_breast_cancer(as_frame=True).frame  # last column 'target': 0 = malignant, 1 = benign
    path = DATA_DIR / "raw.csv"
    df.to_csv(path, index=False)
    return str(path)


def validate(raw_path, min_rows):
    """Stop the pipeline if data looks bad. Returns the csv path."""
    df = pd.read_csv(raw_path)
    if len(df) < min_rows:
        raise ValueError(f"Only {len(df)} rows, need at least {min_rows}.")
    if df.isna().any().any():
        raise ValueError("Data has missing values.")
    if df["target"].nunique() < 2:
        raise ValueError("Data has only one class.")
    return raw_path


def split(raw_path, test_size):
    """Split into train and test csv files. Returns both paths."""
    df = pd.read_csv(raw_path)
    train_df, test_df = train_test_split(
        df, test_size=test_size, random_state=42, stratify=df["target"]
    )
    train_path, test_path = DATA_DIR / "train.csv", DATA_DIR / "test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    return {"train": str(train_path), "test": str(test_path)}


def train(model_name, paths):
    """Train one model, save it, return its scores."""
    train_df, test_df = pd.read_csv(paths["train"]), pd.read_csv(paths["test"])
    model = MODELS[model_name]()
    model.fit(train_df.drop(columns="target"), train_df["target"])

    preds = model.predict(test_df.drop(columns="target"))
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    model_path = CANDIDATE_DIR / f"{model_name}.joblib"
    joblib.dump(model, model_path)
    return {
        "model_name": model_name,
        "accuracy": round(accuracy_score(test_df["target"], preds), 4),
        "f1": round(f1_score(test_df["target"], preds), 4),
        "path": str(model_path),
    }


def pick_best(results):
    """Return the result with the highest f1."""
    return max(results, key=lambda r: r["f1"])


def current_champion():
    """Return the saved champion scores, or None if there is no champion yet."""
    info_path = CHAMPION_DIR / "champion.json"
    return json.loads(info_path.read_text()) if info_path.exists() else None


def should_promote(best, min_f1):
    """Say yes only if best is good enough AND better than the champion."""
    if best["f1"] < min_f1:
        return False, f"f1 {best['f1']} is below the minimum {min_f1}"
    champion = current_champion()
    if champion and best["f1"] <= champion["f1"]:
        return False, f"f1 {best['f1']} does not beat champion {champion['f1']}"
    return True, "good enough and better than the champion"


def promote(best, run_id):
    """Copy the best model to the champion folder and remember which run did it."""
    CHAMPION_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(best["path"], CHAMPION_DIR / "champion.joblib")
    info = {**best, "promoted_by_run": run_id}
    (CHAMPION_DIR / "champion.json").write_text(json.dumps(info, indent=2))


def write_report(run_id, results, best, min_f1):
    """Write a small json report for this run. Returns the report path."""
    champion = current_champion()
    promoted = bool(champion) and champion.get("promoted_by_run") == run_id
    reason = "promoted to champion" if promoted else should_promote(best, min_f1)[1]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "run_id": run_id,
        "scores": results,
        "best_model": best["model_name"],
        "promoted": promoted,
        "reason": reason,
    }
    path = REPORT_DIR / "latest_report.json"
    path.write_text(json.dumps(report, indent=2))
    return str(path)
