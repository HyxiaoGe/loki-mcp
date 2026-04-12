# Loki MCP Server

MCP (Model Context Protocol) server that exposes Loki log queries as AI-callable tools.
Lets Claude and other MCP clients search Docker container logs without SSH access.

## Architecture

Single-package FastAPI app mounting a FastMCP server:

- `app/main.py` - FastAPI entrypoint, mounts MCP app at `/`
- `app/mcp_server.py` - FastMCP tool definitions (query_logs, get_errors, get_log_stats, list_containers, search_logs)
- `app/loki.py` - Loki HTTP API client (query_range, query_instant, label values, formatters)
- `app/config.py` - Pydantic Settings with `LOKI_MCP_` env prefix

## Key Constraints

- Python 3.12+, FastAPI + FastMCP + httpx
- All Loki queries go through httpx async client (no SDK)
- Max log limit enforced via `settings.max_limit` (200)
- Runs on port 8060
- Connects to Loki via `LOKI_MCP_LOKI_URL` env var (default `http://localhost:3100`)
- Deployed on dev server (192.168.1.10), connects to Loki on shared `prometheus-stack_default` network

## Dev Commands

```bash
# Run locally
uv run uvicorn app.main:app --host 0.0.0.0 --port 8060

# Lint & format
ruff check --fix .
ruff format .

# Docker
docker compose up -d --build
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LOKI_MCP_LOKI_URL` | `http://localhost:3100` | Loki base URL |
| `LOKI_MCP_DEFAULT_LIMIT` | `50` | Default log line limit |
| `LOKI_MCP_MAX_LIMIT` | `200` | Hard max log line limit |

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed architecture and data flow
- [docs/CODING_CONVENTIONS.md](docs/CODING_CONVENTIONS.md) - Code style and project conventions
