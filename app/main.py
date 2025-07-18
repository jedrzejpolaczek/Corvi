from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.tasks import optimize_model
import uuid, os, shutil, json

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})


@app.post("/optimize/")
async def optimize(
    request: Request,
    model_file: UploadFile = File(...),
    data_file: UploadFile = File(...),
    hyperparams_file: UploadFile = File(...),
    metric: str = Form(...)
):
    task_id = str(uuid.uuid4())
    task_dir = f"uploads/{task_id}"
    os.makedirs(task_dir, exist_ok=True)

    model_path = f"{task_dir}/{model_file.filename}"
    data_path = f"{task_dir}/{data_file.filename}"
    hyperparams_path = f"{task_dir}/{hyperparams_file.filename}"

    with open(model_path, "wb") as f:
        shutil.copyfileobj(model_file.file, f)
    with open(data_path, "wb") as f:
        shutil.copyfileobj(data_file.file, f)
    # HYPERPARAMETERS: from uploaded file or use default
    if hyperparams_file and hyperparams_file.filename:
        hyperparams_path = f"{task_dir}/{hyperparams_file.filename}"
        with open(hyperparams_path, "wb") as f:
            shutil.copyfileobj(hyperparams_file.file, f)
        with open(hyperparams_path, "r") as f:
            hyperparams_content = f.read()
    else:
        # Default hyperparameters if none provided
        hyperparams_content = json.dumps({
            "learning_rate": [0.001, 0.1],
            "max_depth": [3, 10]
        })

    optimize_model.delay(task_id, model_path, data_path, hyperparams_content, metric)

    return templates.TemplateResponse("upload_form.html", {
        "request": request,
        "message": f"Task {task_id} started.",
        "task_id": task_id
    })


@app.get("/status/{task_id}", response_class=HTMLResponse)
async def status(request: Request, task_id: str):
    result_path = f"results/{task_id}.json"
    if os.path.exists(result_path):
        return templates.TemplateResponse("upload_form.html", {
            "request": request,
            "task_id": task_id,
            "download_url": f"/download/{task_id}"
        })
    else:
        return templates.TemplateResponse("upload_form.html", {
            "request": request,
            "task_id": task_id,
            "message": "Optimization in progress..."
        })


@app.get("/api/status/{task_id}")
async def api_status(task_id: str):
    result_path = f"results/{task_id}.json"
    if os.path.exists(result_path):
        return {"status": "completed", "download_url": f"/download/{task_id}"}
    elif os.path.exists(f"uploads/{task_id}") and not os.listdir(f"uploads/{task_id}"):
        return {"status": "error"}
    else:
        return {"status": "in_progress"}


@app.get("/download/{task_id}")
async def download(task_id: str):
    result_path = f"results/{task_id}.json"
    if os.path.exists(result_path):
        return FileResponse(result_path, media_type="application/json", filename=f"{task_id}_results.json")
    return JSONResponse(content={"error": "Result file not found"}, status_code=404)
