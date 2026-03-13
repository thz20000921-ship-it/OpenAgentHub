from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ToolCreate(BaseModel):
    """注册/更新工具请求体"""
    name: str = Field(..., min_length=1, max_length=128, examples=["issue-triage-agent"])
    version: str = Field(..., min_length=1, examples=["1.0.0"])
    description: str = Field(default="", examples=["Triages GitHub issues using AI"])
    author: str = Field(default="", examples=["open-source-dev"])
    tags: List[str] = Field(default=[], examples=[["github", "triage", "agent"]])
    entry_point: str = Field(..., examples=["https://api.example.com/triage"])

class ToolResponse(ToolCreate):
    """完整的工具数据模型"""
    created_at: Optional[str] = None
    status: str = Field(default="unknown", description="online, offline, timeout, invalid, unknown")
    last_checked_at: Optional[str] = None
    response_time_ms: Optional[int] = None
