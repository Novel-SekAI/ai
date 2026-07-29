# 파인튜닝 전략

상태: **Accepted**  
전제: 파인튜닝을 제품 계획에 포함하되, 기준선보다 좋아졌을 때만 배포합니다.

## 목표

파인튜닝의 목표는 모델에 세계관 지식을 무작정 주입하는 것이 아닙니다.

- SekAI 계약 필드를 안정적으로 채우기
- 짧은 한국어 브리프에서 빠진 설정을 일관되게 확장하기
- 엔티티 간 관계와 참조를 보존하기
- 중복 표현과 상충 설정을 줄이기
- 프롬프트 길이와 복구 호출 비율을 낮추기

JSON 문법 자체는 structured output이 담당하고, 학습은 **내용 품질과 계약 의미**에 집중합니다.

## 1차 방식

`Qwen/Qwen3.5-9B` post-trained 모델에 QLoRA/LoRA를 적용합니다.

- 하나의 어댑터에 `PLAN`과 `WORLDVIEW` 작업을 함께 학습
- 각 샘플에 명시적인 `task_type` 사용
- non-thinking 응답만 정답 데이터로 사용
- 전체 파라미터 학습은 QLoRA가 한계에 도달한 뒤에만 검토

초기에는 랭크·학습률을 문서에 고정하지 않습니다. 작은 sweep과 고정 평가셋으로 정한
최종 학습 설정을 `configs/training/`에 버전 관리합니다.

## 데이터 형식

학습 원본은 JSONL로 저장하고, 실제 chat template 변환은 tokenizer가 담당합니다.

```json
{
  "sample_id": "worldview-0001",
  "task_type": "WORLDVIEW",
  "input": {
    "brief": "기획 브리프",
    "guidance": {},
    "world_plan": {}
  },
  "output": {
    "worldview": {}
  },
  "metadata": {
    "source": "human_authored",
    "review_status": "approved",
    "schema_version": "v1"
  }
}
```

## 데이터 구성

우선순위는 다음과 같습니다.

1. 팀이 직접 작성하고 검수한 정상 예시
2. 실제 오류 유형을 수정한 hard example
3. 여러 장르·길이·제약을 조합한 검수 완료 합성 데이터
4. 거절·빈 입력·상충 지시 등 경계 사례

초기 실험은 **검수된 200~500쌍**으로 시작할 수 있지만, 데이터 수 자체를 성공 기준으로
삼지 않습니다. 품질과 다양성이 부족하면 파인튜닝을 배포하지 않습니다.

### 금지

- 사용 권한이 확인되지 않은 소설 원문을 학습 데이터로 사용
- 개인정보나 사용자 식별 정보를 그대로 저장
- 동일 세계관의 변형을 train과 test에 나눠 넣기
- 검수하지 않은 합성 출력을 정답으로 자동 편입
- 평가셋을 학습 또는 하이퍼파라미터 선택에 사용

## 분할

- train: 학습
- validation: 조기 종료와 설정 선택
- test: 최종 비교
- regression: 운영 장애와 버그 재현 전용

분할은 문장 단위가 아니라 **세계관/시나리오 계열 단위**로 수행해 데이터 누수를 막습니다.

## 실행 순서

1. prompt-only 기준선 측정
2. 데이터 스키마 검증과 중복 제거
3. 작은 QLoRA 실험
4. validation으로 후보 선택
5. test와 regression 전체 평가
6. 기본 모델 대비 품질·구조·지연시간 비교
7. 통과한 어댑터만 등록하고 canary 배포

## 아티팩트 버전

모든 결과에 다음 버전을 남깁니다.

- `base_model_id`
- `base_model_revision`
- `adapter_id`
- `dataset_version`
- `prompt_version`
- `schema_version`
- `serving_version`

재현할 수 없는 어댑터는 배포하지 않습니다.

