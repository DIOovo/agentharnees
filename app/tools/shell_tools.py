from typing import Any

from app.sandbox.docker_runner import run_in_sandbox


ALLOWED_COMMAND_PREFIXES = (
    "pwd",
    "ls",
    "find",
    "cat",
    "sed",
    "grep",
    "python",
    "python3",
    "pytest",
)


def is_allowed_command(command: str) -> bool:
    stripped = command.strip()

    if not stripped:
        return False

    return stripped.startswith(ALLOWED_COMMAND_PREFIXES)


def run_shell_command(args: dict[str, Any]) -> dict[str, Any]:
    command = args.get("command")
    workdir = args.get("workdir", ".")
    timeout = args.get("timeout")

    if not command:
        return {
            "success": False,
            "error": "缺少 command 参数",
        }

    if not is_allowed_command(command):
        return {
            "success": False,
            "error": f"不允许执行该命令：{command}",
        }

    result = run_in_sandbox(
        command=command,
        relative_workdir=workdir,
        timeout=timeout,
    )

    result["command"] = command
    result["workdir"] = workdir
    result["summary"] = (
        "命令执行成功"
        if result.get("success")
        else "命令执行失败"
    )

    return result


def run_pytest(args: dict[str, Any]) -> dict[str, Any]:
    workdir = args.get("workdir", ".")
    timeout = args.get("timeout", 30)

    result = run_in_sandbox(
        command="pytest -q",
        relative_workdir=workdir,
        timeout=timeout,
    )

    result["command"] = "pytest -q"
    result["workdir"] = workdir
    result["summary"] = (
        "pytest 通过"
        if result.get("success")
        else "pytest 未通过"
    )

    return result