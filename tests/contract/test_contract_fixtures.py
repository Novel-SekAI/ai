import json
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from sekai_ai.schemas.contract import (
    GenerateErrorResponse,
    GenerateRequestV1,
    GenerateSuccessResponse,
    ModelInfoResponse,
    Worldview,
)
from sekai_ai.schemas.json import validate_json_model

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def load_fixture_object(name: str) -> dict[str, Any]:
    value = json.loads(read_fixture(name))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a JSON object")
    return cast(dict[str, Any], value)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "generate_request_minimal_valid.json",
        "generate_request_valid.json",
    ],
)
def test_valid_request_fixtures_parse_and_round_trip(fixture_name: str) -> None:
    raw = read_fixture(fixture_name)

    request = GenerateRequestV1.model_validate_json(raw)

    assert request.model_dump(mode="json", by_alias=True, exclude_none=True) == json.loads(raw)


def test_valid_success_response_fixture_parses_and_round_trips() -> None:
    raw = read_fixture("generate_response_valid.json")

    response = validate_json_model(raw, GenerateSuccessResponse)

    assert response.model_dump(mode="json", by_alias=True, exclude_none=False) == json.loads(raw)


def test_valid_error_response_fixture_parses_and_round_trips() -> None:
    raw = read_fixture("generate_error_valid.json")

    response = validate_json_model(raw, GenerateErrorResponse)

    assert response.model_dump(mode="json", by_alias=True, exclude_none=False) == json.loads(raw)


def test_valid_model_info_fixture_parses_and_round_trips() -> None:
    raw = read_fixture("model_info_valid.json")

    response = validate_json_model(raw, ModelInfoResponse)

    assert response.model_dump(mode="json", by_alias=True, exclude_none=False) == json.loads(raw)


@pytest.mark.parametrize(
    ("fixture_name", "expected_location"),
    [
        ("generate_request_invalid_schema_version.json", ("schemaVersion",)),
        ("generate_request_invalid_uuid_version.json", ("requestId",)),
        ("generate_request_missing_options.json", ("options",)),
    ],
)
def test_invalid_request_fixtures_are_rejected(
    fixture_name: str,
    expected_location: tuple[str, ...],
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        GenerateRequestV1.model_validate_json(read_fixture(fixture_name))

    assert expected_location in {tuple(error["loc"]) for error in exc_info.value.errors()}


@pytest.mark.parametrize(
    ("fixture_name", "expected_location"),
    [
        (
            "worldview_invalid_relation.json",
            ("relationshipsByEra", "61년", 0, "relation"),
        ),
        ("worldview_missing_required_field.json", ("project", "summary")),
        ("worldview_extra_field.json", ("factions", 0, "members")),
        ("worldview_null_array.json", ("characters", 0, "groups")),
    ],
)
def test_invalid_worldview_fixtures_are_rejected(
    fixture_name: str,
    expected_location: tuple[str | int, ...],
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        Worldview.model_validate_json(read_fixture(fixture_name))

    assert expected_location in {tuple(error["loc"]) for error in exc_info.value.errors()}


@pytest.mark.parametrize(
    "fixture_name",
    [
        "worldview_duplicate_top_level_key.json",
        "worldview_duplicate_era_key.json",
        "worldview_duplicate_nested_key.json",
    ],
)
def test_duplicate_json_keys_are_rejected_before_model_validation(fixture_name: str) -> None:
    with pytest.raises(ValueError, match="duplicate JSON key"):
        validate_json_model(read_fixture(fixture_name), Worldview)


def test_request_ignores_unknown_minor_fields() -> None:
    payload = load_fixture_object("generate_request_minimal_valid.json")
    payload["schemaVersion"] = "1.99"
    payload["futureField"] = "ignored"
    options = cast(dict[str, Any], payload["options"])
    options["futureOption"] = True

    request = GenerateRequestV1.model_validate_json(json.dumps(payload, ensure_ascii=False))
    dumped = request.model_dump(mode="json", by_alias=True, exclude_none=True)

    assert request.schema_version == "1.99"
    assert "futureField" not in dumped
    assert "futureOption" not in cast(dict[str, Any], dumped["options"])


def test_output_rejects_unknown_nested_fields() -> None:
    payload = load_fixture_object("generate_response_valid.json")
    worldview = cast(dict[str, Any], payload["worldview"])
    project = cast(dict[str, Any], worldview["project"])
    project["unexpected"] = "not allowed"

    with pytest.raises(ValidationError) as exc_info:
        GenerateSuccessResponse.model_validate_json(json.dumps(payload, ensure_ascii=False))

    assert ("worldview", "project", "unexpected") in {
        tuple(error["loc"]) for error in exc_info.value.errors()
    }
