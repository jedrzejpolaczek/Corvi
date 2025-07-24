# task.py
from celery import Celery
import optuna, json, pandas as pd
import importlib.util, os, time, psutil, logging
import GPUtil

celery = Celery(__name__, broker="redis://redis:6379/0")

@celery.task
def optimize_model(task_id, model_path, data_path, hyperparams_json, metric):
    total_start = time.time()

    # Setup logging
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{task_id}.log"
    logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s - %(message)s")

    logging.info(f"Starting optimization for task {task_id}")
    process = psutil.Process(os.getpid())

    try:
        # --- Ładowanie modelu i danych ---
        load_start = time.time()

        # Dynamic import model
        spec = importlib.util.spec_from_file_location("user_model", model_path)
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)
        model_class = getattr(user_module, "MyModel")

        # Load dataset
        df = pd.read_csv(data_path)
        X, y = df.drop("target", axis=1), df["target"]

        # Dataset stats
        file_size = os.path.getsize(data_path) / (1024 ** 2)
        logging.info(f"Dataset file size: {file_size:.2f} MB")
        logging.info(f"Dataset shape: {X.shape[0]} samples, {X.shape[1]} features")

        # Load hyperparameters
        hyperparams = json.loads(hyperparams_json)

        load_duration = time.time() - load_start
        logging.info(f"Data/model load time: {load_duration:.2f} seconds")

        # --- Optuna optymalizacja ---
        optuna_start = time.time()

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

        optuna_duration = time.time() - optuna_start
        logging.info(f"Optuna optimization time: {optuna_duration:.2f} seconds")

        # --- Zapis wyników ---
        os.makedirs("results", exist_ok=True)
        result = {
            "task_id": task_id,
            "best_params": study.best_trial.params,
            "score": study.best_trial.value
        }
        with open(f"results/{task_id}.json", "w") as f:
            json.dump(result, f)

        # --- Zasoby systemowe ---
        cpu_percent = process.cpu_percent(interval=1)
        mem_info = process.memory_info()
        gpu_info = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None
        total_duration = time.time() - total_start

        logging.info(f"CPU usage: {cpu_percent}%")
        logging.info(f"RAM usage: {mem_info.rss / (1024 ** 2):.2f} MB")
        if gpu_info:
            logging.info(f"GPU usage: {gpu_info.load * 100:.2f}%")
            logging.info(f"GPU memory usage: {gpu_info.memoryUsed}MB / {gpu_info.memoryTotal}MB")
        else:
            logging.info("GPU: Not available")

        logging.info(f"Total execution time: {total_duration:.2f} seconds")
        logging.info("Optimization completed successfully.")

    except Exception as e:
        logging.exception("Optimization failed with an exception.")
        raise e
