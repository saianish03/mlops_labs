import json
from contextlib import asynccontextmanager
from typing import List

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.train import INFO_PATH, MODEL_PATH

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model one time when the server starts."""
    if not MODEL_PATH.exists():
        raise RuntimeError("No model found. Run: python -m src.train")
    state["model"] = joblib.load(MODEL_PATH)
    state["info"] = json.loads(INFO_PATH.read_text())
    yield
    state.clear()


app = FastAPI(title="Diabetes Progression API", lifespan=lifespan)


class Patient(BaseModel):
    """One patient. Values are the standardized numbers from the sklearn diabetes data."""
    age: float
    sex: float
    bmi: float
    bp: float
    s1: float = Field(description="total serum cholesterol")
    s2: float = Field(description="LDL cholesterol")
    s3: float = Field(description="HDL cholesterol")
    s4: float = Field(description="total cholesterol / HDL")
    s5: float = Field(description="log of serum triglycerides")
    s6: float = Field(description="blood sugar level")


class Prediction(BaseModel):
    score: float
    risk: str


class BatchRequest(BaseModel):
    patients: List[Patient] = Field(min_length=1, max_length=100)


def to_risk(score: float) -> str:
    if score < 100:
        return "low"
    if score < 200:
        return "medium"
    return "high"


def predict(patients: List[Patient]) -> List[Prediction]:
    rows = [[getattr(p, name) for name in state["info"]["features"]] for p in patients]
    scores = state["model"].predict(rows)
    return [Prediction(score=round(float(s), 2), risk=to_risk(s)) for s in scores]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model")
def model_info():
    """Tell which model is running and how good it is."""
    return state["info"]


@app.post("/score", response_model=Prediction)
def score_one(patient: Patient):
    """Score one patient."""
    try:
        return predict([patient])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score/batch", response_model=List[Prediction])
def score_many(request: BatchRequest):
    """Score many patients (1 to 100) in one call."""
    try:
        return predict(request.patients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
