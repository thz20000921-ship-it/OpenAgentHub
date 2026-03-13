import httpx
from typing import Tuple

async def validate_tool_endpoint(entry_point: str) -> Tuple[bool, str]:
    """
    验证工具注册时的 endpoint 是否可连通并返回基本响应
    Returns: Tuple[is_valid, error_reason]
    """
    if not entry_point.startswith("http://") and not entry_point.startswith("https://"):
        return False, "Invalid URL scheme. Must be http:// or https://"
    
    try:
        # 这里仅发起 GET 请求验证连通性
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(entry_point)
            response.raise_for_status()
            return True, ""
    except httpx.HTTPStatusError as e:
        return False, f"HTTP Error: {e.response.status_code}"
    except httpx.RequestError as e:
        return False, f"Network Error: {type(e).__name__}"
    except Exception as e:
        return False, f"Validation Error: {str(e)}"
