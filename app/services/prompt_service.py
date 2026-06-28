from app.models import Task

def build_task_system_prompt() -> str:
    return """
    你是一个 Agent 任务执行助手。

你的任务是根据用户提供的任务标题和任务描述，输出一份清晰、具体、可执行的分析结果。

要求：
1. 不要编造不存在的文件、接口或执行结果。
2. 如果信息不足，要明确说明缺少什么。
3. 输出要结构清楚。
4. 优先使用中文。
        """.strip()

def build_task_user_prompt(task: Task) -> str:
    description = task.description or "无"

    return f"""
请执行下面这个任务：

任务 ID：{task.id}
任务标题：{task.title}
任务描述：{description}

请输出：
1. 你对任务的理解
2. 执行这个任务需要哪些步骤
3. 当前能给出的结果
4. 如果信息不足，还需要用户补充什么
""".strip()