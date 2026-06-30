from app.tools.base import Tool
from app.tools.file_tools import get_project_tree,list_files,read_file

TOOLS: dict[str,Tool] = {
    "list_files":Tool(
        name="list_files",
        func=list_files,
        description="列出目录下的文件和文件夹"
    ),
    "read_file":Tool(
        name="read_file",
        func=read_file,
        description="读取文本文件内容"
    ),
    "get_project_tree":Tool(
        name="get_project_tree",
        func=get_project_tree,
        description="查看项目目录树"
    )
}

def get_tool(name:str) -> Tool|None:
    return TOOLS.get(name)

def run_tool(name:str,args:dict):
    tool = get_tool(name)
    if tool is None:
        return {
            "success": False,
            "error": f"未知工具：{name}",
        }
    try:
        return tool.run(args)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }



