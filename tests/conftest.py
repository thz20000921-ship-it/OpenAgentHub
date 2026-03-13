import os
import sys
import pytest
from httpx import AsyncClient

# 确保能找到源码目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.core.database import init_db
from app.api.server import app

@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    """隔离数据库，每个测试有自己的 db 文件"""
    db_path = str(tmp_path / "test.db")
    import app.core.config
    app.core.config.settings.DB_PATH = db_path
    init_db(db_path)
    return db_path

@pytest.fixture()
def api_key():
    import app.core.config
    key = "test-api-key-12345"
    app.core.config.settings.API_KEY = key
    return key

@pytest.fixture()
def client(api_key, temp_db):
    """测试客户端"""
    with TestClient(app) as c:
        yield c

@pytest.fixture()
def sample_tool():
    """测试用的合规合法工具"""
    return {
        "name": "test-agent",
        "version": "1.0.0",
        "description": "A demo agent",
        "author": "tester",
        "tags": ["demo", "test"],
        "entry_point": "http://localhost:9000/test"
    }

@pytest.fixture(autouse=True)
def mock_httpx(monkeypatch):
    """全局 Mock httpx.AsyncClient.get 以避免真实网络请求阻塞验证。"""
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code
        def raise_for_status(self):
            if self.status_code >= 400:
                from httpx import HTTPStatusError, Request
                raise HTTPStatusError("Error", request=Request("GET", "url"), response=self)

    async def mock_get(*args, **kwargs):
        url = args[1] if len(args) > 1 else args[0].args[0] if hasattr(args[0], 'args') else ""
        if isinstance(args[0], str): url = args[0]
        
        # 针对特定 URL 模拟错误
        if "fail-endpoint" in str(url):
            return MockResponse(404)
        if "network-error" in str(url):
            raise httpx.RequestError("Mocked network error")
            
        return MockResponse(200)

    # Mock validation_service and healthcheck_service httpx
    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
