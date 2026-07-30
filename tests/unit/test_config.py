import pytest
from pydantic import ValidationError

from sekai_ai.core.config import Settings


def test_default_settings_use_one_pass() -> None:
    settings = Settings(_env_file=None)

    assert settings.pipeline_mode == "one_pass"
    assert settings.request_deadline_seconds == 115.0
    assert settings.rag_enabled is False
    assert settings.log_payloads is False


def test_environment_variables_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SEKAI_PIPELINE_MODE", "plan_then_generate")
    monkeypatch.setenv("SEKAI_REQUEST_DEADLINE_SECONDS", "90")

    settings = Settings(_env_file=None)

    assert settings.pipeline_mode == "plan_then_generate"
    assert settings.request_deadline_seconds == 90.0


@pytest.mark.parametrize("app_env", ["stage", "prod"])
def test_deployment_rejects_default_service_token(app_env: str) -> None:
    with pytest.raises(ValidationError):
        Settings(app_env=app_env, _env_file=None)


def test_production_accepts_explicit_secrets_and_model_revision() -> None:
    settings = Settings(
        app_env="prod",
        service_token="test-service-token",
        model_revision="0123456789abcdef",
        _env_file=None,
    )

    assert settings.app_env == "prod"
    assert settings.model_revision == "0123456789abcdef"


@pytest.mark.parametrize("deadline", [0, 120, 121])
def test_request_deadline_must_leave_backend_margin(deadline: float) -> None:
    with pytest.raises(ValidationError):
        Settings(request_deadline_seconds=deadline, _env_file=None)
