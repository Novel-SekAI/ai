# SekAI — AI

세계관·AI(SekAI)의 **추론 서버**입니다. 기획 브리프를 받아 구조화 세계관 JSON(`worldview`)을 한 번에 반환합니다.

## 역할

- LLM 서빙 및 프롬프트·구조화 출력·검증 루프
- `POST /v1/generate` — 브리프 → `worldview` JSON (동기, 스트리밍 미사용)
- `GET /health` · `GET /ready` · `GET /v1/model`

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
