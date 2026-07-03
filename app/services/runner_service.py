from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Run, RunLog, Task
from app.core.config import settings
from app.services.agent_loop_service import run_tool_agent
from app.services.llm_client import llm_client
from app.services.prompt_service import build_task_system_prompt, build_task_user_prompt

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

def create_run(
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
    return run

def finish_run_success(
        db:Session,
        task:Task,
        run:Run,
        result:str,
) -> Run:
    run.status = "success"
    run.result = result
    run.finished_at = datetime.now()
    task.status = "success"
    db.commit()
    db.refresh(run)
    add_log(db, run.id, "任务执行成功")
    return run

def finish_run_failure(
        db:Session,
        task:Task,
        run:Run,
        error_message:str,
) -> Run:
    run.status = "failed"
    run.error_message = error_message
    run.finished_at = datetime.now()
    task.status = "failed"
    db.commit()
    db.refresh(run)

    add_log(db, run.id, f"任务执行失败：{error_message}", level="error")

    return run

def run_task_with_llm(
        db:Session,
        task:Task,
        run:Run,
) -> Run:
    add_log(db, run.id, f"LLM_BASE_URL：{settings.llm_base_url}")
    add_log(db, run.id, f"LLM_MODEL：{settings.llm_model}")
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
    run = finish_run_success(
        db=db,
        task=task,
        run=run,
        result=result,
    )
    add_log(db, run.id, "LLM Runner 执行成功")
    return run

def run_task_with_fake(
        db:Session,
        task:Task,
        run:Run,
) -> Run:
    add_log(db, run.id, "使用 Fake Runner 执行任务")
    add_log(db, run.id, f"任务标题：{task.title}")

    result = f"任务 `{task.title}` 已由 Fake Runner 执行完成。"

    run = finish_run_success(
        db = db,
        task = task,
        run = run,
    result = result,)
    add_log(db,run.id,"Fake Runner 执行成功")
    return run


def run_task(
        db:Session,
        task:Task,
) -> Run:
    run = create_run(db,task)
    try:
        if settings.runner_mode == "llm":
            return run_task_with_llm(db,task,run)
        if settings.runner_mode == "tool_agent":
            return run_task_with_tool_agent(db,task,run)
        return run_task_with_fake(db,task,run)
    except Exception as exc:
        run = finish_run_failure(
            db=db,
            task=task,
            run=run,
            error_message=str(exc),
        )
        return run

def run_task_with_tool_agent(
        db:Session,
        task:Task,
        run:Run,
) -> Run:
    add_log(db, run.id, "使用 Tool Agent Runner 执行任务")
    add_log(db, run.id, f"任务标题：{task.title}")
    result = run_tool_agent(
        db = db,
        task = task,
        run = run,
    )
    run = finish_run_success(
        db = db,
        task = task,
        run = run,
        result = result,
    )
    add_log(db,run.id,"Tool Agent Runner 执行完成")
    return run
