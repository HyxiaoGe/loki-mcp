from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.mcp_server import mcp

mcp_app = mcp.http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(app):
        yield


app = FastAPI(title="Loki MCP Server", lifespan=lifespan)
app.mount("/", mcp_app)
