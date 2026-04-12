# Architecture

## Overview

Loki MCP Server is a thin bridge between MCP-compatible AI clients and a Grafana Loki instance.
It translates structured tool calls into LogQL queries and returns formatted results.

## Components

```
MCP Client (Claude, etc.)
    |
    | SSE / HTTP
    v
FastAPI (app/main.py)
    |
    | mount "/"
    v
FastMCP (app/mcp_server.py)        app/config.py
    |  5 tools exposed              (Pydantic Settings)
    |
    v
Loki Client (app/loki.py)
    |
    | HTTP (httpx)
    v
Grafana Loki (:3100)
```

## Layers

1. **Transport** - FastAPI + FastMCP handle MCP protocol over SSE/HTTP
2. **Tools** - `mcp_server.py` defines 5 MCP tools with typed parameters and docstrings
3. **Client** - `loki.py` wraps Loki HTTP API (query_range, query, label values)
4. **Config** - `config.py` loads settings from env vars with `LOKI_MCP_` prefix

## MCP Tools

| Tool | Purpose |
|---|---|
| `query_logs` | Query logs by container/project with optional text search |
| `get_errors` | Filter for error/exception/fatal/traceback lines |
| `get_log_stats` | Log volume and error counts per container |
| `list_containers` | List all containers and compose projects in Loki |
| `search_logs` | Full-text keyword search across all logs |

## Data Flow

1. MCP client calls a tool (e.g. `query_logs(container="fusion-api", minutes=30)`)
2. Tool handler builds a LogQL selector and optional filter pipeline
3. `loki.py` sends HTTP GET to Loki's query_range or query endpoint
4. Response is parsed, formatted into `{timestamp, message}` entries
5. Tool returns structured dict with total count, query string, and log entries

## Deployment

- Docker container on dev server (192.168.1.10), port 8060
- Joins `prometheus-stack_default` network to reach Loki
- Memory limit: 192MB
- CI/CD: GitHub Actions self-hosted runner, auto-deploy on push to main
