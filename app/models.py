from sqlalchemy import String, Text, Column
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship


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

class RunLog(Base):
    __tablename__ = 'run_logs'
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    task_id:Mapped[int] = mapped_column(ForeignKey("tasks.id"),nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    run: Mapped["Run"] = relationship(back_populates="logs")