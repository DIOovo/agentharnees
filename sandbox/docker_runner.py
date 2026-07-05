import subprocess
from pathlib import Path
from typing import Any

from app.core.config import settings


WORKSPACE_DIR = Path("workspace").resolve()


def truncate_text(text: str, limit: int = 8000) -> str:
    if len(text) <= limit:
        return text

    return text[-limit:]


def run_in_sandbox(
    command: str,
    relative_workdir: str = ".",
    timeout: int | None = None,
) -> dict[str, Any]:
    workdir_path = (WORKSPACE_DIR / relative_workdir).resolve()

    if not str(workdir_path).startswith(str(WORKSPACE_DIR)):
        return {
            "success": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "error": "不允许访问 workspace 之外的目录",
        }

    if not workdir_path.exists():
        return {
            "success": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "error": f"工作目录不存在：{relative_workdir}",
        }

    docker_command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--memory",
        settings.sandbox_memory,
        "--cpus",
        settings.sandbox_cpus,
        "-v",
        f"{workdir_path}:/workspace:ro",
        "-w",
        "/workspace",
        settings.sandbox_image,
        "sh",
        "-lc",
        command,
    ]

    try:
        completed = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=timeout or settings.sandbox_timeout,
        )

        return {
            "success": completed.returncode == 0,
            "exit_code": completed.returncode,
            "stdout": truncate_text(completed.stdout),
            "stderr": truncate_text(completed.stderr),
            "error": None,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "error": "命令执行超时",
        }

    except FileNotFoundError:
        return {
            "success": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "error": "未找到 docker 命令，请确认 Docker 已安装，并且 docker 命令已加入 PATH",
        }

    except Exception as exc:
        return {
            "success": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "error": str(exc),
        }