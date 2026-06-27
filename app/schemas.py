from pydantic import BaseModel,ConfigDict
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    status: str

class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    status: str
    result: str | None = None
    error_message: str | None = None
    created_at: datetime
    finished_at: datetime | None = None


class RunLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    level: str
    message: str
    created_at: datetime