import asyncio
from app.core.database import init_db
from app.models.domain import ToolCreate
from app.services.registry_service import RegistryService

SEED_TOOLS = [
    {
        "name": "github-pr-review-agent",
        "version": "1.2.0",
        "description": "Automatically reviews GitHub Pull Requests for security and style issues using LLM.",
        "author": "open-devtools",
        "tags": ["github", "review", "security", "code"],
        "entry_point": "https://api.example.com/agents/pr-review"
    },
    {
        "name": "issue-triage-agent",
        "version": "0.9.5",
        "description": "Triages incoming issues, adds labels, and assigns to relevant maintainers.",
        "author": "open-devtools",
        "tags": ["github", "triage", "automation"],
        "entry_point": "https://api.example.com/agents/triage"
    },
    {
        "name": "weather-query-agent",
        "version": "2.1.0",
        "description": "Provides real-time weather information and forecasts for given locations.",
        "author": "weather-ai",
        "tags": ["weather", "utility", "search"],
        "entry_point": "https://api.example.com/agents/weather"
    },
    {
        "name": "sql-query-agent",
        "version": "3.0.0",
        "description": "Translates natural language questions into executable SQL queries for Postgres/MySQL.",
        "author": "data-team",
        "tags": ["database", "sql", "data-analytics"],
        "entry_point": "https://api.example.com/agents/sql"
    },
    {
        "name": "document-search-agent",
        "version": "1.5.0",
        "description": "Semantic search agent for internal documentation and knowledge bases.",
        "author": "enterprise-ai",
        "tags": ["RAG", "search", "docs"],
        "entry_point": "https://api.example.com/agents/doc-search"
    },
    {
        "name": "code-security-scan-agent",
        "version": "1.0.1",
        "description": "SAST scanning agent that detects vulnerabilities in source code.",
        "author": "sec-ops",
        "tags": ["security", "SAST", "code"],
        "entry_point": "https://api.example.com/agents/sec-scan"
    }
]

def run_seed():
    print("Initializing Database...")
    init_db()
    
    print(f"Seeding {len(SEED_TOOLS)} tools...")
    for data in SEED_TOOLS:
        tool = ToolCreate(**data)
        RegistryService.insert_or_update_tool(tool)
        print(f"✅ Pre-registered: {tool.name}")
        
    print("Seed complete. You can now start the server and run health checks.")

if __name__ == "__main__":
    run_seed()
