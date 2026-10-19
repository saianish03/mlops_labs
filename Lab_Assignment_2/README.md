# Diabetes Progression API

Small project. We train a model on patient health numbers. Then we put the model behind a web API. You send patient numbers, API gives back a score and a risk level.

## What I built

- **Data:** Diabetes dataset from scikit-learn (442 patients, 10 health numbers each). It comes with scikit-learn, no download needed.
- **Model:** Random Forest Regressor. It gives a number (disease progression score), not a class.
- **API:** FastAPI server with 4 endpoints.
- **Risk level:** API turns the score into a word:
  - below 100 = `low`
  - 100 to 199 = `medium`
  - 200 and up = `high`

## Files

```
Lab_Assignemnt_2/
├── src/
│   ├── __init__.py
│   ├── train.py       trains model, saves it in model/
│   └── api.py         the web API
├── model/             made by train.py (model + scores)
├── requirements.txt
└── README.md
```

## Setup (do one time)

Open terminal inside the `Lab_Assignemnt_2` folder.

1. Make virtual environment:
   ```
   python3 -m venv venv
   ```
2. Turn it on:
   ```
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```
3. Install packages:
   ```
   pip install -r requirements.txt
   ```

## Run it

Stay in the `Lab_Assignemnt_2` folder (not inside `src`).

1. Train the model:
   ```
   python -m src.train
   ```
   You will see the scores (r2 and mae). Model file goes to `model/`.

2. Start the API:
   ```
   uvicorn src.api:app --reload
   ```
   Server runs at http://127.0.0.1:8000

3. Open the test page in browser: http://127.0.0.1:8000/docs
   Click an endpoint -> **Try it out** -> **Execute**.

To stop the server press `Ctrl + C`.

## Endpoints

| Method | Path | What it do |
|---|---|---|
| GET | `/health` | Says server is ok |
| GET | `/model` | Shows model name, feature names, r2 and mae scores |
| POST | `/score` | Score one patient |
| POST | `/score/batch` | Score 1 to 100 patients in one call |

### Try with curl

Score one patient:

```
curl -X POST http://127.0.0.1:8000/score \
  -H "Content-Type: application/json" \
  -d '{"age":0.04,"sex":0.05,"bmi":0.06,"bp":0.02,"s1":-0.04,"s2":-0.03,"s3":-0.04,"s4":0.0,"s5":0.02,"s6":-0.02}'
```

Answer:

```
{"score": 218.37, "risk": "high"}
```

Score many patients: send `{"patients": [ {...}, {...} ]}` to `/score/batch`. You get a list of answers back, same order.

### Input fields

All 10 are numbers. They are already scaled (small numbers near 0), same as scikit-learn diabetes data.

`age`, `sex`, `bmi`, `bp`, `s1` (cholesterol), `s2` (LDL), `s3` (HDL), `s4` (cholesterol ratio), `s5` (triglycerides), `s6` (blood sugar)

If a field is missing or not a number, API says `422` and tells which field is wrong.

## Note

- Model loads one time when server starts, not on every request.
- If server says "No model found", you forgot step 1. Run `python -m src.train`.
- Paths work from any folder, but run commands from `Lab_Assignemnt_2` to keep it simple.
