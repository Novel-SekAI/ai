# 모델 선정

상태: **Accepted**  
결정일: **2026-07-29**

## 결정

MVP 기본 모델은 [`Qwen/Qwen3.5-9B`](https://huggingface.co/Qwen/Qwen3.5-9B)
post-trained 모델로 정합니다.

- 추론: non-thinking
- 학습: QLoRA/LoRA
- 서빙: vLLM
- 컨텍스트 길이: SekAI 입력 분포에 맞게 작게 시작하고 부하 테스트로 확정

Qwen3.5-9B 모델 카드는 9B 언어 모델, Apache-2.0 라이선스, 201개 언어·방언 지원,
Transformers·vLLM·SGLang 호환을 명시합니다. 범용 벤치마크 점수만으로 선정한 것이 아니라,
MVP에서 중요한 비용·지연시간·구조화 출력·파인튜닝 편의의 균형을 우선했습니다.

## 후보 비교

| 후보 | 위치 | 장점 | 현재 판단 |
|---|---|---|---|
| Qwen3.5-9B post-trained | 기본 | 작은 운영 단위, 지시 이행, Apache-2.0, vLLM 지원 | **채택** |
| Qwen3.5-9B-Base | 학습 실험 | LoRA형 PEFT를 고려한 base 모델 | 데이터가 충분해진 뒤 challenger |
| Qwen3.5-27B | 품질 상향 | 더 큰 용량과 높은 품질 잠재력, Apache-2.0 | 9B가 품질 기준을 못 넘을 때 A/B |
| HyperCLOVA X SEED Think 14B | 한국어 challenger | 한국어·한국 문화 강점 | 사용자 정의 라이선스 검토 후 제한적 비교 |
| EXAONE 4.0 32B | 연구 후보 | 한국어 지원, 32B급 | NC 라이선스 때문에 기본 상용 후보에서 제외 |

공식 자료:

- [`Qwen3.5-9B-Base`](https://huggingface.co/Qwen/Qwen3.5-9B-Base)는 직접 상호작용보다 파인튜닝·연구를 주 용도로 설명합니다.
- [`Qwen3.5-27B`](https://huggingface.co/Qwen/Qwen3.5-27B)는 27B, Apache-2.0, vLLM 호환 모델입니다.
- [`HyperCLOVA X SEED Think 14B`](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Think-14B)는 `hyperclovax-seed` 사용자 정의 라이선스를 사용합니다.
- [`EXAONE 4.0 32B`](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B)는 EXAONE AI Model License Agreement 1.2-NC를 사용합니다.

## Base가 아니라 post-trained부터 시작하는 이유

파인튜닝을 전제로 해도 첫 실험은 post-trained 모델이 안전합니다.

- 적은 데이터로도 기존 지시 이행 능력을 유지하기 쉽습니다.
- prompt-only 기준선을 즉시 만들 수 있습니다.
- 파인튜닝 효과와 “원래 모델이 잘하던 것”을 분리해 비교할 수 있습니다.
- base 모델은 더 큰 학습 데이터와 대화 정렬 작업이 필요합니다.

다음 조건을 만족하면 base 모델도 같은 평가셋으로 비교합니다.

- 충분히 다양한 검수 완료 데이터가 확보됨
- post-trained LoRA가 일정 수준 이후 개선되지 않음
- base 학습의 시간·GPU 비용을 감당할 수 있음

## 변경 조건

다음 중 하나가 발생하면 모델 결정을 다시 엽니다.

1. 9B가 파인튜닝 후에도 콘텐츠 품질 릴리스 기준을 통과하지 못함
2. 27B가 허용 지연시간 안에서 유의미한 품질 향상을 보임
3. 한국어 challenger가 동일 데이터·동일 평가에서 더 우수하고 라이선스가 배포 목적에 적합함
4. 목표 GPU에서 9B 처리량이 서비스 요구를 충족하지 못함

모델 변경은 이름이나 공개 리더보드가 아니라
[`04-EVALUATION.md`](04-EVALUATION.md)의 동일 조건 A/B 결과로 승인합니다.

