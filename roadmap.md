# OpenAgentHub Roadmap

The development of OpenAgentHub is guided by three distinct phases aimed at building a robust, enterprise-ready registry for AI agents.

## Phase 1: Foundation (v0.1) - Current
- **Registry & Storage:** Core registry functionality backed by SQLite.
- **Search & Discovery:** basic filtering by tags, author, and keywords.
- **CLI Tool:** Developer-friendly terminal interface for managing agents.
- **Health Check Infrastructure:** Basic endpoint ping logic and status recording.

## Phase 2: Platform Maturation (v0.2)
- **Web Dashboard:** A visual interface for managing and discovering agent endpoints.
- **Tool Validation:** Strict validation rules during the registration phase, evaluating schema and live endpoint connectivity.
- **Tagging & Advanced Filtering:** Extensive categorization logic grouping agents by capabilities (e.g., RAG, Code-Gen, External-API).
- **Usage Logs & Analytics:** Basic metrics on health check historical uptime and system latency.

## Phase 3: Enterprise & Ecosystem (v0.3)
- **Auth Roles & Multi-tenant:** Differentiate between admin maintainers and standard users.
- **Plugin Architecture:** Support for pluggable storage backends (PostgreSQL, Redis) and custom health-check probes.
- **MCP-compatible Metadata:** Full interoperability with the Model Context Protocol (MCP), enriching agent context delivery.
- **External Registry Sync:** Ability to federate and sync tools across multiple internal network registries.
