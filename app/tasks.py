from celery import Celery
import optuna, json, pandas as pd
import importlib.util, os

celery = Celery(__name__, broker="redis://redis:6379/0")

@celery.task
def optimize_model(task_id, model_path, data_path, hyperparams_json, metric):
    spec = importlib.util.spec_from_file_location("user_model", model_path)
    user_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_module)
    model_class = getattr(user_module, "MyModel")

    df = pd.read_csv(data_path)
    X, y = df.drop("target", axis=1), df["target"]
    hyperparams = json.loads(hyperparams_json)

    def objective(trial):
        params = {
            key: trial.suggest_float(key, *val) if isinstance(val[0], float)
            else trial.suggest_int(key, *val)
            for key, val in hyperparams.items()
        }
        model = model_class(**params)
        model.fit(X, y)
        preds = model.predict(X)
        return (preds == y).mean() if metric == "accuracy" else 0.0

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)

    os.makedirs("results", exist_ok=True)
    result = {
        "task_id": task_id,
        "best_params": study.best_trial.params,
        "score": study.best_trial.value
    }
    with open(f"results/{task_id}.json", "w") as f:
        json.dump(result, f)