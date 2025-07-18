# Local Deployment Instructions

## 📦 Requirements

- Docker
- Docker Compose

---

## 🚀 Running Locally

### 1. Unzip or clone the project

If you downloaded `hyperopt_saas.zip`:

```bash
unzip hyperopt_saas.zip
cd hyperopt_saas
```

Or clone the repository:

```bash
git clone <repo_url>
cd hyperopt_saas
```

---

### 2. Build and start the app

```bash
docker-compose up --build
```

This starts:
- API at `http://localhost:8000`
- Redis queue
- Celery worker

---

### 3. Open in your browser

Navigate to:

[http://localhost:8000](http://localhost:8000)

The form allows uploading:
- `.py` model file with `MyModel`
- `.csv` data file (must have `target` column)
- hyperparameters in JSON (e.g., `{ "lr": [0.01, 0.1] }`)
- metric (e.g., `accuracy`)

---

## 🧪 Example Data

### 🔧 `MyModel.py`

```python
class MyModel:
    def __init__(self, learning_rate=0.01, max_depth=3):
        self.learning_rate = learning_rate
        self.max_depth = max_depth

    def fit(self, X, y):
        pass

    def predict(self, X):
        return [0 for _ in range(len(X))]
```

### 📊 `data.csv`

```csv
feature1,feature2,target
0.5,1.2,0
0.6,1.1,0
1.5,2.2,1
1.6,2.1,1
```

### ⚙️ JSON hyperparameters

```json
{
  "learning_rate": [0.01, 0.1],
  "max_depth": [3, 5]
}
```

---

## 📥 Result

After optimization:
- Visit `/status/<task_id>`
- Download the `.json` result

---

## 🛠️ Useful Commands

Logs:

```bash
docker-compose logs -f
```

Stop and clean up:

```bash
docker-compose down -v
```

---

## 🧱 TODO

- Sandbox user code (Docker-in-Docker)
- Support more metrics: `f1`, `roc_auc`, etc.
- Add user accounts + task history