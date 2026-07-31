from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import UUID4, Field

from sekai_ai.schemas.base import CompatibleRequestModel, StrictOutputModel

SchemaVersion = Annotated[str, Field(pattern=r"^[0-9]+\.[0-9]+$")]
Brief = Annotated[str, Field(max_length=5_000)]
NonNegativeInt = Annotated[int, Field(ge=0)]


class GenerationHints(CompatibleRequestModel):
    title: str | None = None
    genre: str | None = None


class GenerationOptions(CompatibleRequestModel):
    language: str
    model_version: str | None = None


class GenerationRequestEnvelope(CompatibleRequestModel):
    schema_version: SchemaVersion
    request_id: UUID4


class GenerateRequestV1(CompatibleRequestModel):
    schema_version: SchemaVersion
    request_id: UUID4
    brief: Brief
    hints: GenerationHints | None = None
    options: GenerationOptions


class RelationType(StrEnum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"


class Project(StrictOutputModel):
    title: str
    genre: str
    summary: str


class Character(StrictOutputModel):
    temp_id: str
    name: str
    role: str
    groups: list[str]
    tags: list[str]
    description: str


class Relationship(StrictOutputModel):
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    relation: RelationType
    summary: str


class Faction(StrictOutputModel):
    temp_id: str
    name: str
    role: str
    tags: list[str]
    description: str


class Law(StrictOutputModel):
    markdown: str


class TimelineEvent(StrictOutputModel):
    era: str
    title: str
    desc: str


class Worldview(StrictOutputModel):
    project: Project
    eras: list[str]
    characters: list[Character]
    relationships_by_era: dict[str, list[Relationship]]
    factions: list[Faction]
    faction_relationships_by_era: dict[str, list[Relationship]]
    law: Law
    timeline: list[TimelineEvent]


class GenerationUsage(StrictOutputModel):
    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    latency_ms: NonNegativeInt


class GenerateSuccessResponse(StrictOutputModel):
    schema_version: Literal["1.0"]
    request_id: UUID4
    worldview: Worldview
    usage: GenerationUsage
    model_version: str


class ErrorCode(StrEnum):
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    CONFLICT = "CONFLICT"
    SCHEMA_INVALID = "SCHEMA_INVALID"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    INTERNAL = "INTERNAL"


class GenerationStage(StrEnum):
    ANALYZE = "analyze"
    STRUCTURE = "structure"
    RELATIONS = "relations"
    FINALIZE = "finalize"


class GenerateErrorResponse(StrictOutputModel):
    schema_version: Literal["1.0"]
    request_id: UUID4 | None
    code: ErrorCode
    message: str
    stage: GenerationStage | None = None


class ModelInfoResponse(StrictOutputModel):
    model_version: str
    base_model: str
    loaded_at: datetime
    quantization: str


class HealthResponse(StrictOutputModel):
    status: Literal["ok"]
