"""
OpenAgentHub CLI — 命令行工具

用法:
    openagent list                    列出所有已注册的工具
    openagent search <query>          搜索工具
    openagent info <name>             查看工具详情
    openagent register                注册一个新工具
"""

import click
import httpx
import json
import sys

DEFAULT_SERVER = "http://localhost:8000"


def _get_client(server: str) -> httpx.Client:
    return httpx.Client(base_url=server, timeout=10.0)


def _print_tool(tool: dict):
    """格式化输出单个工具信息"""
    tags = ", ".join(tool.get("tags", [])) if tool.get("tags") else "none"
    click.echo(f"  📦 {click.style(tool['name'], fg='cyan', bold=True)}"
               f"  v{tool.get('version', '?')}")
    click.echo(f"     {tool.get('description', 'No description')}")
    click.echo(f"     Author: {tool.get('author', 'unknown')}  |  Tags: {tags}")
    click.echo(f"     Endpoint: {tool.get('entry_point', 'N/A')}")
    click.echo()


@click.group()
@click.option("--server", default=DEFAULT_SERVER, envvar="OPENAGENT_SERVER",
              help="OpenAgentHub API server URL")
@click.pass_context
def cli(ctx, server):
    """🚀 OpenAgentHub CLI — AI Agent 工具注册表客户端"""
    ctx.ensure_object(dict)
    ctx.obj["server"] = server


@cli.command()
@click.pass_context
def list(ctx):
    """列出所有已注册的工具"""
    try:
        client = _get_client(ctx.obj["server"])
        resp = client.get("/tools")
        resp.raise_for_status()
        tools = resp.json()
        if not tools:
            click.echo("📭 No tools registered yet.")
            return
        click.echo(f"\n🔧 Registered Tools ({len(tools)}):\n")
        for tool in tools:
            _print_tool(tool)
    except httpx.ConnectError:
        click.echo(f"❌ Cannot connect to server at {ctx.obj['server']}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--author", default=None, help="Filter by author")
@click.option("--tag", default=None, help="Filter by tag")
@click.pass_context
def search(ctx, query, author, tag):
    """搜索工具（按关键词、作者或标签）"""
    try:
        client = _get_client(ctx.obj["server"])
        params = {"q": query}
        if author:
            params["author"] = author
        if tag:
            params["tag"] = tag
        resp = client.get("/tools/search", params=params)
        resp.raise_for_status()
        tools = resp.json()
        if not tools:
            click.echo(f"🔍 No tools found for '{query}'")
            return
        click.echo(f"\n🔍 Search results for '{query}' ({len(tools)} found):\n")
        for tool in tools:
            _print_tool(tool)
    except httpx.ConnectError:
        click.echo(f"❌ Cannot connect to server at {ctx.obj['server']}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.pass_context
def info(ctx, name):
    """查看工具详情"""
    try:
        client = _get_client(ctx.obj["server"])
        resp = client.get(f"/tools/{name}")
        if resp.status_code == 404:
            click.echo(f"❌ Tool '{name}' not found")
            sys.exit(1)
        resp.raise_for_status()
        tool = resp.json()
        click.echo(f"\n📦 Tool Details:\n")
        _print_tool(tool)
    except httpx.ConnectError:
        click.echo(f"❌ Cannot connect to server at {ctx.obj['server']}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--name", prompt="Tool name", help="Tool name")
@click.option("--version", prompt="Version", help="Tool version")
@click.option("--description", prompt="Description", help="Tool description")
@click.option("--author", prompt="Author", help="Tool author")
@click.option("--tags", prompt="Tags (comma-separated)", default="", help="Comma-separated tags")
@click.option("--entry-point", prompt="Entry point URL", help="Tool API endpoint")
@click.option("--api-key", prompt="API Key", hide_input=True, help="API key for authentication")
@click.pass_context
def register(ctx, name, version, description, author, tags, entry_point, api_key):
    """注册一个新工具（需要 API Key）"""
    try:
        client = _get_client(ctx.obj["server"])
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        payload = {
            "name": name,
            "version": version,
            "description": description,
            "author": author,
            "tags": tag_list,
            "entry_point": entry_point,
        }
        resp = client.post(
            "/tools/register",
            json=payload,
            headers={"X-API-Key": api_key},
        )
        if resp.status_code == 401:
            click.echo("❌ Authentication failed: invalid API Key", err=True)
            sys.exit(1)
        resp.raise_for_status()
        click.echo(f"\n✅ Tool '{name}' registered successfully!\n")
        _print_tool(resp.json())
    except httpx.ConnectError:
        click.echo(f"❌ Cannot connect to server at {ctx.obj['server']}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
