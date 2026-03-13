import json
from typing import List, Optional

from app.core.database import get_connection, row_to_dict
from app.models.domain import ToolCreate

class RegistryService:
    @staticmethod
    def get_all_tools() -> List[dict]:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM tools ORDER BY created_at DESC"
        )
        tools = [row_to_dict(row) for row in cursor.fetchall()]
        conn.close()
        return tools

    @staticmethod
    def get_tool_by_name(name: str) -> Optional[dict]:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM tools WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        conn.close()
        return row_to_dict(row) if row else None

    @staticmethod
    def insert_or_update_tool(tool: ToolCreate) -> dict:
        conn = get_connection()
        tags_json = json.dumps(tool.tags, ensure_ascii=False)
        conn.execute("""
            INSERT INTO tools (name, version, description, author, tags, entry_point)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                version = excluded.version,
                description = excluded.description,
                author = excluded.author,
                tags = excluded.tags,
                entry_point = excluded.entry_point,
                status = 'unknown'
        """, (
            tool.name, tool.version, tool.description, 
            tool.author, tags_json, tool.entry_point
        ))
        conn.commit()
        conn.close()
        return RegistryService.get_tool_by_name(tool.name)

    @staticmethod
    def delete_tool(name: str) -> bool:
        conn = get_connection()
        cursor = conn.execute("DELETE FROM tools WHERE name = ?", (name,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    @staticmethod
    def search_tools(
        q: Optional[str] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        conn = get_connection()
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
        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM tools WHERE {where_clause} ORDER BY last_checked_at DESC NULLS LAST, created_at DESC"

        cursor = conn.execute(query, params)
        tools = [row_to_dict(row) for row in cursor.fetchall()]
        conn.close()
        return tools
