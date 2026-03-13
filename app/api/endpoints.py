from fastapi import APIRouter, HTTPException, Depends, Security, Query, BackgroundTasks
from fastapi.security import APIKeyHeader
from typing import List, Optional

from app.core.config import settings
from app.models.domain import ToolCreate, ToolResponse
from app.services.registry_service import RegistryService
from app.services.validation_service import validate_tool_endpoint
from app.services.healthcheck_service import check_single_tool, run_healthcheck_cycle

api_router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@api_router.get("/health", summary="System Health")
def system_health_check(background_tasks: BackgroundTasks):
    """触发全局后台健康检查周期并返回 ok"""
    background_tasks.add_task(run_healthcheck_cycle)
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}

@api_router.get("/tools", response_model=List[ToolResponse])
def get_tools(
    q: Optional[str] = Query(None, description="Search by name or description"),
    author: Optional[str] = Query(None, description="Filter by author"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    status: Optional[str] = Query(None, description="Filter by status (online, offline, timeout, invalid)")
):
    """获取所有工具，支持筛选与按最近状态排序"""
    tools = RegistryService.search_tools(q=q, author=author, tag=tag, status=status)
    return tools

@api_router.get("/tools/{tool_name}", response_model=ToolResponse)
def get_tool(tool_name: str):
    tool = RegistryService.get_tool_by_name(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return tool

@api_router.post("/tools/register", response_model=ToolResponse)
async def register_tool(
    tool: ToolCreate,
    background_tasks: BackgroundTasks,
    _: str = Depends(verify_api_key)
):
    """注册前包含连通性校验的网关注册"""
    is_valid, err_msg = await validate_tool_endpoint(tool.entry_point)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Endpoint validation failed: {err_msg}")
    
    saved_tool = RegistryService.insert_or_update_tool(tool)
    
    # 异步触发该新增节点的心跳查询以刷新其状态
    background_tasks.add_task(check_single_tool, tool.name, tool.entry_point)
    
    return saved_tool

@api_router.delete("/tools/{tool_name}")
def unregister_tool(tool_name: str, _: str = Depends(verify_api_key)):
    deleted = RegistryService.delete_tool(tool_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"status": "deleted", "name": tool_name}
