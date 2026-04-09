from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    loki_url: str = "http://localhost:3100"
    default_limit: int = 50
    max_limit: int = 200

    model_config = {"env_prefix": "LOKI_MCP_"}


settings = Settings()
