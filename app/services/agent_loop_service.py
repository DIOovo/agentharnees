import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import Run, RunStep, Task
from app.services.llm_client import llm_client
from app.services.prompt_service import (
    build_tool_agent_system_prompt,
    build_tool_agent_user_prompt,
)
from app.tools.registry import run_tool


MAX_AGENT_STEPS = 5


def parse_model_json(content: str) -> dict[str, Any]:
    cleaned = content.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1 and end > start:
            json_text = cleaned[start : end + 1]
            return json.loads(json_text)

        raise ValueError(f"模型输出不是合法 JSON：{content}")


def normalize_agent_output(parsed: dict[str, Any]) -> dict[str, Any]:
    if "type" in parsed:
        return parsed

    if "tool_name" in parsed:
        parsed["type"] = "tool_call"
        return parsed

    if "answer" in parsed:
        parsed["type"] = "final"
        return parsed

    return parsed


def save_step(
    db: Session,
    run: Run,
    step_index: int,
    model_output: str,
    step_type: str,
    tool_name: str | None = None,
    tool_args: dict | None = None,
    tool_result: dict | None = None,
    status: str = "success",
    error_message: str | None = None,
) -> RunStep:
    step = RunStep(
        run_id=run.id,
        step_index=step_index,
        model_output=model_output,
        step_type=step_type,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_result=tool_result,
        status=status,
        error_message=error_message,
    )

    db.add(step)
    db.commit()
    db.refresh(step)

    return step


def run_tool_agent(
    db: Session,
    task: Task,
    run: Run,
) -> str:
    system_prompt = build_tool_agent_system_prompt()

    conversation_context = build_tool_agent_user_prompt(
        task_title=task.title,
        task_description=task.description,
    )

    for step_index in range(1, MAX_AGENT_STEPS + 1):
        model_output = llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=conversation_context,
        )

        try:
            parsed = parse_model_json(model_output)
            parsed = normalize_agent_output(parsed)

        except Exception as exc:
            save_step(
                db=db,
                run=run,
                step_index=step_index,
                model_output=model_output,
                step_type="parse_error",
                status="failed",
                error_message=str(exc),
            )

            raise

        output_type = parsed.get("type")

        if output_type == "final":
            answer = parsed.get("answer", "")

            save_step(
                db=db,
                run=run,
                step_index=step_index,
                model_output=model_output,
                step_type="final",
            )

            return answer

        if output_type == "tool_call":
            tool_name = parsed.get("tool_name")
            tool_args = parsed.get("tool_args", {})

            tool_result = run_tool(
                name=tool_name,
                args=tool_args,
            )

            save_step(
                db=db,
                run=run,
                step_index=step_index,
                model_output=model_output,
                step_type="tool_call",
                tool_name=tool_name,
                tool_args=tool_args,
                tool_result=tool_result,
            )

            conversation_context += f"""

上一步模型调用了工具：

工具名：
{tool_name}

工具参数：
{json.dumps(tool_args, ensure_ascii=False)}

工具返回结果：
{json.dumps(tool_result, ensure_ascii=False)}

请继续判断下一步。

重要：
1. 如果信息足够，请输出 final。
2. 如果还需要工具，请继续输出 tool_call。
3. 输出必须是合法 JSON。
4. JSON 顶层必须包含 type 字段。
"""

            continue

        save_step(
            db=db,
            run=run,
            step_index=step_index,
            model_output=model_output,
            step_type="unknown",
            status="failed",
            error_message=f"未知模型输出类型：{output_type}，解析结果：{parsed}",
        )

        raise ValueError(f"未知模型输出类型：{output_type}")

    save_step(
        db=db,
        run=run,
        step_index=MAX_AGENT_STEPS + 1,
        model_output="",
        step_type="max_steps_reached",
        status="failed",
        error_message="Agent 已达到最大执行步数，未能生成最终答案。",
    )

    return "Agent 已达到最大执行步数，未能生成最终答案。"