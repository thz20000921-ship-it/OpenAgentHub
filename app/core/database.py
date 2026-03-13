import sqlite3
import json
from typing import Optional

from app.core.config import settings

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """获取数据库连接，启用 WAL 模式以支持并发"""
    db_path = db_path or settings.DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db(db_path: Optional[str] = None):
    """初始化数据库并创建包含健康检查字段的新 tools 表"""
    db_path = db_path or settings.DB_PATH
    conn = get_connection(db_path)
    # 增加 status, last_checked_at, response_time_ms
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            name TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            author TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            entry_point TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'unknown',
            last_checked_at TIMESTAMP,
            response_time_ms INTEGER
        )
    """)
    conn.commit()
    conn.close()

def row_to_dict(row: sqlite3.Row) -> dict:
    """内部转换工具"""
    if not row:
        return {}
    d = dict(row)
    d["tags"] = json.loads(d.get("tags", "[]"))
    return d
