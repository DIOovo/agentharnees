from fastapi import APIRouter,Depends
from app.schemas import TaskCreate, TaskRead
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskRead

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