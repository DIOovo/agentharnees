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

class RunStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    step_index: int
    model_output: str | None = None
    step_type: str
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_result: dict | None = None
    status: str
    error_message: str | None = None
    created_at: datetime

class RunLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    level: str
    message: str
    created_at: datetime

class EvalRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    runner_mode: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    success_rate: float
    status: str
    created_at: datetime
    finished_at: datetime | None = None


class EvalResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eval_run_id: int
    task_id: int | None = None
    run_id: int | None = None
    case_name: str
    title: str
    passed: bool
    validator_type: str
    expected: str | None = None
    actual: str | None = None
    error_message: str | None = None
    created_at: datetime