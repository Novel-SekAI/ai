import json
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel


def reject_duplicate_keys(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_json_model[ModelT: BaseModel](raw: str, model_type: type[ModelT]) -> ModelT:
    """중복 키를 거절한 뒤 JSON 경계 규칙으로 Pydantic 모델을 검증한다."""

    json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    return model_type.model_validate_json(raw)
