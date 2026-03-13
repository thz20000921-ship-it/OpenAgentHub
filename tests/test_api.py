from app.services.registry_service import RegistryService
from app.core.config import settings

class TestCoreEndpoints:
    def test_health_check(self, client):
        resp = client.get(f"{settings.API_V1_STR}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_dashboard_render(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "OpenAgentHub" in resp.text

class TestValidationAndRegistration:
    def test_register_invalid_endpoint_url_schema(self, client, api_key, sample_tool):
        bad_tool = sample_tool.copy()
        bad_tool["entry_point"] = "ftp://invalid-schema"
        
        resp = client.post(
            f"{settings.API_V1_STR}/tools/register",
            json=bad_tool,
            headers={"X-API-Key": api_key}
        )
        assert resp.status_code == 400
        assert "Invalid URL scheme" in resp.json()["detail"]

    def test_register_unreachable_endpoint(self, client, api_key, sample_tool):
        bad_tool = sample_tool.copy()
        bad_tool["entry_point"] = "http://fail-endpoint.com/api"
        
        resp = client.post(
            f"{settings.API_V1_STR}/tools/register",
            json=bad_tool,
            headers={"X-API-Key": api_key}
        )
        assert resp.status_code == 400
        assert "HTTP Error" in resp.json()["detail"]

    def test_register_successful(self, client, api_key, sample_tool):
        # httpx mock 默认返回 200
        resp = client.post(
            f"{settings.API_V1_STR}/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "test-agent"
        # 初始未经过后台异步 HealthCheck，所以默认还是 unknown
        assert data["status"] == "unknown"

class TestRegistrySearch:
    def test_search_by_tags_and_status(self, client, api_key, sample_tool):
        # 注册工具
        client.post(
            f"{settings.API_V1_STR}/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key}
        )
        
        # 强制将状态更新至 DB 中以模拟 HealthCheck 后台返回后的效果
        tool_db = RegistryService.get_tool_by_name(sample_tool["name"])
        import app.core.database as db
        conn = db.get_connection()
        conn.execute("UPDATE tools SET status = 'online' WHERE name = ?", (tool_db["name"],))
        conn.commit()
        conn.close()

        # 验证 search 过滤器
        resp = client.get(f"{settings.API_V1_STR}/tools", params={"tag": "demo", "status": "online"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["status"] == "online"
