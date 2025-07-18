# SaaS for Hyperparameter Optimization

## Launch

```bash
docker-compose up --build
```

The application will be available at: [http://localhost:8000](http://localhost:8000)

## Features

- Upload .py model file, .csv dataset, hyperparameters, and evaluation metric
- Check task status using task_id
- Download optimization result as a .json file

## TODO

- Sandbox user code (Docker-in-Docker, restrictedexec, etc.)
- Support for multiple evaluation metrics (f1, roc_auc, etc.)
- User authentication