import json
from pathlib import Path

import joblib
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
MODEL_PATH = MODEL_DIR / "diabetes_model.joblib"
INFO_PATH = MODEL_DIR / "model_info.json"


def train():
    """Train a Random Forest on the diabetes dataset and save model + scores."""
    data = load_diabetes()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    info = {
        "model": "RandomForestRegressor",
        "features": list(data.feature_names),
        "r2": round(r2_score(y_test, preds), 3),
        "mae": round(mean_absolute_error(y_test, preds), 3),
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    INFO_PATH.write_text(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    print("Model saved:", train())
