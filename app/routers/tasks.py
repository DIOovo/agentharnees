from fastapi import APIRouter
from app.schemas import TaskCreate, TaskRead

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

tasks = []
next_id = 1


@router.post("", response_model=TaskRead)
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


@router.get("", response_model=list[TaskRead])
def list_tasks():
    return tasks