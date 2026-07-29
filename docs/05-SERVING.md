# 서빙과 운영

상태: **Accepted**

## 구성

```text
BE
 └─ POST /v1/generate
     └─ SekAI API/orchestrator
         ├─ schema + validator
         └─ vLLM OpenAI-compatible API
             └─ Qwen3.5-9B + optional LoRA
```

vLLM 포트는 내부에서만 사용하고, BE에는 SekAI 계약 API만 노출합니다.

## vLLM 선택

vLLM은 OpenAI-compatible API와 JSON Schema 기반 structured output을 지원합니다.
[`Structured Outputs`](https://docs.vllm.ai/en/stable/features/structured_outputs/) 문서를 기준으로
`response_format.type=json_schema` 또는 현재 버전의 `structured_outputs.json`을 사용합니다.

기존 README의 TGI 병기는 제거합니다. TGI 저장소는
[maintenance mode](https://github.com/huggingface/text-generation-inference)이며 2026-03-21에
archive되었으므로 신규 MVP의 기본 서빙 엔진으로 선택하지 않습니다.

## 시작 설정

- 모델: `Qwen/Qwen3.5-9B`
- 모드: non-thinking
- 외부 컨텍스트: 없음
- RAG: OFF
- temperature: 평가로 결정하고 설정 파일에 고정
- max output tokens: 계약상 최대 크기를 측정한 뒤 고정
- context length: 실제 브리프 분포에 맞춰 최소화

Qwen 모델 카드는 최신 서빙 프레임워크 사용을 권장합니다. PoC에서는 호환 버전을 찾되,
운영에서는 검증한 vLLM·PyTorch·CUDA 버전 또는 commit을 고정합니다.

## 엔드포인트

| 엔드포인트 | 의미 |
|---|---|
| `/health` | API 프로세스가 응답하는가 |
| `/ready` | 모델과 필수 스키마가 로드되었는가 |
| `/v1/model` | 실제 제공 중인 모델 조합은 무엇인가 |
| `/v1/generate` | 계약에 맞는 세계관을 생성하는가 |

`/v1/model` 응답에는 최소한 아래 정보를 포함합니다.

```json
{
  "baseModelId": "Qwen/Qwen3.5-9B",
  "baseModelRevision": "pinned-revision",
  "adapterId": null,
  "promptVersion": "v1",
  "schemaVersion": "v1",
  "servingVersion": "pinned-version"
}
```

## 타임아웃과 재시도

- 모델 호출을 애플리케이션 레벨에서 무한 재시도하지 않습니다.
- 구조 오류는 네트워크 재시도가 아니라 부분 복구 경로로 처리합니다.
- OOM·타임아웃은 재시도 가능 여부가 드러나는 표준 오류로 변환합니다.
- 클라이언트 연결이 끊기면 가능한 범위에서 진행 중 생성을 취소합니다.

## 로그와 메트릭

기본 로그:

- `request_id`
- 처리 단계
- 모델·어댑터·프롬프트·스키마 버전
- 단계별 지연시간
- 입력·출력 토큰 수
- validator 오류 코드
- 복구 시도 여부

원문 브리프와 전체 생성 결과는 기본 로그에 남기지 않습니다. 디버그 샘플 저장이 필요하면
사용자 동의, 보존 기간, 접근 권한, 비식별화 정책을 먼저 정합니다.

