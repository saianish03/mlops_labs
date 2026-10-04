# Lab 1 - GitHub Actions (Interest Calculator)

Write Python code for a small application, write tests, and let GitHub run tests by itself on every push.

## What I built

An interest calculator in `src/interest.py`. It has these functions:

| Function | What it do |
|---|---|
| `simple_interest(principal, rate, years)` | Interest with no compounding |
| `compound_interest(principal, rate, years, n=1)` | Interest earned with compounding |
| `future_value(principal, rate, years, n=1)` | Money + interest after compounding |
| `monthly_emi(principal, annual_rate, months)` | Monthly loan payment |
| `years_to_double(rate)` | Rule of 72: years to double money |

Bad input (negative, text, True/False) gives `ValueError`.

## Folder layout

```
src/interest.py          the code
test/test_pytest.py      the tests (pytest)
requirements.txt         needs pytest
.gitignore               hide venv and cache files
../../.github/workflows/lab1_githublab1_pytest.yaml   GitHub Action (at repo root)
```

## Setup

Make and turn on virtual environment:

```
python -m venv lab_01
source lab_01/bin/activate
pip install -r requirements.txt
```

## Run tests on your machine

```
python -m pytest
```

All tests should pass.

## GitHub Action

File: `.github/workflows/lab1_githublab1_pytest.yaml` (must be at repo root, GitHub only look there).

What it do on every push or pull request to `main`:

1. Get the code
2. Install Python 3.12
3. Install `requirements.txt`
4. Run pytest and save `pytest-report.xml`
5. Upload the report
6. Print "passed" or "failed"

## See result on GitHub

1. Open your repo on GitHub
2. Click **Actions** tab
3. Click latest run named **Pytest**
4. Green tick = tests pass. Red cross = tests fail.
5. Download `test-results` at bottom of the run page to get the report.
