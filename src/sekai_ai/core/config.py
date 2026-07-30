from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SEKAI_",
        extra="ignore",
    )

    app_env: Literal["local", "test", "stage", "prod"] = "local"
    pipeline_mode: Literal["one_pass", "plan_then_generate"] = "one_pass"

    schema_version: str = "1.0"
    model_id: str = "Qwen/Qwen3.5-9B"
    model_revision: str = "UNPINNED"
    adapter_id: str | None = None

    vllm_base_url: str = "http://127.0.0.1:8001/v1"
    vllm_api_key: SecretStr = SecretStr("EMPTY")
    service_token: SecretStr = SecretStr("local-only")

    request_deadline_seconds: float = Field(default=115.0, gt=0.0, lt=120.0)
    rag_enabled: bool = False
    log_payloads: bool = False

    @model_validator(mode="after")
    def validate_deployment_settings(self) -> Self:
        if self.app_env in {"stage", "prod"} and self.service_token.get_secret_value() in {
            "",
            "local-only",
        }:
            raise ValueError("stage/prod에서는 SEKAI_SERVICE_TOKEN을 설정해야 합니다")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
