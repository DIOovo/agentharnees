from typing import Any,Callable

ToolFunc = Callable[[dict[str,Any]], dict[str,Any]]

class Tool:
    def __init__(self,name:str,description:str,func:ToolFunc) -> None:
        self.name = name
        self.description = description
        self.func = func
    def run(self,args:dict[str,Any]) -> dict[str,Any]:
        return self.func(args)

