from fastapi import APIRouter

from sekai_ai.schemas.contract import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="API 프로세스 상태 확인",
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
