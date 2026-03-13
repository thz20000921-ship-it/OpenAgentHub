import asyncio
import httpx
import time
from datetime import datetime

from app.core.database import get_connection
from app.services.registry_service import RegistryService

async def check_single_tool(name: str, entry_point: str):
    start_time = time.time()
    status = "offline"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(entry_point)
            if resp.status_code < 400:
                status = "online"
            else:
                status = "invalid"
    except httpx.TimeoutException:
        status = "timeout"
    except Exception:
        status = "offline"
        
    response_time_ms = int((time.time() - start_time) * 1000)
    now_str = datetime.utcnow().isoformat() + "Z"
    
    # Update DB
    conn = get_connection()
    conn.execute(
        "UPDATE tools SET status = ?, last_checked_at = ?, response_time_ms = ? WHERE name = ?",
        (status, now_str, response_time_ms, name)
    )
    conn.commit()
    conn.close()
    
    return status

async def run_healthcheck_cycle():
    """遍历所有注册的 tools，检查健康状态。该任务可被后台系统或者 API 端点触发。"""
    tools = RegistryService.get_all_tools()
    tasks = []
    for t in tools:
        tasks.append(check_single_tool(t["name"], t["entry_point"]))
    
    if tasks:
        # 并发执行检查
        await asyncio.gather(*tasks)
