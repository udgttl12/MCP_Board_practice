# MCP 게시판 프로젝트 구현 가이드

## 프로젝트 개요
- **목적**: MCP(Model Context Protocol)를 활용한 게시판에서 차트 자동 생성 기능 구현
- **핵심 기능**: 특정 작성자의 숫자 데이터를 Chart.js로 시각화
- **기술 스택**: Python, FastAPI, MCP, Chart.js, SQLite

## 준비사항

### 1. 필요한 패키지 설치
```bash
# MCP 관련 패키지
pip install mcp
pip install anthropic  # Claude API 사용시 (선택사항)

# 웹 프레임워크
pip install fastapi uvicorn

# 데이터베이스
pip install sqlalchemy sqlite3

# 추가 도구
pip install websockets  # 실시간 통신용 (선택사항)
```

### 2. 프로젝트 폴더 구조
```
mcp_board/
├── app.py                 # FastAPI 메인 애플리케이션
├── mcp_server.py          # MCP 서버 구성
├── database.py            # 데이터베이스 모델
├── chart_generator.py     # 차트 생성 로직
├── templates/
│   ├── index.html         # 게시판 메인 페이지
│   └── post.html          # 게시글 작성 페이지
└── static/
    ├── style.css          # CSS 스타일
    └── app.js             # 프론트엔드 JavaScript
```

## 데이터베이스 설계

### 게시글 테이블 구조
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

## 핵심 구현 코드

### 1. 차트 생성기 (chart_generator.py)
```python
class ChartGenerator:
    def create_chart_js_code(self, author_data, chart_type="bar"):
        """
        작성자 데이터를 받아서 Chart.js 코드를 동적으로 생성
        """
        labels = [f"게시글 {i+1}" for i in range(len(author_data))]
        values = [post['numeric_value'] for post in author_data]
        
        chart_code = f"""
        // 기존 차트가 있다면 제거
        if (window.myChart) {{
            window.myChart.destroy();
        }}
        
        const ctx = document.getElementById('dynamicChart').getContext('2d');
        window.myChart = new Chart(ctx, {{
            type: '{chart_type}',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: '수치 데이터',
                    data: {values},
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '작성자별 데이터 차트'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        """
        return chart_code
    
    def get_author_numeric_data(self, author_name):
        """
        특정 작성자의 숫자 데이터를 데이터베이스에서 조회
        """
        # 실제 구현에서는 데이터베이스 쿼리 실행
        # 예시 데이터
        return [
            {'id': 1, 'numeric_value': 100, 'title': '첫 번째 글'},
            {'id': 2, 'numeric_value': 150, 'title': '두 번째 글'},
            {'id': 3, 'numeric_value': 200, 'title': '세 번째 글'}
        ]
```

### 2. MCP 서버 구성 (mcp_server.py)
```python
from mcp import Tool, Server
from chart_generator import ChartGenerator

server = Server("board-mcp")
chart_generator = ChartGenerator()

@server.tool("generate_author_chart")
async def generate_author_chart(author_name: str, chart_type: str = "bar"):
    """
    특정 작성자의 숫자 데이터로 차트 생성
    
    Args:
        author_name: 차트를 생성할 작성자명
        chart_type: 차트 타입 (bar, line, pie 등)
    
    Returns:
        dict: 성공 여부, 차트 코드, 데이터 개수
    """
    try:
        # 작성자의 데이터 조회
        author_posts = chart_generator.get_author_numeric_data(author_name)
        
        if not author_posts:
            return {
                "success": False,
                "message": f"'{author_name}' 작성자의 데이터를 찾을 수 없습니다.",
                "chart_code": None
            }
        
        # Chart.js 코드 생성
        chart_code = chart_generator.create_chart_js_code(author_posts, chart_type)
        
        return {
            "success": True,
            "message": f"'{author_name}' 작성자의 차트가 생성되었습니다.",
            "chart_code": chart_code,
            "data_count": len(author_posts)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"차트 생성 중 오류가 발생했습니다: {str(e)}",
            "chart_code": None
        }

@server.tool("parse_chart_command")
async def parse_chart_command(command: str):
    """
    자연어 명령을 파싱해서 차트 생성 파라미터 추출
    
    Args:
        command: 사용자가 입력한 자연어 명령
        
    Returns:
        dict: 파싱된 작성자명과 차트 타입
    """
    import re
    
    # 작성자명 추출 (예: "홍길동의 데이터를...")
    author_match = re.search(r'(\w+)의\s*(?:데이터|값|수치)', command)
    author_name = author_match.group(1) if author_match else None
    
    # 차트 타입 추출
    chart_type = "bar"  # 기본값
    if "선그래프" in command or "라인" in command:
        chart_type = "line"
    elif "원그래프" in command or "파이" in command:
        chart_type = "pie"
    elif "막대" in command or "바" in command:
        chart_type = "bar"
    
    return {
        "author_name": author_name,
        "chart_type": chart_type,
        "valid": author_name is not None
    }
```

### 3. FastAPI 메인 애플리케이션 (app.py)
```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mcp_server import generate_author_chart, parse_chart_command
import uvicorn

app = FastAPI(title="MCP 게시판")

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def main_page(request: Request):
    """메인 게시판 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-chart")
async def create_chart(request: dict):
    """차트 생성 API 엔드포인트"""
    command = request.get('command', '')
    
    # 명령어 파싱
    parsed = await parse_chart_command(command)
    
    if not parsed['valid']:
        return {
            "success": False,
            "message": "작성자명을 찾을 수 없습니다. 예: '홍길동의 데이터를 차트로 보여줘'"
        }
    
    # MCP 도구를 통해 차트 생성
    result = await generate_author_chart(
        parsed['author_name'], 
        parsed['chart_type']
    )
    
    return result

@app.post("/add-post")
async def add_post(request: dict):
    """게시글 추가 API"""
    # 실제 구현에서는 데이터베이스에 저장
    return {"success": True, "message": "게시글이 추가되었습니다."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. 웹페이지 템플릿 (templates/index.html)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP 게시판</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>MCP 게시판</h1>
        
        <!-- 게시글 작성 폼 -->
        <div class="post-form">
            <h2>게시글 작성</h2>
            <input type="text" id="author" placeholder="작성자명" required>
            <input type="text" id="title" placeholder="제목" required>
            <textarea id="content" placeholder="내용"></textarea>
            <input type="number" id="numericValue" placeholder="숫자값 (차트용)" step="0.1">
            <button onclick="addPost()">게시글 작성</button>
        </div>
        
        <!-- 차트 생성 명령 -->
        <div class="chart-command">
            <h2>차트 생성</h2>
            <input type="text" id="command" placeholder="예: 홍길동의 데이터를 막대차트로 보여줘" size="50">
            <button onclick="executeCommand()">차트 생성</button>
        </div>
        
        <!-- 결과 메시지 -->
        <div id="message" class="message"></div>
        
        <!-- 차트 표시 영역 -->
        <div class="chart-container">
            <canvas id="dynamicChart" width="400" height="200"></canvas>
        </div>
        
        <!-- 게시글 목록 -->
        <div class="post-list">
            <h2>게시글 목록</h2>
            <div id="posts"></div>
        </div>
    </div>
    
    <script>
        // 전역 차트 변수
        let currentChart = null;
        
        async function executeCommand() {
            const command = document.getElementById('command').value.trim();
            const messageDiv = document.getElementById('message');
            
            if (!command) {
                showMessage('명령어를 입력해주세요.', 'error');
                return;
            }
            
            showMessage('차트를 생성하고 있습니다...', 'info');
            
            try {
                // MCP 서버에 차트 생성 요청
                const response = await fetch('/generate-chart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({command: command})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // 기존 차트 제거
                    if (currentChart) {
                        currentChart.destroy();
                    }
                    
                    // MCP에서 생성된 Chart.js 코드 실행
                    eval(result.chart_code);
                    
                    showMessage(result.message, 'success');
                } else {
                    showMessage(result.message, 'error');
                }
                
            } catch (error) {
                showMessage('차트 생성 중 오류가 발생했습니다: ' + error.message, 'error');
            }
        }
        
        async function addPost() {
            const author = document.getElementById('author').value;
            const title = document.getElementById('title').value;
            const content = document.getElementById('content').value;
            const numericValue = document.getElementById('numericValue').value;
            
            if (!author || !title) {
                showMessage('작성자와 제목은 필수입니다.', 'error');
                return;
            }
            
            try {
                const response = await fetch('/add-post', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        author: author,
                        title: title,
                        content: content,
                        numeric_value: parseFloat(numericValue) || 0
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('게시글이 작성되었습니다.', 'success');
                    // 폼 초기화
                    document.getElementById('author').value = '';
                    document.getElementById('title').value = '';
                    document.getElementById('content').value = '';
                    document.getElementById('numericValue').value = '';
                } else {
                    showMessage('게시글 작성에 실패했습니다.', 'error');
                }
                
            } catch (error) {
                showMessage('게시글 작성 중 오류가 발생했습니다: ' + error.message, 'error');
            }
        }
        
        function showMessage(message, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = message;
            messageDiv.className = 'message ' + type;
            
            // 3초 후 메시지 자동 제거
            setTimeout(() => {
                messageDiv.textContent = '';
                messageDiv.className = 'message';
            }, 3000);
        }
        
        // 엔터 키로 명령 실행
        document.getElementById('command').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeCommand();
            }
        });
    </script>
</body>
</html>
```

### 5. CSS 스타일 (static/style.css)
```css
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
}

.post-form, .chart-command {
    background: #f5f5f5;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
}

.post-form input, .post-form textarea, .chart-command input {
    width: 100%;
    padding: 10px;
    margin: 5px 0;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
}

.post-form textarea {
    height: 100px;
    resize: vertical;
}

button {
    background: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 10px 0;
}

button:hover {
    background: #0056b3;
}

.message {
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

.message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.message.info {
    background: #cce7ff;
    color: #004085;
    border: 1px solid #99d1ff;
}

.chart-container {
    background: white;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.post-list {
    margin-top: 30px;
}

h1, h2 {
    color: #333;
}
```

## 실행 방법

### 1. 프로젝트 실행
```bash
# 가상환경 생성 (선택사항)
python -m venv mcp_env
source mcp_env/bin/activate  # Windows: mcp_env\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

### 2. 브라우저에서 접속
```
http://localhost:8000
```

## 사용 예시

### 게시글 작성
1. 작성자: 홍길동
2. 제목: 1월 매출 보고
3. 숫자값: 150

### 차트 생성 명령
- "홍길동의 데이터를 막대차트로 보여줘"
- "김철수의 값을 선그래프로 표시해줘"
- "이영희의 수치를 원그래프로 만들어줘"

## MCP의 핵심 개념 학습 포인트

1. **도구 연결**: 데이터베이스 조회 + 차트 생성 + 웹 표시
2. **자동화**: 자연어 명령 → 데이터 분석 → 코드 생성
3. **통합**: 여러 컴포넌트가 MCP를 통해 협력
4. **확장성**: 새로운 차트 타입이나 기능을 쉽게 추가 가능

이 프로젝트를 통해 MCP가 어떻게 여러 도구를 연결하고 자동화하는지 직접 체험할 수 있습니다!