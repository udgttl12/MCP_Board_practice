# 🚀 MCP 게시판 프로젝트

> **MCP(Model Context Protocol)를 활용한 게시판에서 차트 자동 생성 기능**

이 프로젝트는 특정 작성자의 숫자 데이터를 Chart.js로 시각화하는 게시판 시스템입니다.

## ✨ 주요 기능

- 📝 **게시글 작성**: 작성자, 제목, 내용과 함께 차트용 숫자 데이터 입력
- 📊 **자동 차트 생성**: 자연어 명령으로 특정 작성자의 데이터를 다양한 차트로 시각화
- 🎨 **다양한 차트 타입**: 막대차트, 선그래프, 원그래프, 도넛차트 지원
- 🔍 **실시간 데이터 조회**: 작성자별 게시글 및 통계 정보 표시
- 📱 **반응형 디자인**: 모바일과 데스크톱 모두 지원

## 🛠️ 기술 스택

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **MCP**: Model Context Protocol 시뮬레이션
- **Database**: SQLite (개발용)

## 📦 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd mcp_board
```

### 2. 의존성 설치
```bash
# 방법 1: run.py 스크립트 사용
python run.py install

# 방법 2: 직접 설치
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
# 방법 1: run.py 스크립트 사용 (권장)
python run.py

# 방법 2: 직접 실행
python app.py
```

### 4. 브라우저에서 접속
```
http://localhost:8000
```

## 🎯 사용 방법

### 게시글 작성
1. **작성자명**: 차트 생성에 사용될 작성자명 입력
2. **제목**: 게시글 제목 입력
3. **내용**: 게시글 내용 (선택사항)
4. **숫자값**: 차트에 표시될 숫자 데이터
5. **카테고리**: 게시글 분류 (선택사항)

### 차트 생성 명령어
자연어로 명령을 입력하면 MCP가 파싱하여 자동으로 차트를 생성합니다.

**명령어 예시:**
- `"홍길동의 데이터를 막대차트로 보여줘"`
- `"김철수의 값을 선그래프로 표시해줘"`
- `"이영희의 수치를 원그래프로 만들어줘"`

**지원하는 차트 타입:**
- **막대차트**: 막대, 바, 막대그래프, 바차트
- **선그래프**: 선그래프, 라인, 선형, 꺾은선
- **원그래프**: 원그래프, 파이, 원형
- **도넛차트**: 도넛, 도너츠

## 📁 프로젝트 구조

```
mcp_board/
├── app.py                 # FastAPI 메인 애플리케이션
├── mcp_server.py          # MCP 서버 시뮬레이션
├── database.py            # 데이터베이스 모델 및 관리
├── chart_generator.py     # 차트 생성 로직
├── run.py                 # 실행 스크립트
├── requirements.txt       # 의존성 패키지 목록
├── README.md             # 프로젝트 문서
├── readme.txt            # 원본 구현 가이드
├── templates/
│   └── index.html        # 메인 웹페이지 템플릿
└── static/
    └── style.css         # CSS 스타일시트
```

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

### 웹페이지
- `GET /` - 메인 게시판 페이지

### 게시글 관리
- `POST /add-post` - 게시글 추가
- `GET /posts` - 모든 게시글 조회
- `GET /posts/author/{author_name}` - 특정 작성자 게시글 조회

### 차트 기능
- `POST /generate-chart` - 차트 생성
- `GET /authors` - 사용 가능한 작성자 목록
- `GET /chart-types` - 지원하는 차트 타입 목록

### 기타
- `GET /health` - 서버 상태 확인
- `GET /test/mcp` - MCP 기능 테스트 (개발용)

## 🎨 주요 특징

### MCP 통합
- **자연어 명령 파싱**: 사용자의 자연어 입력을 분석하여 차트 생성 파라미터 추출
- **동적 차트 생성**: Chart.js 코드를 실시간으로 생성하여 웹페이지에 적용
- **데이터 통합**: 데이터베이스, 차트 생성, 웹 표시가 MCP를 통해 연결

### 사용자 경험
- **직관적 인터페이스**: 명확한 폼과 명령어 입력
- **실시간 피드백**: 차트 생성 결과와 오류 메시지 즉시 표시
- **반응형 디자인**: 다양한 디바이스에서 최적화된 경험

### 개발자 친화적
- **모듈화 구조**: 각 기능이 독립적인 모듈로 분리
- **확장 가능**: 새로운 차트 타입이나 기능을 쉽게 추가
- **테스트 지원**: 개발용 테스트 엔드포인트 제공

## 🔄 개발 워크플로우

1. **데이터 입력**: 사용자가 게시글과 숫자 데이터 입력
2. **명령 파싱**: MCP가 자연어 명령을 분석
3. **데이터 조회**: 데이터베이스에서 해당 작성자의 데이터 검색
4. **차트 생성**: Chart.js 코드 동적 생성
5. **결과 표시**: 웹페이지에 차트와 통계 정보 표시

## 🐛 문제 해결

### 일반적인 문제
1. **패키지 설치 오류**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **포트 충돌**
   - 8000번 포트가 사용 중인 경우 app.py에서 포트 번호 변경

3. **데이터베이스 오류**
   - `board.db` 파일 삭제 후 서버 재시작

### 개발 모드
```bash
# 디버그 모드로 실행 (파일 변경 시 자동 재시작)
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📈 확장 가능성

- **실시간 업데이트**: WebSocket을 통한 실시간 차트 업데이트
- **사용자 인증**: 로그인 시스템 추가
- **데이터 내보내기**: 차트 이미지나 데이터 CSV 내보내기
- **고급 차트**: 더 복잡한 차트 타입 지원
- **AI 분석**: 데이터 트렌드 자동 분석 및 인사이트 제공

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Made with ❤️ for MCP Learning**