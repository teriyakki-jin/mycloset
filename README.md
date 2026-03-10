<div align="center">

# 👗 ClosetIQ

**AI가 당신의 옷장을 분석하고, 오늘의 코디를 추천해드립니다**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tests](https://img.shields.io/badge/Tests-52%20passed-22c55e)](./apps/api/tests)
[![Coverage](https://img.shields.io/badge/Coverage-73%25-22c55e)](./apps/api/tests)

</div>

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 📸 **AI 옷 등록** | 사진 업로드 시 배경 자동 제거 + GPT-4o 태깅 (카테고리, 색상, 시즌, 스타일) |
| 🔗 **쇼핑몰 URL 임포트** | 무신사·29CM 등 상품 URL만 붙여넣으면 이미지·이름 자동 등록 |
| 👔 **코디 추천** | 날씨·기온·상황(출근/데이트/운동)을 반영한 개인화 추천 엔진 |
| 🪞 **AI 가상 피팅** | 내 사진 + 옷 사진 → HuggingFace IDM-VTON으로 실제 착용 이미지 생성 |
| 📊 **스타일 리포트** | 보유 아이템 통계, 대표 색상, 카테고리 분포, 자주 입는 옷 분석 |
| 📅 **착용 기록** | 날짜·상황별 착용 로그로 옷 활용도 추적 |

---

## 🏗️ 아키텍처

```

<img width="1024" height="561" alt="image" src="https://github.com/user-attachments/assets/5e293427-f96d-4391-9000-c28bcb2fd8c7" />

```

---

## 🛠️ 기술 스택

### Frontend
- **Next.js 15** (App Router) + **TypeScript**
- **Tailwind CSS v4** + shadcn/ui
- PWA (Progressive Web App) 지원

### Backend
- **FastAPI** + **SQLAlchemy 2.x** (async)
- **PostgreSQL** + pgvector (벡터 임베딩)
- **Redis** + **arq** (비동기 작업 큐)
- **MinIO** (S3 호환 오브젝트 스토리지)

### AI / ML
- **rembg** — 배경 자동 제거
- **OpenAI GPT-4o-mini** — 옷 이미지 자동 태깅
- **HuggingFace IDM-VTON** — AI 가상 피팅

---

## 🚀 빠른 시작

### 사전 준비
- Docker & Docker Compose
- Python 3.11+, Node.js 20+, pnpm
- OpenAI API Key
- HuggingFace API Token

### 1. 저장소 클론
```bash
git clone https://github.com/teriyakki-jin/mycloset.git
cd mycloset
```

### 2. 인프라 실행 (DB · Redis · MinIO)
```bash
docker compose up -d
```

### 3. API 서버
```bash
cd apps/api
cp .env.example .env   # .env 편집 후 API 키 입력
uv sync
uv run uvicorn src.main:app --port 8102 --reload
```

### 4. 이미지 처리 워커
```bash
cd workers/image-processor
uv sync
uv run python src/main.py
```

### 5. 웹 앱
```bash
cd apps/web
pnpm install
pnpm dev
```

`http://localhost:3000` 에서 확인

---

## 🧪 테스트

```bash
cd apps/api
uv run pytest --cov=src
```

```
52 passed  ·  Coverage 73%
├── unit/      추천 엔진 로직, URL 스크래퍼 파서
└── integration/  인증, 옷장 CRUD, 코디 추천, 스타일 리포트
```

---

## 📁 프로젝트 구조

```
mycloset/
├── apps/
│   ├── api/                # FastAPI 백엔드
│   │   ├── src/
│   │   │   ├── routers/    # 엔드포인트
│   │   │   ├── services/   # 비즈니스 로직
│   │   │   ├── models/     # SQLAlchemy ORM
│   │   │   └── schemas/    # Pydantic 스키마
│   │   └── tests/          # 단위·통합 테스트
│   └── web/                # Next.js 프론트엔드
│       └── src/app/
│           ├── closet/     # 옷장
│           ├── outfit/     # 코디 추천
│           ├── style-report/ # 스타일 리포트
│           └── upload/     # 옷 등록
├── workers/
│   └── image-processor/    # rembg + GPT-4o 워커
└── docker-compose.yml
```

---

## 📄 API 문서

서버 실행 후 `http://localhost:8102/docs` 에서 Swagger UI 확인

---

<div align="center">

Made with ❤️ by [teriyakki-jin](https://github.com/teriyakki-jin)

</div>
