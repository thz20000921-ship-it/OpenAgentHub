"""
OpenAgentHub API — 自动化测试

覆盖：健康检查、工具注册、列表、搜索、详情、删除、认证拦截。
"""


class TestHealthCheck:
    """健康检查端点测试"""

    def test_root_returns_ok(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "OpenAgentHub"


class TestToolRegistration:
    """工具注册端点测试"""

    def test_register_tool_with_valid_key(self, client, api_key, sample_tool):
        resp = client.post(
            "/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == sample_tool["name"]
        assert data["tags"] == ["search", "test"]

    def test_register_tool_without_key_returns_401(self, client, sample_tool):
        resp = client.post("/tools/register", json=sample_tool)
        assert resp.status_code == 401

    def test_register_tool_with_wrong_key_returns_401(self, client, sample_tool):
        resp = client.post(
            "/tools/register",
            json=sample_tool,
            headers={"X-API-Key": "wrong-key"},
        )
        assert resp.status_code == 401

    def test_register_updates_existing_tool(self, client, api_key, sample_tool):
        headers = {"X-API-Key": api_key}
        client.post("/tools/register", json=sample_tool, headers=headers)
        updated = {**sample_tool, "version": "2.0.0", "description": "Updated!"}
        resp = client.post("/tools/register", json=updated, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["version"] == "2.0.0"


class TestToolListing:
    """工具列表端点测试"""

    def test_list_tools_empty(self, client):
        resp = client.get("/tools")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_tools_after_registration(self, client, api_key, sample_tool):
        client.post(
            "/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key},
        )
        resp = client.get("/tools")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestToolSearch:
    """工具搜索端点测试"""

    def _register(self, client, api_key, tool):
        client.post("/tools/register", json=tool, headers={"X-API-Key": api_key})

    def test_search_by_keyword(self, client, api_key, sample_tool):
        self._register(client, api_key, sample_tool)
        resp = client.get("/tools/search", params={"q": "search"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_search_by_author(self, client, api_key, sample_tool):
        self._register(client, api_key, sample_tool)
        resp = client.get("/tools/search", params={"q": "", "author": "tester"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_search_by_tag(self, client, api_key, sample_tool):
        self._register(client, api_key, sample_tool)
        resp = client.get("/tools/search", params={"q": "", "tag": "test"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_search_no_results(self, client):
        resp = client.get("/tools/search", params={"q": "nonexistent"})
        assert resp.status_code == 200
        assert resp.json() == []


class TestToolDetails:
    """工具详情端点测试"""

    def test_get_existing_tool(self, client, api_key, sample_tool):
        client.post(
            "/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key},
        )
        resp = client.get(f"/tools/{sample_tool['name']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == sample_tool["name"]

    def test_get_nonexistent_tool_returns_404(self, client):
        resp = client.get("/tools/not-a-real-tool")
        assert resp.status_code == 404


class TestToolDeletion:
    """工具删除端点测试"""

    def test_delete_tool_with_valid_key(self, client, api_key, sample_tool):
        client.post(
            "/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key},
        )
        resp = client.delete(
            f"/tools/{sample_tool['name']}",
            headers={"X-API-Key": api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"
        # 确认已删除
        resp = client.get(f"/tools/{sample_tool['name']}")
        assert resp.status_code == 404

    def test_delete_without_key_returns_401(self, client, api_key, sample_tool):
        client.post(
            "/tools/register",
            json=sample_tool,
            headers={"X-API-Key": api_key},
        )
        resp = client.delete(f"/tools/{sample_tool['name']}")
        assert resp.status_code == 401

    def test_delete_nonexistent_returns_404(self, client, api_key):
        resp = client.delete(
            "/tools/not-a-real-tool",
            headers={"X-API-Key": api_key},
        )
        assert resp.status_code == 404
