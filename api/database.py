"""
OpenAgentHub — SQLite 数据库层

提供工具注册表的持久化存储，替代原有的 JSON 文件方案。
"""

import sqlite3
import os
import json
from typing import List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "openagent.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """获取数据库连接，启用 WAL 模式以支持并发读取"""
    db_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(db_path: Optional[str] = None):
    """初始化数据库，创建 tools 表（若不存在）"""
    db_path = db_path or DEFAULT_DB_PATH
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            version TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            author TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            entry_point TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """将数据库行转换为字典，tags 从 JSON 字符串还原为列表"""
    d = dict(row)
    d["tags"] = json.loads(d.get("tags", "[]"))
    return d


def get_all_tools(db_path: Optional[str] = None) -> List[dict]:
    """获取所有已注册工具"""
    conn = get_connection(db_path)
    cursor = conn.execute(
        "SELECT name, version, description, author, tags, entry_point, created_at FROM tools ORDER BY created_at DESC"
    )
    tools = [_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return tools


def get_tool_by_name(name: str, db_path: Optional[str] = None) -> Optional[dict]:
    """根据名称查询单个工具"""
    conn = get_connection(db_path)
    cursor = conn.execute(
        "SELECT name, version, description, author, tags, entry_point, created_at FROM tools WHERE name = ?",
        (name,)
    )
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def insert_or_update_tool(tool: dict, db_path: Optional[str] = None) -> dict:
    """插入或更新工具（基于 name 去重）"""
    conn = get_connection(db_path)
    tags_json = json.dumps(tool.get("tags", []), ensure_ascii=False)
    conn.execute("""
        INSERT INTO tools (name, version, description, author, tags, entry_point)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            version = excluded.version,
            description = excluded.description,
            author = excluded.author,
            tags = excluded.tags,
            entry_point = excluded.entry_point
    """, (
        tool["name"],
        tool["version"],
        tool.get("description", ""),
        tool.get("author", ""),
        tags_json,
        tool.get("entry_point", ""),
    ))
    conn.commit()
    conn.close()
    return get_tool_by_name(tool["name"], db_path)


def delete_tool(name: str, db_path: Optional[str] = None) -> bool:
    """删除指定名称的工具，返回是否删除成功"""
    conn = get_connection(db_path)
    cursor = conn.execute("DELETE FROM tools WHERE name = ?", (name,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def search_tools(
    q: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[dict]:
    """搜索工具：支持关键词（匹配 name/description）、按作者、按标签过滤"""
    conn = get_connection(db_path)
    conditions = []
    params = []

    if q:
        conditions.append("(name LIKE ? OR description LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    if author:
        conditions.append("author LIKE ?")
        params.append(f"%{author}%")
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f'%"{tag}"%')

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT name, version, description, author, tags, entry_point, created_at FROM tools WHERE {where_clause} ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    tools = [_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return tools
