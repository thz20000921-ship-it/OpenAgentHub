"""
Pytest conftest — 共享测试 fixtures
"""

import os
import sys
import pytest
import tempfile

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.database import init_db


@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    """为每个测试创建临时数据库"""
    db_path = str(tmp_path / "test.db")
    import api.database
    api.database.DEFAULT_DB_PATH = db_path
    init_db(db_path)
    return db_path


@pytest.fixture()
def api_key(monkeypatch):
    """设置已知的测试 API Key"""
    key = "test-api-key-12345"
    monkeypatch.setattr("api.server.API_KEY", key)
    return key


@pytest.fixture()
def client(api_key, temp_db):
    """获取 FastAPI TestClient"""
    from api.server import app
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sample_tool():
    """示例工具数据"""
    return {
        "name": "test-search-agent",
        "version": "1.0.0",
        "description": "A test agent for searching",
        "author": "tester",
        "tags": ["search", "test"],
        "entry_point": "http://localhost:9000/search",
    }
