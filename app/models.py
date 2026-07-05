from sqlalchemy import String, Text, Column
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import JSON
from sqlalchemy import Float

class Task(Base):
    __tablename__ = 'tasks'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    title:Mapped[str] = mapped_column(String(200),nullable=False)
    description:Mapped[str | None] = mapped_column(Text,nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    runs: Mapped[list["Run"]] = relationship(
        back_populates="task",
        cascade="all,delete-orphan",
    )

class Run(Base):
    __tablename__ = 'runs'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    task_id:Mapped[int] = mapped_column(ForeignKey("tasks.id"),nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="running")
    result: Mapped[str | None] = mapped_column(Text,nullable=True)
    error_message:Mapped[str | None] = mapped_column(Text,nullable=True)
    created_at:Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow())
    finished_at:Mapped[datetime] = mapped_column(DateTime,nullable=True)
    task: Mapped["Task"] = relationship(back_populates="runs")
    logs: Mapped[list["RunLog"]] = relationship(
        back_populates="run",
        cascade="all,delete-orphan",
    )
    steps: Mapped[list["RunStep"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )

class RunLog(Base):
    __tablename__ = 'run_logs'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    run_id:Mapped[int] = mapped_column(ForeignKey("runs.id"),nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    run: Mapped["Run"] = relationship(back_populates="logs")


class RunStep(Base):
    __tablename__ = 'run_steps'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    run_id:Mapped[int] = mapped_column(ForeignKey("runs.id"),nullable=False)
    step_index:Mapped[int] = mapped_column(Integer,nullable=False)
    model_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    tool_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_args: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tool_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    run: Mapped["Run"] = relationship(back_populates="steps")

class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    runner_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="running")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    results: Mapped[list["EvalResult"]] = relationship(
        back_populates="eval_run",
        cascade="all, delete-orphan",
    )


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    eval_run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id"), nullable=True)

    case_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    passed: Mapped[bool] = mapped_column(default=False)
    validator_type: Mapped[str] = mapped_column(String(100), nullable=False)
    expected: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    eval_run: Mapped["EvalRun"] = relationship(back_populates="results")