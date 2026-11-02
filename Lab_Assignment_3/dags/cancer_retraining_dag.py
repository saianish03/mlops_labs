from datetime import datetime, timedelta

from airflow.sdk import Param, dag, task

from src import pipeline


@dag(
    dag_id="cancer_model_retraining",
    description="Train 3 models in parallel, keep the best one only if it beats the champion.",
    schedule="0 6 * * *",  # every day 06:00 UTC
    start_date=datetime(2026, 11, 1),
    catchup=False,
    default_args={"owner": "sai", "retries": 1, "retry_delay": timedelta(minutes=1)},
    params={
        "min_rows": Param(500, type="integer", minimum=1, description="Stop if data has fewer rows."),
        "test_size": Param(0.2, type="number", minimum=0.1, maximum=0.5, description="Share of data used for testing."),
        "min_f1": Param(0.95, type="number", minimum=0, maximum=1, description="Best model must reach this f1 to be promoted."),
    },
    tags=["lab3", "retraining"],
)
def cancer_model_retraining():
    @task
    def ingest():
        return pipeline.ingest()

    @task
    def validate(raw_path, params=None):
        return pipeline.validate(raw_path, params["min_rows"])

    @task
    def split(raw_path, params=None):
        return pipeline.split(raw_path, params["test_size"])

    @task
    def train(paths, model_name):
        return pipeline.train(model_name, paths)

    @task
    def pick_best(results):
        return pipeline.pick_best(list(results))

    @task.branch
    def decide(best, params=None):
        ok, reason = pipeline.should_promote(best, params["min_f1"])
        print(f"Promote? {ok} - {reason}")
        return "promote" if ok else "skip_promotion"

    @task
    def promote(best, run_id=None):
        pipeline.promote(best, run_id)

    @task
    def skip_promotion():
        print("Champion stays the same.")

    @task(trigger_rule="none_failed_min_one_success")
    def report(results, best, params=None, run_id=None):
        path = pipeline.write_report(run_id, list(results), best, params["min_f1"])
        print(f"Report saved: {path}")

    raw = ingest()
    checked = validate(raw)
    paths = split(checked)
    results = train.partial(paths=paths).expand(model_name=list(pipeline.MODELS))
    best = pick_best(results)
    verdict = decide(best)
    verdict >> [promote(best), skip_promotion()] >> report(results, best)


cancer_model_retraining()
