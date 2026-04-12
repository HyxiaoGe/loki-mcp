# Coding Conventions

## Stack

- Python 3.12+
- FastAPI + FastMCP for MCP server
- httpx for async HTTP calls to Loki
- pydantic-settings for configuration
- uv for dependency management

## Style

- Linter: ruff with rules `E, F, I, UP, B, SIM`
- Formatter: ruff format, 120 char line length
- Ignored rules: `E501` (line length handled by formatter), `B008` (FastAPI Depends)
- Run before commit: `ruff check --fix . && ruff format .`

## Project Structure

```
app/
  __init__.py
  main.py          # FastAPI app creation and lifespan
  mcp_server.py    # MCP tool definitions
  loki.py          # Loki HTTP client and formatters
  config.py        # Settings from environment
```

## Conventions

- All Loki HTTP calls use `httpx.AsyncClient` with explicit timeouts
- Private helper functions prefixed with `_` (e.g. `_query_range`, `_format_logs`)
- MCP tools are public functions decorated with `@mcp.tool()`
- Tool docstrings follow Google-style Args format (FastMCP uses these for schema)
- Settings accessed via module-level `settings` singleton from `config.py`
- Environment variables use `LOKI_MCP_` prefix

## Adding a New Tool

1. If it needs a new Loki API call, add it to `loki.py`
2. Add the tool function in `mcp_server.py` with `@mcp.tool()` decorator
3. Include a clear docstring with Args section (MCP clients show this to the AI)
4. Use typed parameters with defaults where sensible
5. Return a dict with structured data (not raw strings)

## Docker

- Base image: `python:3.12-slim`
- Uses uv for dependency install (no pip)
- Port 8060
