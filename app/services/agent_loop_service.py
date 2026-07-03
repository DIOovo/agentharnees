import json
from typing import Any
from sqlalchemy.orm import Session
from app.models import Run, RunStep,Task
from app.services.llm_client import llm_client
from app.services.prompt_service import build_tool_agent_user_prompt,build_tool_agent_system_prompt
from app.tools.registry import run_tool

MAX_AGENT_STEPS = 5

def parse_model_json(content:str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"模型输出不是合法 JSON：{content}") from e

def save_step(
        db:Session,
        run:Run,
        step_index:int,
        model_output:str,
        step_type:str,
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
        db:Session,task:Task,run:Run) -> str:
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

        parsed = parse_model_json(model_output)
        output_type = parsed.get("output_type")
        if output_type == "final":
            answer = parsed.get("answer","")
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
            tool_args = parsed.get("tool_args")
            tool_result = run_tool(
                name = tool_name,
                args = tool_args,
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
            conversation_context  += f"""
            上一步模型调用了工具：

            工具名：
            {tool_name}
            
            工具参数：
            {json.dumps(tool_args, ensure_ascii=False)}
            
            工具返回结果：
            {json.dumps(tool_result, ensure_ascii=False)}
            
            请继续判断下一步。
            如果信息足够，请输出 final。
            如果还需要工具，请继续输出 tool_call。
            """
            continue
        raise ValueError(f"未知模型输出类型：{output_type}")
    return "Agent 已达到最大执行步数，未能生成最终答案。"