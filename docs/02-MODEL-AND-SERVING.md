# 모델과 서빙

상태: **Provisional — PoC 후 확정**  
기준일: **2026-07-30**

## 초기 기준 모델

첫 MVP PoC는 [`Qwen/Qwen3.5-9B`](https://huggingface.co/Qwen/Qwen3.5-9B) post-trained 모델로 시작합니다.

- 모드: non-thinking
- 서빙: vLLM OpenAI-compatible server
- 입력: text-only
- RAG: OFF
- 파인튜닝: 초기 기준선에서는 사용하지 않음

Qwen3.5-9B는 9B 언어 모델, Apache-2.0 라이선스, vLLM 호환 모델입니다. 모델 이름만으로 최종 채택하지 않으며, 현재 `worldview` 계약과 목표 GPU에서 품질·지연시간·VRAM을 측정해 확정합니다.

## post-trained부터 시작하는 이유

- 적은 설정으로 지시 이행 기준선을 만들 수 있습니다.
- prompt-only와 파인튜닝 결과를 분리해 비교할 수 있습니다.
- Base 모델보다 초기 데이터와 정렬 작업 부담이 작습니다.
- 구조화 생성과 한국어 품질을 즉시 평가할 수 있습니다.

`Qwen3.5-9B-Base`는 충분한 검수 데이터와 별도 정렬 실험이 필요한 후속 후보입니다.

## non-thinking 설정

Qwen3.5는 Qwen3의 `/think`, `/nothink` 소프트 스위치를 공식 지원하지 않습니다. vLLM OpenAI-compatible 요청에는 다음 값을 사용합니다.

```python
extra_body={
    "top_k": 20,
    "chat_template_kwargs": {
        "enable_thinking": False,
    },
}
```

공식 non-thinking 일반 작업 권장값은 PoC 시작점으로만 사용합니다.

```text
temperature = 0.7
top_p = 0.8
top_k = 20
presence_penalty = 1.5
repetition_penalty = 1.0
```

최종 값은 SekAI 고정 평가셋으로 정하고 설정 파일에 고정합니다.

## structured output

Pydantic v2 모델에서 JSON Schema를 생성해 vLLM에 전달합니다.

```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "sekai-worldview-v1",
        "schema": Worldview.model_json_schema(),
    },
}
```

최신 vLLM의 [`Structured Outputs`](https://docs.vllm.ai/en/stable/features/structured_outputs/)를 기준으로 사용하고, 검증이 끝난 vLLM 버전과 컨테이너 이미지를 고정합니다.

structured output은 JSON 형태를 제약합니다. ID 집합, 교차 참조, 중복 관계와 브리프 제약은 애플리케이션 Validator가 별도로 검사합니다.

Qwen3.5 모델 카드의 현재 예시는 vLLM nightly/main 계열 설치를 안내합니다. 먼저 stable 지원 여부를 확인하고, 지원되지 않으면 PoC에서 검증한 nightly commit 또는 이미지를 명시적으로 고정합니다. 운영 환경이 무심코 다른 최신 버전으로 이동하지 않게 합니다.

## vLLM 실행 기준

SekAI는 텍스트 입력만 사용하므로 vision encoder와 multimodal profiling을 생략하는 `--language-model-only`를 우선 검증합니다.

```powershell
vllm serve Qwen/Qwen3.5-9B `
  --port 8000 `
  --tensor-parallel-size 1 `
  --reasoning-parser qwen3 `
  --language-model-only `
  --max-model-len <POC에서_확정>
```

위 명령은 개발 시작용 템플릿입니다. 다음 값은 smoke test와 부하 테스트 후 확정합니다.

- vLLM·PyTorch·CUDA 버전
- 모델 revision
- dtype과 양자화
- `max-model-len`
- `max_tokens`
- GPU memory utilization
- 동시 요청·queue 상한

## 컨텍스트와 출력 한도

모델의 최대 컨텍스트를 그대로 운영값으로 사용하지 않습니다. 다음 합계를 실제 tokenizer로 측정합니다.

```text
브리프 + 내부 계획 + 프롬프트 + JSON Schema + 최대 worldview 출력 + 안전 여유
```

공통 계약이 클라이언트 입력에 출력 토큰 한도를 노출하지 않더라도, OOM과 무한 생성을 막기 위한 내부 `max_tokens`는 필요합니다. 한도에서 출력이 잘려 계약을 만족하지 못하면 부분 응답을 반환하지 않습니다.

## 서비스 시간과 재시도

- BE→AI hard timeout은 공통 계약의 120초를 따릅니다.
- p95 90초 이하는 초기 잠정 목표이며, 목표 GPU 측정 후 확정합니다.
- 애플리케이션에서 모델 호출을 무한 재시도하지 않습니다.
- 구조 오류는 네트워크 재시도가 아니라 대상 교체 경로로 처리합니다.
- 클라이언트 연결이 끊기면 가능한 범위에서 진행 중 생성을 취소합니다.

## 관측과 버전

공통 계약의 범위에 맞춰 응답 `usage`와 structured log부터 사용합니다.

기본 기록 항목:

- `request_id`
- pipeline mode와 처리 단계
- 모델 ID·revision
- 어댑터 ID
- 프롬프트 버전
- 스키마 버전
- vLLM·PyTorch·CUDA 버전
- 입력·출력 토큰
- 단계별 지연시간과 TTFT
- Validator 오류 코드
- 복구 시도 여부
- OOM·타임아웃

원문 브리프와 전체 생성 결과는 기본 로그에 남기지 않습니다.

## PoC 완료 기준

1. 목표 GPU에서 모델이 안정적으로 로드됨
2. non-thinking 응답에 불필요한 사고 내용이 없음
3. 전체 `worldview` JSON Schema 출력 성공
4. 최대 출력에 가까운 요청이 잘리지 않음
5. 1개와 복수 동시 요청의 VRAM·p50·p95 측정
6. 목표 부하에서 OOM 0건
7. 모델·서빙 조합을 재현할 수 있는 버전 기록

## 모델 변경 조건

다음 경우에만 [`Qwen/Qwen3.5-27B`](https://huggingface.co/Qwen/Qwen3.5-27B)를 동일 조건으로 비교합니다.

1. 9B가 구조 하드 게이트를 통과하지만 콘텐츠 품질 기준을 못 넘음
2. 프롬프트와 `plan_then_generate`로도 같은 품질 문제가 반복됨
3. 27B가 목표 하드웨어에서 120초 예산과 처리량을 만족함
4. 품질 개선이 추가 GPU 비용보다 큼

모델 변경은 공개 리더보드가 아니라 [`03-EVALUATION-AND-FINETUNING.md`](03-EVALUATION-AND-FINETUNING.md)의 동일 평가셋 결과로 결정합니다.

## 공식 자료

- [Qwen3.5-9B model card](https://huggingface.co/Qwen/Qwen3.5-9B)
- [vLLM Qwen3.5 support](https://docs.vllm.ai/en/stable/api/vllm/model_executor/models/qwen3_5/)
- [vLLM Structured Outputs](https://docs.vllm.ai/en/stable/features/structured_outputs/)
