from fastapi import FastAPI
from app.schemas import TaskCreate, TaskRead

app = FastAPI(
    title="Agent Dashboard Demo",
    description="A simple backend for managing agent tasks.",
    version="0.1.0",
)

tasks = []
next_id = 1


@app.get("/")
def root():
    return {"message": "Agent Dashboard Demo is running"}


@app.post("/tasks", response_model=TaskRead)
def create_task(task: TaskCreate):
    global next_id

    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "status": "pending",
    }

    tasks.append(new_task)
    next_id += 1

    return new_task


@app.get("/tasks", response_model=list[TaskRead])
def list_tasks():
    return tasks