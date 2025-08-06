# 🚀 MCP 게시판 프로젝트

> **MCP(Model Context Protocol)와 Anthropic Claude API를 활용한 AI 기반 게시판 차트 생성 시스템**

이 프로젝트는 사용자의 자연어 명령을 AI가 이해하여 데이터를 시각화하는 혁신적인 게시판 시스템입니다. 
실제 Anthropic Claude API와 시뮬레이션 모드를 모두 지원하여 다양한 환경에서 사용할 수 있습니다.

## ✨ 주요 기능

### 🤖 AI 기반 자연어 처리
- 📝 **스마트 게시글 작성**: AI를 통한 자연어 게시글 관리 ("홍길동으로 매출 10 데이터 글 써줘")
- 📊 **AI 차트 생성**: 자연어 명령으로 다양한 차트 자동 생성
- 🧠 **실시간 MCP 통합**: Anthropic Claude API를 통한 실제 AI 기반 명령 처리

### 📈 고급 차트 기능
- 🎨 **다양한 차트 타입**: 막대차트, 선그래프, 원그래프, 도넛차트 지원
- 👥 **다중 작성자 차트**: 여러 작성자의 데이터를 하나의 차트로 통합 시각화
- 🔍 **실시간 데이터 조회**: 작성자별 게시글 및 통계 정보 동적 표시

### 🔧 개발자 친화적 기능
- 📱 **반응형 웹 디자인**: 모바일과 데스크톱 최적화
- 📋 **상세한 로깅**: MCP 통신 과정 실시간 모니터링
- 🌐 **AWS 배포 지원**: Lightsail 원클릭 배포 가이드 제공
- 📚 **완전한 문서화**: 코드 주석 및 아키텍처 가이드

## 🛠️ 기술 스택

### Backend
- **Framework**: Python 3.8+, FastAPI, Uvicorn
- **Database**: SQLAlchemy, SQLite
- **AI Integration**: Anthropic Claude API, AsyncAnthropic
- **Configuration**: python-dotenv, 환경변수 관리

### Frontend
- **UI**: HTML5, CSS3, JavaScript (ES6+)
- **Visualization**: Chart.js 4.x
- **Template Engine**: Jinja2
- **Responsive**: CSS Grid, Flexbox

### Infrastructure
- **Development**: 로컬 개발 서버
- **Production**: AWS Lightsail, Ubuntu 22.04
- **Monitoring**: 커스텀 로깅 시스템
- **Deployment**: 자동화 배포 스크립트

## 📦 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd mcp_board
```

### 2. 환경 설정
```bash
# .env 파일 생성 (프로젝트 루트에)
touch .env

# .env 파일에 API 키 설정 (선택사항 - 실제 MCP 사용시)
echo "ANTHROPIC_API_KEY=sk-ant-api03-your_actual_key_here" >> .env
echo "HOST=127.0.0.1" >> .env
echo "PORT=8000" >> .env
echo "DEBUG=true" >> .env
```

### 3. 의존성 설치
```bash
# 방법 1: 자동 설치 스크립트 사용 (권장)
python run.py install

# 방법 2: 직접 설치
pip install -r requirements.txt
```

### 4. 서버 실행
```bash
# 방법 1: run.py 스크립트 사용 (권장)
python run.py

# 방법 2: 직접 실행
python app.py
```

### 5. 브라우저에서 접속
```
http://localhost:8000
```

### 6. API 키 설정 (실제 MCP 사용시)

#### 옵션 A: .env 파일로 설정 (권장)
1. [Anthropic Console](https://console.anthropic.com/)에서 API 키 발급
2. `.env` 파일에 `ANTHROPIC_API_KEY=your_key` 추가
3. 서버 재시작

#### 옵션 B: 웹 인터페이스로 설정
1. 브라우저에서 게시판 접속
2. "MCP 상태" 섹션에서 API 키 입력
3. 설정 완료 (서버 재시작시 초기화됨)

> **💡 참고**: API 키 없이도 시뮬레이션 모드로 모든 기능을 테스트할 수 있습니다!

## 🎯 사용 방법

### 📝 게시글 작성 방법

#### 방법 1: 일반 게시글 작성 폼
1. **작성자명**: 차트 생성에 사용될 작성자명 입력
2. **제목**: 게시글 제목 입력
3. **내용**: 게시글 내용 (선택사항)
4. **숫자값**: 차트에 표시될 숫자 데이터
5. **카테고리**: 게시글 분류 (선택사항)

#### 방법 2: AI 자연어 게시글 관리 (🆕 NEW!)
자연어 명령으로 게시글을 생성/수정/삭제할 수 있습니다.

**게시글 생성 명령어 예시:**
- `"홍길동으로 제목은 1월 매출, 내용은 월간 매출 보고서, 매출 150으로 글 써줘"`
- `"김철수로 프로젝트 진행률 80% 데이터 글 생성해줘"`
- `"이영희로 고객 만족도 95점 포스트 만들어줘"`

**게시글 수정 명령어 예시:**
- `"3번 게시글의 제목을 '2월 매출 보고서'로 수정해줘"`
- `"5번 게시글의 숫자값을 200으로 변경해줘"`

**게시글 삭제 명령어 예시:**
- `"1번 게시글 삭제해줘"`
- `"홍길동의 모든 게시글 삭제해줘"`

### 📊 차트 생성 명령어

#### 단일 작성자 차트
- `"홍길동의 데이터를 막대차트로 보여줘"`
- `"김철수의 값을 선그래프로 표시해줘"`
- `"이영희의 수치를 원그래프로 만들어줘"`

#### 다중 작성자 차트 (🆕 NEW!)
- `"홍길동과 김철수의 데이터를 막대차트로 비교해줘"`
- `"모든 사람들의 데이터를 선그래프로 보여줘"`
- `"전체 작성자의 데이터를 차트로 만들어줘"`

### 🎨 지원하는 차트 타입
- **막대차트**: 막대, 바, 막대그래프, 바차트
- **선그래프**: 선그래프, 라인, 선형, 꺾은선
- **원그래프**: 원그래프, 파이, 원형
- **도넛차트**: 도넛, 도너츠

### 🔍 MCP 모드
- **실제 MCP 모드**: Anthropic Claude API 사용 (API 키 필요)
- **시뮬레이션 모드**: 정규식 기반 파싱 (API 키 불필요)

## 📁 프로젝트 구조

```
mcp_board/
├── 🚀 핵심 애플리케이션
│   ├── app.py                 # FastAPI 메인 애플리케이션
│   ├── run.py                 # 실행 스크립트
│   └── config.py              # 설정 관리 (.env 지원)
│
├── 🤖 MCP 서버 구현
│   ├── mcp_server_real.py     # 실제 Anthropic API 기반 MCP 서버
│   ├── mcp_server.py          # 시뮬레이션 MCP 서버
│   ├── mcp_logger.py          # MCP 통신 로깅 시스템
│   └── mcp_real_example.py    # MCP 사용 예시
│
├── 🗄️ 데이터 및 차트
│   ├── database.py            # 데이터베이스 모델 및 관리 (SQLAlchemy)
│   ├── chart_generator.py     # Chart.js 동적 생성 엔진
│   └── board.db              # SQLite 데이터베이스 파일
│
├── 🎨 프론트엔드
│   ├── templates/
│   │   └── index.html        # 메인 웹페이지 (Jinja2 템플릿)
│   └── static/
│       └── style.css         # 반응형 CSS 스타일시트
│
├── 📚 문서 및 설정
│   ├── README.md             # 프로젝트 메인 문서
│   ├── deploy.md             # AWS Lightsail 배포 가이드
│   ├── logic.md              # 구현 로직 상세 설명서
│   ├── readme.txt            # 원본 구현 가이드
│   ├── requirements.txt      # Python 의존성 목록
│   ├── .env                  # 환경변수 설정 파일 (gitignore)
│   └── .gitignore            # Git 무시 파일 목록
│
└── 🔧 개발 도구
    └── __pycache__/          # Python 바이트코드 캐시
```

### 📋 주요 파일 설명

#### 🚀 핵심 모듈
- **`app.py`**: FastAPI 기반 웹 서버, API 엔드포인트, 라우팅
- **`config.py`**: 환경변수 관리, .env 파일 지원, 설정 중앙화
- **`run.py`**: 개발/프로덕션 서버 실행 스크립트

#### 🤖 MCP 시스템
- **`mcp_server_real.py`**: Anthropic Claude API 실제 연동
- **`mcp_server.py`**: 정규식 기반 시뮬레이션 모드
- **`mcp_logger.py`**: MCP 통신 과정 실시간 로깅

#### 📊 데이터 처리
- **`database.py`**: SQLAlchemy ORM, 게시글 CRUD
- **`chart_generator.py`**: Chart.js 코드 동적 생성

#### 📚 문서화
- **`deploy.md`**: AWS 배포 완전 가이드 (11KB)
- **`logic.md`**: 시스템 아키텍처 및 구현 로직 (18KB)

## 🗄️ 데이터베이스 스키마

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    numeric_value FLOAT,      -- 차트로 표현할 숫자값
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 API 엔드포인트

### 🌐 웹페이지
- `GET /` - 메인 게시판 페이지 (템플릿 렌더링)

### 📝 게시글 관리
- `POST /add-post` - 일반 게시글 추가
- `POST /manage-post` - 🆕 AI 자연어 게시글 관리 (생성/수정/삭제)
- `GET /posts` - 모든 게시글 조회
- `GET /posts/author/{author_name}` - 특정 작성자 게시글 조회
- `PUT /posts/{post_id}` - 게시글 수정
- `DELETE /posts/{post_id}` - 게시글 삭제

### 📊 차트 기능
- `POST /generate-chart` - 자연어 명령 차트 생성 (단일/다중 작성자)
- `GET /authors` - 차트 생성 가능한 작성자 목록
- `GET /chart-types` - 지원하는 차트 타입 목록

### 🤖 MCP 시스템 관리
- `GET /mcp-status` - MCP 상태 확인 (실제/시뮬레이션 모드)
- `POST /set-api-key` - Anthropic API 키 동적 설정
- `GET /mcp-logs` - MCP 통신 로그 조회
- `POST /clear-mcp-logs` - MCP 로그 초기화

### 🔧 시스템 관리
- `GET /health` - 서버 헬스체크
- `GET /test/mcp` - MCP 기능 테스트 (개발용)

### 📊 요청/응답 예시

#### 자연어 차트 생성
```bash
curl -X POST "http://localhost:8000/generate-chart" \
  -H "Content-Type: application/json" \
  -d '{"command": "홍길동의 데이터를 막대차트로 보여줘"}'
```

#### AI 게시글 관리
```bash
curl -X POST "http://localhost:8000/manage-post" \
  -H "Content-Type: application/json" \
  -d '{"command": "김철수로 매출 100 데이터 글 써줘"}'
```

#### MCP 상태 확인
```bash
curl -X GET "http://localhost:8000/mcp-status"
```

## 🎨 주요 특징

### 🤖 AI 기반 MCP 통합
- **실제 AI 파싱**: Anthropic Claude API를 통한 고급 자연어 이해
- **폴백 시스템**: API 오류시 정규식 기반 파싱으로 자동 전환
- **실시간 로깅**: MCP 통신 과정 완전 투명화 및 모니터링
- **동적 차트 생성**: AI가 최적화한 Chart.js 코드 실시간 생성

### 🎯 사용자 경험
- **직관적 자연어 인터페이스**: "홍길동으로 매출 데이터 글 써줘" 같은 자연어 명령
- **실시간 피드백**: 차트 생성 과정과 결과를 즉시 확인
- **반응형 웹 디자인**: 모바일/데스크톱 최적화
- **API 키 웹 설정**: 브라우저에서 직접 Anthropic API 키 설정

### 🔧 개발자 친화적
- **완전 문서화**: 모든 함수/클래스에 상세 주석 및 독스트링
- **모듈화 아키텍처**: 각 컴포넌트가 독립적으로 동작
- **환경 분리**: .env 파일을 통한 개발/프로덕션 설정 분리
- **배포 자동화**: AWS Lightsail 원클릭 배포 스크립트 제공

### 🚀 확장성
- **다중 모드 지원**: 실제 AI + 시뮬레이션 모드 동시 지원
- **플러그인 아키텍처**: 새로운 차트 타입 쉽게 추가
- **클라우드 Ready**: AWS 배포 가이드 및 스크립트 제공
- **성능 모니터링**: 실시간 로그 및 성능 추적

## 🔄 시스템 워크플로우

### 📊 차트 생성 플로우
```mermaid
graph TD
    A[사용자 자연어 입력] --> B{API 키 있음?}
    B -->|Yes| C[Anthropic Claude API 호출]
    B -->|No| D[정규식 기반 파싱]
    C --> E[AI 파싱 결과]
    D --> E
    E --> F[데이터베이스 조회]
    F --> G[Chart.js 코드 생성]
    G --> H[웹페이지 렌더링]
```

### 📝 게시글 관리 플로우
```mermaid
graph TD
    A[자연어 명령] --> B[MCP 파싱]
    B --> C{액션 타입}
    C -->|CREATE| D[게시글 생성]
    C -->|UPDATE| E[게시글 수정]
    C -->|DELETE| F[게시글 삭제]
    C -->|LIST| G[게시글 조회]
    D --> H[결과 반환]
    E --> H
    F --> H
    G --> H
```

## 🐛 문제 해결

### 🔧 일반적인 문제

#### 1. 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 의존성 재설치
pip install -r requirements.txt

# 가상환경 사용 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. 포트 충돌 (8000번 포트 사용 중)
```bash
# .env 파일에서 포트 변경
echo "PORT=8001" >> .env

# 또는 직접 실행시 포트 지정
python app.py --port 8001
```

#### 3. API 키 관련 문제
```bash
# .env 파일 확인
cat .env

# API 키 형식 확인 (sk-ant-로 시작해야 함)
# 웹 인터페이스에서 테스트 가능
```

#### 4. 데이터베이스 오류
```bash
# 데이터베이스 초기화
rm board.db
python run.py

# 수동 데이터베이스 재생성
python -c "from database import init_sample_data; init_sample_data()"
```

### 🚀 개발 모드

#### 로컬 개발 서버
```bash
# 자동 재시작 모드 (개발용)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 또는 run.py 사용
python run.py
```

#### 디버깅
```bash
# MCP 로그 실시간 확인
curl http://localhost:8000/mcp-logs

# 서버 상태 확인
curl http://localhost:8000/health

# MCP 상태 확인
curl http://localhost:8000/mcp-status
```

## 🌐 AWS 배포 가이드

### 🚀 Lightsail 배포 (권장)
프로덕션 환경에서 MCP 게시판을 운영하려면 AWS Lightsail을 사용하세요.

```bash
# 배포 가이드 문서 확인
cat deploy.md

# 주요 단계:
# 1. Lightsail 인스턴스 생성 ($5/월 권장)
# 2. Ubuntu 22.04 LTS 선택
# 3. SSH 접속 후 배포 스크립트 실행
# 4. .env 파일에 API 키 설정
# 5. 서비스 시작 및 모니터링
```

### 💰 예상 비용
- **Lightsail 인스턴스**: $5/월 (1GB RAM, 1vCPU, 40GB SSD)
- **데이터 전송**: 무료 (1TB까지)
- **도메인**: $10-15/년 (선택사항)
- **총 예상**: **월 $5-10**

**🔗 전체 배포 가이드**: [`deploy.md`](./deploy.md)

## 📈 확장 가능성

### 🎯 즉시 추가 가능한 기능
- **실시간 차트 업데이트**: WebSocket 통합
- **사용자 인증**: JWT 기반 로그인 시스템
- **데이터 내보내기**: PDF, PNG, CSV 내보내기
- **대시보드**: 여러 차트 통합 대시보드 

### 🚀 고급 기능 확장
- **다중 AI 모델**: OpenAI GPT, Google Gemini 지원
- **고급 차트**: D3.js, Plotly 통합
- **실시간 협업**: 다중 사용자 동시 편집
- **AI 분석**: 데이터 트렌드 자동 분석 및 인사이트

### 🏢 엔터프라이즈 기능
- **SSO 통합**: SAML, OAuth 2.0 지원
- **API 키 관리**: 사용량 제한 및 모니터링
- **감사 로그**: 모든 사용자 활동 기록
- **백업/복구**: 자동 데이터 백업 시스템

## 📚 추가 문서

- **📋 구현 로직**: [`logic.md`](./logic.md) - 시스템 아키텍처 및 상세 구현 설명
- **🚀 배포 가이드**: [`deploy.md`](./deploy.md) - AWS Lightsail 완전 배포 가이드  
- **📝 개발 가이드**: [`readme.txt`](./readme.txt) - 원본 개발 구현 가이드

## 🤝 기여하기

### 🔧 개발 환경 설정
```bash
# 1. 프로젝트 포크 및 클론
git clone https://github.com/your-username/mcp_board.git
cd mcp_board

# 2. 개발 브랜치 생성
git checkout -b feature/your-feature-name

# 3. 가상환경 설정
python -m venv venv
source venv/bin/activate

# 4. 개발 의존성 설치
pip install -r requirements.txt
```

### 📋 기여 가이드라인
1. **코드 스타일**: 기존 코드 스타일 유지, 상세한 주석 추가
2. **테스트**: 새로운 기능에 대한 테스트 코드 작성
3. **문서화**: README.md 및 관련 문서 업데이트
4. **커밋 메시지**: 명확하고 설명적인 커밋 메시지 작성

### 🎯 기여 아이디어
- 새로운 차트 타입 추가 (Radar, Bubble, Scatter)
- 다국어 지원 (i18n)
- 테마 시스템 (다크 모드)
- 성능 최적화
- 모바일 앱 개발

## 📄 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 글

- **Anthropic**: Claude API 제공
- **FastAPI**: 훌륭한 웹 프레임워크
- **Chart.js**: 아름다운 차트 라이브러리
- **SQLAlchemy**: 강력한 ORM

---

<div align="center">

**🚀 Made with ❤️ for MCP Learning & Innovation**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3.5-orange.svg)](https://anthropic.com)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**

</div>