# SekAI — AI

세계관·AI(SekAI)의 추론 서버입니다. 사용자의 기획 브리프를 받아 검증된 구조화 세계관 JSON(`worldview`)을 반환합니다.

## 역할

- LLM 서빙과 프롬프트 실행
- 구조화 세계관 생성
- ID·참조·계약 규칙 검증
- 잘못된 대상의 제한적 복구
- 모델·프롬프트·스키마 버전 추적

## 동작 방식

1. BE로부터 세계관 브리프를 전달받습니다.
2. 브리프를 한 번에 생성하거나, 먼저 계획한 뒤 전체 세계관을 생성합니다.
3. 코드가 결과의 형식, ID, 관계, 시점 참조를 검증합니다.
4. 복구 가능한 오류만 해당 대상을 한 번 교체하고 전체 결과를 다시 검증합니다.
5. 완전한 `worldview` 또는 명시적인 오류를 BE에 반환합니다.

AI 서버는 데이터를 저장하거나 사용자를 인증하지 않습니다. UUID 치환과 DB 저장은 BE가 담당합니다.

## 문서

- [MVP 워크플로우](docs/01-MVP-WORKFLOW.md)
- [모델과 서빙](docs/02-MODEL-AND-SERVING.md)
- [평가와 파인튜닝](docs/03-EVALUATION-AND-FINETUNING.md)

팀 간 요청·응답과 데이터 모델의 기준은 다음 공통 문서입니다.

- [AI ↔ BE 계약](https://github.com/Novel-SekAI/docs/blob/main/02-%EC%84%A4%EA%B3%84/AI-BE-CONTRACT.md)
- [공통 데이터 모델](https://github.com/Novel-SekAI/docs/blob/main/02-%EC%84%A4%EA%B3%84/DATA-MODEL.md)
