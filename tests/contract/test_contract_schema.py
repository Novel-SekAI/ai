import json
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from sekai_ai.schemas.contract import (
    GenerateRequestV1,
    GenerateSuccessResponse,
    GenerationRequestEnvelope,
    Worldview,
)

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures"


def load_fixture_object(name: str) -> dict[str, Any]:
    value = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a JSON object")
    return cast(dict[str, Any], value)


def test_brief_limit_uses_unicode_code_points() -> None:
    payload = load_fixture_object("generate_request_minimal_valid.json")
    payload["brief"] = "😀" * 5_000

    request = GenerateRequestV1.model_validate_json(json.dumps(payload, ensure_ascii=False))

    assert len(request.brief) == 5_000

    payload["brief"] = "😀" * 5_001
    with pytest.raises(ValidationError) as exc_info:
        GenerateRequestV1.model_validate_json(json.dumps(payload, ensure_ascii=False))

    assert ("brief",) in {tuple(error["loc"]) for error in exc_info.value.errors()}


def test_request_rejects_uuid_v4_field_under_snake_case_name() -> None:
    payload = load_fixture_object("generate_request_minimal_valid.json")
    payload["request_id"] = payload.pop("requestId")

    with pytest.raises(ValidationError) as exc_info:
        GenerateRequestV1.model_validate_json(json.dumps(payload, ensure_ascii=False))

    assert ("requestId",) in {tuple(error["loc"]) for error in exc_info.value.errors()}


def test_minimal_envelope_reads_version_and_request_id_from_full_request() -> None:
    raw = (FIXTURE_DIR / "generate_request_valid.json").read_text(encoding="utf-8")

    envelope = GenerationRequestEnvelope.model_validate_json(raw)

    assert envelope.schema_version == "1.0"
    assert envelope.request_id.version == 4


def test_worldview_rejects_snake_case_wire_field() -> None:
    response = load_fixture_object("generate_response_valid.json")
    worldview = cast(dict[str, Any], response["worldview"])
    worldview["relationships_by_era"] = worldview.pop("relationshipsByEra")

    with pytest.raises(ValidationError) as exc_info:
        GenerateSuccessResponse.model_validate_json(json.dumps(response, ensure_ascii=False))

    locations = {tuple(error["loc"]) for error in exc_info.value.errors()}
    assert ("worldview", "relationshipsByEra") in locations


def test_usage_requires_non_negative_strict_integers() -> None:
    response = load_fixture_object("generate_response_valid.json")
    usage = cast(dict[str, Any], response["usage"])
    usage["inputTokens"] = -1
    usage["outputTokens"] = True

    with pytest.raises(ValidationError) as exc_info:
        GenerateSuccessResponse.model_validate_json(json.dumps(response, ensure_ascii=False))

    locations = {tuple(error["loc"]) for error in exc_info.value.errors()}
    assert ("usage", "inputTokens") in locations
    assert ("usage", "outputTokens") in locations


def test_scalar_fields_reject_null_and_array_values() -> None:
    response = load_fixture_object("generate_response_valid.json")
    worldview = cast(dict[str, Any], response["worldview"])
    characters = cast(list[dict[str, Any]], worldview["characters"])
    factions = cast(list[dict[str, Any]], worldview["factions"])
    characters[0]["description"] = None
    factions[0]["role"] = ["지배 세력"]

    with pytest.raises(ValidationError) as exc_info:
        GenerateSuccessResponse.model_validate_json(json.dumps(response, ensure_ascii=False))

    locations = {tuple(error["loc"]) for error in exc_info.value.errors()}
    assert ("worldview", "characters", 0, "description") in locations
    assert ("worldview", "factions", 0, "role") in locations


def test_worldview_json_schema_uses_contract_aliases() -> None:
    schema = Worldview.model_json_schema(by_alias=True)
    properties = cast(dict[str, Any], schema["properties"])
    definitions = cast(dict[str, Any], schema["$defs"])
    character = cast(dict[str, Any], definitions["Character"])
    character_properties = cast(dict[str, Any], character["properties"])
    relationship = cast(dict[str, Any], definitions["Relationship"])
    relationship_properties = cast(dict[str, Any], relationship["properties"])

    assert "relationshipsByEra" in properties
    assert "factionRelationshipsByEra" in properties
    assert "relationships_by_era" not in properties
    assert "tempId" in character_properties
    assert "temp_id" not in character_properties
    assert "from" in relationship_properties
    assert "from_" not in relationship_properties


def test_all_output_models_forbid_additional_properties() -> None:
    schema = Worldview.model_json_schema(by_alias=True)
    definitions = cast(dict[str, Any], schema["$defs"])

    assert schema["additionalProperties"] is False
    for definition in definitions.values():
        model_schema = cast(dict[str, Any], definition)
        if "properties" in model_schema:
            assert model_schema["additionalProperties"] is False
