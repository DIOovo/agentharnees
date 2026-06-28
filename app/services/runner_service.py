from datetime import datetime

from sqlalchemy.orm import Session
from tenacity import retry

from app.models import Run, RunLog, Task
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.llm_client import llm_client
from app.services.prompt_service import build_task_user_prompt,build_task_system_prompt


def add_log(
        db:Session,
        run_id:int,
        message:str,
        level: str = "info",
)->RunLog:
    log = RunLog(
        run_id = run_id,
        level = level,
        message = message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def run_task(
        db:Session,
        task:Task
)-> Run:
    run = Run(
        task_id = task.id,
        status = "running",
    )
    db.add(run)
    task.status = "running"
    db.commit()
    db.refresh(run)

    try:
        add_log(db,run.id,"开始执行任务")
        add_log(db,run.id,f"任务标题{task.title}")
        if task.description:
            add_log(db,run.id,f"任务表述{task.description}")

        system_prompt = build_task_system_prompt()
        user_prompt = build_task_user_prompt(task)

        add_log(db, run.id, "已构建 system prompt")
        add_log(db, run.id, "已构建 user prompt")
        add_log(db, run.id, "开始调用 LLM")
        result = llm_client.chat(
            system_prompt = system_prompt,
            user_prompt = user_prompt,
        )
        add_log(db, run.id, "LLM 调用完成")

        run.status = "success"
        run.result = result
        run.finished_at = datetime.now()
        task.status = "success"
        db.commit()
        db.refresh(run)
        add_log(db,run.id,"任务执行成功")
        return run
    except Exception as exc:
        run.status = "failed"
        run.error_message = str(exc)
        run.finished_at = datetime.now()
        task.status = "failed"
        db.commit()
        db.refresh(run)

        add_log(db, run.id, f"任务执行失败：{exc}", level="error")

        return run