"""
OpenAgentHub — FastAPI 核心服务

提供 AI Agent 工具的注册、发现、搜索与管理 API。
"""

import os
import secrets
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Security, Query
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from api.database import (
    init_db,
    get_all_tools,
    get_tool_by_name,
    insert_or_update_tool,
    delete_tool,
    search_tools,
)

# ---------------------------------------------------------------------------
# API Key 认证配置
# ---------------------------------------------------------------------------
# 可通过环境变量 OPENAGENT_API_KEY 设置，未设置时自动生成一个并输出到控制台
API_KEY = os.environ.get("OPENAGENT_API_KEY", "")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    print(f"\n🔑 Generated API Key (set OPENAGENT_API_KEY env var to override):\n   {API_KEY}\n")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """校验 API Key，写操作需要认证"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return api_key


# ---------------------------------------------------------------------------
# 应用生命周期
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时初始化数据库"""
    init_db()
    print("✅ Database initialized")
    yield


# ---------------------------------------------------------------------------
# FastAPI 应用实例
# ---------------------------------------------------------------------------
app = FastAPI(
    title="OpenAgentHub API",
    description="A lightweight AI Agent tool registry and marketplace — npm for AI agents.",
    version="2.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
class ToolCreate(BaseModel):
    """注册/更新工具时的请求体"""
    name: str = Field(..., min_length=1, max_length=128, examples=["web-scraper-agent"])
    version: str = Field(..., min_length=1, examples=["1.0.0"])
    description: str = Field(default="", examples=["An agent that scrapes web pages"])
    author: str = Field(default="", examples=["alice"])
    tags: List[str] = Field(default=[], examples=[["search", "web", "scraper"]])
    entry_point: str = Field(default="", examples=["http://localhost:9000/scrape"])


class ToolResponse(ToolCreate):
    """工具响应模型（附带时间戳）"""
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# 公开端点（无需认证）
# ---------------------------------------------------------------------------
@app.get("/")
def health_check():
    """服务健康检查"""
    return {"status": "ok", "service": "OpenAgentHub", "version": "2.0.0"}


@app.get("/tools", response_model=List[ToolResponse])
def list_tools():
    """列出所有已注册工具"""
    return get_all_tools()


@app.get("/tools/search", response_model=List[ToolResponse])
def search_tools_endpoint(
    q: Optional[str] = Query(None, description="关键词搜索（匹配名称和描述）"),
    author: Optional[str] = Query(None, description="按作者过滤"),
    tag: Optional[str] = Query(None, description="按标签过滤"),
):
    """搜索和过滤工具"""
    return search_tools(q=q, author=author, tag=tag)


@app.get("/tools/{tool_name}", response_model=ToolResponse)
def get_tool(tool_name: str):
    """获取特定工具的详细信息"""
    tool = get_tool_by_name(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return tool


# ---------------------------------------------------------------------------
# 受保护端点（需要 API Key）
# ---------------------------------------------------------------------------
@app.post("/tools/register", response_model=ToolResponse)
def register_tool(tool: ToolCreate, _: str = Depends(verify_api_key)):
    """注册新工具或更新现有工具（需要 API Key）"""
    result = insert_or_update_tool(tool.model_dump())
    return result


@app.delete("/tools/{tool_name}")
def remove_tool(tool_name: str, _: str = Depends(verify_api_key)):
    """删除指定工具（需要 API Key）"""
    deleted = delete_tool(tool_name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return {"status": "deleted", "name": tool_name}


# ---------------------------------------------------------------------------
# 本地开发入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
