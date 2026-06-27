from pydantic import BaseModel,ConfigDict
from pydantic.mypy import from_attributes_callback


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    status: str