from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class CompatibleRequestModel(BaseModel):
    """동일 MAJOR의 새 MINOR 필드를 허용하는 외부 요청 모델."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="ignore",
        serialize_by_alias=True,
        strict=True,
        validate_by_alias=True,
        validate_by_name=False,
    )


class StrictOutputModel(BaseModel):
    """계약에 없는 필드를 거절하는 AI 출력 모델."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="forbid",
        serialize_by_alias=True,
        strict=True,
        validate_by_alias=True,
        validate_by_name=False,
    )
