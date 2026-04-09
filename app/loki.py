import time

import httpx

from app.config import settings


async def _query_range(query: str, start: str, end: str, limit: int) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{settings.loki_url}/loki/api/v1/query_range",
            params={
                "query": query,
                "start": start,
                "end": end,
                "limit": limit,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def _query_instant(query: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{settings.loki_url}/loki/api/v1/query",
            params={"query": query},
        )
        resp.raise_for_status()
        return resp.json()


async def _get_labels(label: str) -> list[str]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.loki_url}/loki/api/v1/label/{label}/values",
        )
        resp.raise_for_status()
        return resp.json().get("data", [])


def _time_range(minutes: int) -> tuple[str, str]:
    end = int(time.time())
    start = end - minutes * 60
    return f"{start}000000000", f"{end}000000000"


def _format_logs(data: dict, include_labels: bool = False) -> list[dict]:
    results = []
    for stream in data.get("data", {}).get("result", []):
        labels = stream.get("stream", {})
        for ts, line in stream.get("values", []):
            entry = {"timestamp": ts, "message": line}
            if include_labels:
                entry["labels"] = labels
            results.append(entry)
    return results


def _format_stats(data: dict) -> list[dict]:
    results = []
    for item in data.get("data", {}).get("result", []):
        metric = item.get("metric", {})
        value = item.get("value", [None, "0"])
        results.append({**metric, "count": int(value[1])})
    results.sort(key=lambda x: x["count"], reverse=True)
    return results
