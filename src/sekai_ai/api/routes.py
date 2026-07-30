from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    status: Literal["ok"]


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="API 프로세스 상태 확인",
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
