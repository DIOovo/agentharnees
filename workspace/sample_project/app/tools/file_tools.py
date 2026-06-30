from pathlib import Path
from typing import Any

from pydantic.v1 import PathError

WORKSPACE_DIR = Path("workspace").resolve()

def safe_resolve_path(path:str) -> Path:
    target_path = (WORKSPACE_DIR / path).resolve()

    if not str(target_path).startswith(str(WORKSPACE_DIR)):
        raise ValueError("不允许访问 workspace 以外的路径")
    return target_path

def list_files(args:dict[str,Any]) -> dict[str,Any]:
    path = args.get("path","")
    target_path = safe_resolve_path(path)
    if not target_path.exists():
        return {
            "success": False,
            "error":f"路径不存在{path}"
        }
    if not target_path.is_dir():
        return {
            "success": False,
            "error": f"不是目录：{path}",
        }
    files = []
    for item in target_path.iterdir():
        files.append(
            {
                "name": item.name,
                "path": str(item.relative_to(target_path)),
                "type":"directory" if item.is_dir() else "file"
            }
        )
    return {
        "success": True,
        "path": path,
        "files": files,
    }


def read_file(args: dict[str, Any]) -> dict[str, Any]:
    path = args.get("path")
    if not path:
        return {
            "success": False,
            "error": "缺少 path 参数",
        }

    target_path = safe_resolve_path(path)

    if not target_path.exists():
        return {
            "success": False,
            "error": f"文件不存在：{path}",
        }

    if not target_path.is_file():
        return {
            "success": False,
            "error": f"不是文件：{path}",
        }

    content = target_path.read_text(encoding="utf-8")
    return {
        "success": True,
        "path": path,
        "content": content[:8000],
        "truncated": len(content) > 8000,

    }

def get_project_tree(args: dict[str,Any]) -> dict[str,Any]:
    path = args.get("path",'.')
    max_depth = int(args.get("max_depth",3))
    target_path = safe_resolve_path(path)
    if not path.exists():
        return {
            "success": False,
            "error":"路径不存在"
        }
    lines = list[str] = []
    def walk(current_path:Path,depth:int) -> None:
        if depth > max_depth:
            return
        indent = "   "*depth
        lines.append(f"{indent}{current_path.name}/"if current_path.is_dir() else f"{indent}{current_path.name}")
        if current_path.is_dir():
            for child in sorted(current_path.iterdir()):
                if child.name in {"__pycache__", ".git", ".idea"}:
                    continue
                walk(child, depth+1)
    walk(target_path, 0)
    return {
        "success": True,
        "path": path,
        "tree": "\n".join(lines),
    }
