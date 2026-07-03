from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import RunRead, TaskCreate, TaskRead
from app.services.runner_service import run_task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.post("", response_model=TaskRead)
def create_task(task:TaskCreate,
    db:Session = Depends(get_db),):
    db_task = Task(
        title=task.title,
        description=task.description,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task



@router.get("", response_model=list[TaskRead])
def list_tasks(db:Session = Depends(get_db)):
    return db.query(Task).all()

@router.get("/{task_id}",response_model=TaskRead)
def read_task(task_id: int,db:Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/runs", response_model=RunRead)
def start_task_run(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    run = run_task(db, task)

    return run
