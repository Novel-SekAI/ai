# SekAI — AI

세계관·AI(SekAI)의 **추론 서버**입니다. 기획 브리프를 받아 구조화 세계관 JSON(`worldview`)을 한 번에 반환합니다.

## 역할

- LLM 서빙과 프롬프트 실행
- 구조화 출력과 코드 기반 검증
- 실패한 필드의 제한적 복구
- 모델·프롬프트·어댑터 버전 관리

## 동작 방식

1. 사용자가 작성한 세계관 브리프를 전달받습니다.
2. 브리프의 핵심 설정과 필요한 구성 요소를 분석합니다.
3. 분석 결과를 바탕으로 인물, 장소, 사건, 관계가 포함된 세계관을 생성합니다.
4. 생성 결과의 형식과 참조 관계를 코드로 검증합니다.
5. 문제가 있는 부분만 제한적으로 복구한 뒤 구조화된 `worldview` JSON을 반환합니다.

기존 BE↔AI 요청/응답 계약은 [`Novel-SekAI/docs`](https://github.com/Novel-SekAI/docs)의
`02-설계/AI-BE-CONTRACT.md`와 `02-설계/DATA-MODEL.md`를 기준으로 합니다.

AI 서버는 데이터를 직접 저장하거나 사용자를 인증하지 않습니다. 생성과 검증만 담당하며,
저장과 사용자 관리는 BE가 담당합니다.

## 실행 정보

| 항목 | 값 |
|------|-----|
| 포트 | 8000 |
| 노드 | **GPU** (`nvidia/cuda:*-runtime`) |
| 서빙 | vLLM/TGI 등 self-host |

경계: DB·인증·클라이언트를 알지 못하며 계약의 요청/응답만 처리합니다(stateless).

## 문서

설계·컨벤션 문서는 [`Novel-SekAI/docs`](https://github.com/Novel-SekAI/docs)에 있습니다.

- `02-설계/AI-BE-CONTRACT.md` — BE↔AI 내부 계약
- `02-설계/DATA-MODEL.md` — 공통 데이터 모델
- `03-컨벤션/CONTAINER.md`


AI 레포지토리에 관한 내부 문서 : 

1. [MVP 워크플로우](docs/01-MVP-WORKFLOW.md)
2. [모델 선정](docs/02-MODEL-SELECTION.md)
3. [파인튜닝 전략](docs/03-FINETUNING-STRATEGY.md)
4. [평가와 릴리스 기준](docs/04-EVALUATION.md)
5. [저장소 초기 구조](docs/05-REPOSITORY-SETUP.md)
6. [서빙과 운영](docs/06-SERVING.md)
