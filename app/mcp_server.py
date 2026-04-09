from fastmcp import FastMCP

from app.config import settings
from app.loki import (
    _format_logs,
    _format_stats,
    _get_labels,
    _query_instant,
    _query_range,
    _time_range,
)

mcp = FastMCP(
    name="loki",
    instructions=(
        "Loki log query server. Use these tools to search and analyze "
        "Docker container logs without SSH access."
    ),
)


@mcp.tool()
async def query_logs(
    container: str | None = None,
    project: str | None = None,
    search: str | None = None,
    minutes: int = 30,
    limit: int = 50,
) -> dict:
    """Query container logs from Loki.

    Args:
        container: Container name to filter (e.g. "fusion-api"). None for all.
        project: Compose project name to filter (e.g. "fusion"). None for all.
        search: Text to search for in log lines. None for no filter.
        minutes: How many minutes of logs to look back. Default 30.
        limit: Max number of log lines to return. Default 50.
    """
    limit = min(limit, settings.max_limit)
    selector = _build_selector(container, project)
    query = f"{selector}"
    if search:
        query += f' |= `{search}`'
    start, end = _time_range(minutes)
    data = await _query_range(query, start, end, limit)
    logs = _format_logs(data)
    return {"total": len(logs), "query": query, "logs": logs}


@mcp.tool()
async def get_errors(
    container: str | None = None,
    project: str | None = None,
    minutes: int = 30,
    limit: int = 50,
) -> dict:
    """Get error and exception logs from containers.

    Args:
        container: Container name to filter. None for all.
        project: Compose project name to filter. None for all.
        minutes: How many minutes to look back. Default 30.
        limit: Max number of error lines to return. Default 50.
    """
    limit = min(limit, settings.max_limit)
    selector = _build_selector(container, project)
    query = f'{selector} |~ "(?i)error|exception|fatal|traceback" !~ "level=info"'
    start, end = _time_range(minutes)
    data = await _query_range(query, start, end, limit)
    logs = _format_logs(data, include_labels=True)
    return {"total": len(logs), "query": query, "logs": logs}


@mcp.tool()
async def get_log_stats(
    minutes: int = 60,
) -> dict:
    """Get log volume and error count statistics per container.

    Args:
        minutes: Time range in minutes for statistics. Default 60.
    """
    interval = f"{minutes}m"

    volume_query = f'sum by (container) (count_over_time({{container=~".+"}} [{interval}]))'
    volume_data = await _query_instant(volume_query)
    volumes = _format_stats(volume_data)

    error_query = (
        f'sum by (container) (count_over_time({{container=~".+"}} '
        f'|~ "(?i)error|exception|fatal" !~ "level=info" [{interval}]))'
    )
    error_data = await _query_instant(error_query)
    errors = _format_stats(error_data)

    return {
        "time_range_minutes": minutes,
        "log_volume_by_container": volumes,
        "error_count_by_container": errors,
    }


@mcp.tool()
async def list_containers() -> dict:
    """List all containers and compose projects that Loki is collecting logs from."""
    containers = await _get_labels("container")
    projects = await _get_labels("compose_project")
    return {"containers": containers, "projects": projects}


@mcp.tool()
async def search_logs(
    keyword: str,
    container: str | None = None,
    project: str | None = None,
    minutes: int = 60,
    limit: int = 50,
) -> dict:
    """Full-text search across all container logs.

    Args:
        keyword: The keyword or phrase to search for (required).
        container: Container name to filter. None for all.
        project: Compose project name to filter. None for all.
        minutes: How many minutes to look back. Default 60.
        limit: Max number of matching lines to return. Default 50.
    """
    limit = min(limit, settings.max_limit)
    selector = _build_selector(container, project)
    query = f'{selector} |= `{keyword}`'
    start, end = _time_range(minutes)
    data = await _query_range(query, start, end, limit)
    logs = _format_logs(data, include_labels=True)
    return {"total": len(logs), "keyword": keyword, "query": query, "logs": logs}


def _build_selector(container: str | None, project: str | None) -> str:
    filters = []
    if container:
        filters.append(f'container="{container}"')
    else:
        filters.append('container=~".+"')
    if project:
        filters.append(f'compose_project="{project}"')
    return "{" + ", ".join(filters) + "}"
