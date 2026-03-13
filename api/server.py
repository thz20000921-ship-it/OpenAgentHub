import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="OpenAgentHub API",
    description="A lightweight AI Agent tool registry and marketplace.",
    version="1.0.0"
)

# 计算 registry.json 的绝对路径：server.py 位于 api/ 目录下，registry.json 在其上一层
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")

class Tool(BaseModel):
    name: str
    version: str
    description: str
    author: str
    entry_point: str

def load_registry() -> dict:
    """从本地 JSON 文件读取注册表数据"""
    if not os.path.exists(REGISTRY_FILE):
        return {"tools": []}
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading registry: {e}")
        return {"tools": []}

def save_registry(data: dict):
    """将数据持久化保存到本地 JSON 文件"""
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to OpenAgentHub API"}

@app.get("/tools", response_model=List[Tool])
def list_tools():
    """列出注册表中现有的所有工具"""
    registry = load_registry()
    return registry.get("tools", [])

@app.post("/tools/register", response_model=Tool)
def register_tool(tool: Tool):
    """注册一个新的工具，如果同名工具已存在则进行更新操作"""
    registry = load_registry()
    tools = registry.get("tools", [])
    
    # 查找是否已经存在同名工具
    for i, t in enumerate(tools):
        if t["name"] == tool.name:
            tools[i] = tool.model_dump()
            save_registry(registry)
            return tool
            
    # 不存在则新增
    tools.append(tool.model_dump())
    registry["tools"] = tools
    save_registry(registry)
    return tool

@app.get("/tools/{tool_name}", response_model=Tool)
def get_tool(tool_name: str):
    """根据工具名称查询特定工具详情"""
    registry = load_registry()
    tools = registry.get("tools", [])
    for t in tools:
        if t["name"] == tool_name:
            return t
    raise HTTPException(status_code=404, detail="Tool not found")

if __name__ == "__main__":
    import uvicorn
    # 为了方便本地独立运行测试，可通过 python api/server.py 启动
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
