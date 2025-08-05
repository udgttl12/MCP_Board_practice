"""
실제 Anthropic API를 사용하는 MCP 서버
"""

import json
import re
import asyncio
import time
from typing import Dict, Any, Optional, List
from anthropic import AsyncAnthropic
from config import config
from chart_generator import chart_generator
from mcp_logger import mcp_logger, log_mcp_warning, log_mcp_error

class RealMCPServer:
    """실제 Anthropic API를 사용하는 MCP 서버"""
    
    def __init__(self):
        self.chart_gen = chart_generator
        self.client: Optional[AsyncAnthropic] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Anthropic 클라이언트 초기화"""
        if config.is_api_key_configured():
            try:
                self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
                print("✅ Anthropic 클라이언트가 초기화되었습니다.")
            except Exception as e:
                print(f"❌ Anthropic 클라이언트 초기화 실패: {e}")
                self.client = None
        else:
            print("⚠️ API 키가 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.")
            self.client = None
    
    def is_real_mcp_available(self) -> bool:
        """실제 MCP 사용 가능 여부 확인"""
        return self.client is not None and config.is_api_key_configured()
    
    async def generate_multi_author_chart(self, author_names: List[str], chart_type: str = "bar") -> Dict[str, Any]:
        """
        여러 작성자의 데이터로 통합 차트 생성
        
        Args:
            author_names (List[str]): 작성자명 리스트
            chart_type (str): 차트 타입
        
        Returns:
            dict: 차트 생성 결과
        """
        start_time = time.time()
        
        await mcp_logger.log_api_call("generate_multi_author_chart", {
            "author_names": author_names,
            "chart_type": chart_type
        })
        
        try:
            if not author_names:
                return {
                    "success": False,
                    "message": "작성자가 지정되지 않았습니다.",
                    "chart_code": None,
                    "method": "validation_error"
                }
            
            # 차트 타입 유효성 검사
            if not self.chart_gen.validate_chart_type(chart_type):
                return {
                    "success": False,
                    "message": f"지원하지 않는 차트 타입입니다: {chart_type}",
                    "chart_code": None,
                    "method": "validation_error"
                }
            
            # 각 작성자의 데이터 수집
            all_author_data = []
            valid_authors = []
            
            for author in author_names:
                author_posts = self.chart_gen.get_author_numeric_data(author)
                if author_posts:
                    # 작성자 정보를 데이터에 추가
                    for post in author_posts:
                        post['author'] = author
                    all_author_data.extend(author_posts)
                    valid_authors.append(author)
            
            if not all_author_data:
                available_authors = self.chart_gen.get_available_authors()
                authors_str = ", ".join(available_authors) if available_authors else "없음"
                return {
                    "success": False,
                    "message": f"지정된 작성자들의 숫자 데이터를 찾을 수 없습니다: {', '.join(author_names)}. 사용 가능한 작성자: {authors_str}",
                    "chart_code": None,
                    "method": "no_data_found"
                }
            
            # AI 또는 기존 방식으로 다중 작성자 차트 코드 생성
            chart_result = await self.generate_multi_author_chart_code(all_author_data, chart_type, valid_authors)
            
            if not chart_result["success"]:
                return chart_result
            
            # 통합 요약 정보 생성
            summary = self._generate_multi_author_summary(valid_authors, all_author_data)
            
            method_msg = "🤖 AI로 생성됨" if chart_result["method"] == "ai_generated" else "⚙️ 로컬로 생성됨"
            
            # 성공 로그 기록
            duration_ms = (time.time() - start_time) * 1000
            await mcp_logger.log_chart_generation(chart_type, valid_authors, True, chart_result["method"], duration_ms)
            await mcp_logger.log_api_response("generate_multi_author_chart", True, duration_ms, {
                "authors": valid_authors,
                "chart_type": chart_type,
                "data_count": len(all_author_data),
                "method": chart_result["method"]
            })
            
            return {
                "success": True,
                "message": f"{method_msg} - {', '.join(valid_authors)} 작성자들의 {chart_type} 차트가 생성되었습니다.",
                "chart_code": chart_result["chart_code"],
                "data_count": len(all_author_data),
                "summary": summary,
                "method": chart_result["method"],
                "mcp_enabled": self.is_real_mcp_available(),
                "authors": valid_authors
            }
            
        except Exception as e:
            # 실패 로그 기록
            duration_ms = (time.time() - start_time) * 1000
            await mcp_logger.log_chart_generation(chart_type, author_names, False, "error", duration_ms)
            await mcp_logger.log_error("chart_generation", f"다중 작성자 차트 생성 실패: {str(e)}", {
                "author_names": author_names,
                "chart_type": chart_type
            })
            await mcp_logger.log_api_response("generate_multi_author_chart", False, duration_ms, {"error": str(e)})
            
            return {
                "success": False,
                "message": f"다중 작성자 차트 생성 중 오류가 발생했습니다: {str(e)}",
                "chart_code": None,
                "method": "error",
                "mcp_enabled": self.is_real_mcp_available()
            }
    
    async def parse_chart_command_with_ai(self, command: str) -> Dict[str, Any]:
        """
        AI를 사용해서 자연어 명령 파싱 (실제 MCP)
        """
        start_time = time.time()
        
        await mcp_logger.log_api_call("parse_chart_command", {"command": command})
        
        if not self.is_real_mcp_available():
            # 시뮬레이션 모드로 폴백
            await log_mcp_warning("parsing", "API 키 미설정으로 시뮬레이션 모드로 전환")
            return await self._parse_chart_command_fallback(command)
        
        try:
            prompt = f"""
다음 한국어 명령을 분석해서 차트 생성 정보를 추출해주세요:

명령: "{command}"

다음 JSON 형식으로 응답해주세요:
{{
    "author_names": ["작성자1", "작성자2"] 또는 null (여러 작성자 또는 없으면 null),
    "author_name": "단일 작성자명 (호환성용, 없으면 null)",
    "chart_type": "bar|line|pie|doughnut 중 하나",
    "valid": true/false,
    "confidence": 0.0-1.0,
    "explanation": "파싱 결과 설명",
    "is_multi_author": true/false
}}

차트 타입 매핑:
- 막대, 바, 막대그래프, 바차트 → "bar"
- 선그래프, 라인, 선형, 꺾은선 → "line"  
- 원그래프, 파이, 원형 → "pie"
- 도넛, 도너츠 → "doughnut"

작성자명 추출 규칙:
- 단일: "홍길동의", "김철수님의", "이영희 데이터" → author_name: "홍길동", is_multi_author: false
- 다중: "홍길동과 김철수", "홍길동, 김철수의", "홍길동 김철수 데이터" → author_names: ["홍길동", "김철수"], is_multi_author: true
- 없음: 작성자 언급 없음 → author_names: null, author_name: null, is_multi_author: false

여러 작성자가 감지되면 is_multi_author를 true로, author_names 배열에 모든 작성자를 포함하세요.
"""

            response = await self.client.messages.create(
                model=config.DEFAULT_MODEL,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # AI 응답 파싱
            ai_response = response.content[0].text.strip()
            
            # JSON 추출 시도
            try:
                # JSON 블록이 있는지 확인
                if "```json" in ai_response:
                    json_start = ai_response.find("```json") + 7
                    json_end = ai_response.find("```", json_start)
                    json_content = ai_response[json_start:json_end].strip()
                elif "{" in ai_response and "}" in ai_response:
                    json_start = ai_response.find("{")
                    json_end = ai_response.rfind("}") + 1
                    json_content = ai_response[json_start:json_end]
                else:
                    raise ValueError("JSON 형식을 찾을 수 없습니다")
                
                parsed_result = json.loads(json_content)
                
                # 결과 검증 및 보완
                author_names = parsed_result.get("author_names")
                author_name = parsed_result.get("author_name")
                is_multi_author = parsed_result.get("is_multi_author", False)
                
                # 호환성 처리: author_names가 있으면 우선, 없으면 author_name 사용
                if is_multi_author and author_names:
                    final_authors = author_names
                    final_single_author = None
                elif author_name:
                    final_authors = [author_name]
                    final_single_author = author_name
                else:
                    final_authors = None
                    final_single_author = None
                
                result = {
                    "author_names": final_authors,
                    "author_name": final_single_author,
                    "chart_type": parsed_result.get("chart_type", "bar"),
                    "valid": parsed_result.get("valid", False),
                    "confidence": parsed_result.get("confidence", 0.5),
                    "explanation": parsed_result.get("explanation", "AI가 분석한 결과"),
                    "method": "ai_powered",
                    "original_command": command,
                    "is_multi_author": is_multi_author
                }
                
                print(f"🤖 AI 파싱 결과: {result}")
                
                # 로그 기록
                duration_ms = (time.time() - start_time) * 1000
                await mcp_logger.log_parsing(command, result, duration_ms)
                await mcp_logger.log_api_response("parse_chart_command", True, duration_ms, result)
                
                return result
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"⚠️ AI 응답 파싱 실패: {e}")
                print(f"AI 응답: {ai_response}")
                
                # 로그 기록
                duration_ms = (time.time() - start_time) * 1000
                await mcp_logger.log_error("parsing", f"AI 응답 파싱 실패: {str(e)}", {"ai_response": ai_response[:200]})
                await mcp_logger.log_api_response("parse_chart_command", False, duration_ms, {"error": str(e)})
                
                # 폴백으로 기존 방식 사용
                return await self._parse_chart_command_fallback(command)
                
        except Exception as e:
            print(f"❌ AI 명령 파싱 중 오류: {e}")
            
            # 로그 기록
            duration_ms = (time.time() - start_time) * 1000
            await mcp_logger.log_error("parsing", f"AI 파싱 실패: {str(e)}")
            await mcp_logger.log_api_response("parse_chart_command", False, duration_ms, {"error": str(e)})
            
            # 폴백으로 기존 방식 사용
            return await self._parse_chart_command_fallback(command)
    
    async def _parse_chart_command_fallback(self, command: str) -> Dict[str, Any]:
        """기존 정규표현식 방식으로 폴백"""
        try:
            command = command.strip()
            
            # 작성자명 추출 패턴들
            author_patterns = [
                r'(\w+)의\s*(?:데이터|값|수치|글)',
                r'(\w+)\s*작성자',
                r'(\w+)\s*님',
                r'"([^"]+)"',
                r"'([^']+)'",
            ]
            
            author_name = None
            for pattern in author_patterns:
                match = re.search(pattern, command)
                if match:
                    author_name = match.group(1).strip()
                    break
            
            # 차트 타입 추출
            chart_type = "bar"
            chart_type_keywords = {
                "line": ["선그래프", "라인", "선형", "꺾은선"],
                "pie": ["원그래프", "파이", "원형"],
                "doughnut": ["도넛", "도너츠"],
                "bar": ["막대", "바", "막대그래프", "바차트"]
            }
            
            command_lower = command.lower()
            for ctype, keywords in chart_type_keywords.items():
                for keyword in keywords:
                    if keyword in command or keyword in command_lower:
                        chart_type = ctype
                        break
                if chart_type != "bar":
                    break
            
            # 다중 작성자 감지 시도
            multi_author_patterns = [
                r'(\w+)(?:과|와|,)\s*(\w+)',  # "홍길동과 김철수"
                r'(\w+)\s+(\w+)(?:\s+데이터|의)',  # "홍길동 김철수 데이터"
            ]
            
            author_names = []
            for pattern in multi_author_patterns:
                matches = re.findall(pattern, command)
                if matches:
                    for match in matches:
                        author_names.extend([name.strip() for name in match if name.strip()])
                    break
            
            # 중복 제거
            author_names = list(dict.fromkeys(author_names))
            
            is_multi_author = len(author_names) > 1
            
            return {
                "author_names": author_names if author_names else None,
                "author_name": author_names[0] if len(author_names) == 1 else None,
                "chart_type": chart_type,
                "valid": bool(author_names),
                "confidence": 0.8 if author_names else 0.0,
                "explanation": "정규표현식으로 파싱됨",
                "method": "regex_fallback",
                "original_command": command,
                "is_multi_author": is_multi_author
            }
            
        except Exception as e:
            return {
                "author_names": None,
                "author_name": None,
                "chart_type": "bar",
                "valid": False,
                "confidence": 0.0,
                "explanation": f"파싱 오류: {str(e)}",
                "method": "error",
                "original_command": command,
                "is_multi_author": False
            }
    
    async def generate_chart_code_with_ai(self, author_data: List[Dict], chart_type: str, author_name: str) -> Dict[str, Any]:
        """
        AI를 사용해서 Chart.js 코드 생성 (실제 MCP)
        """
        if not self.is_real_mcp_available():
            # 시뮬레이션 모드로 폴백
            chart_code = self.chart_gen.create_chart_js_code(author_data, chart_type)
            return {
                "success": True,
                "chart_code": chart_code,
                "method": "fallback",
                "message": "시뮬레이션 모드로 차트 생성됨"
            }
        
        try:
            # 데이터 준비
            labels = [post['title'] for post in author_data]
            values = [post['numeric_value'] for post in author_data if post['numeric_value'] is not None]
            
            if not values:
                values = [0] * len(labels)
            
            prompt = f"""
다음 데이터로 Chart.js 코드를 생성해주세요:

작성자: {author_name}
차트 타입: {chart_type}
라벨: {labels}
값: {values}

요구사항:
1. Chart.js 3.x 문법 사용
2. 기존 차트 제거 코드 포함 (window.myChart 확인)
3. 반응형 디자인
4. 한국어 제목과 라벨
5. 아름다운 색상 조합
6. 캔버스 ID는 'dynamicChart' 사용

다음 형식으로 완전한 JavaScript 코드를 생성해주세요:
```javascript
// 기존 차트 제거
if (window.myChart) {{
    window.myChart.destroy();
}}

// 새 차트 생성
const ctx = document.getElementById('dynamicChart').getContext('2d');
window.myChart = new Chart(ctx, {{
    // 차트 설정...
}});
```

응답은 JavaScript 코드만 반환해주세요.
"""

            response = await self.client.messages.create(
                model=config.DEFAULT_MODEL,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            ai_response = response.content[0].text.strip()
            
            # JavaScript 코드 추출
            if "```javascript" in ai_response:
                code_start = ai_response.find("```javascript") + 13
                code_end = ai_response.find("```", code_start)
                chart_code = ai_response[code_start:code_end].strip()
            elif "```js" in ai_response:
                code_start = ai_response.find("```js") + 5
                code_end = ai_response.find("```", code_start)
                chart_code = ai_response[code_start:code_end].strip()
            elif "```" in ai_response:
                code_start = ai_response.find("```") + 3
                code_end = ai_response.find("```", code_start)
                chart_code = ai_response[code_start:code_end].strip()
            else:
                chart_code = ai_response
            
            print(f"🤖 AI가 생성한 차트 코드 길이: {len(chart_code)} 문자")
            
            return {
                "success": True,
                "chart_code": chart_code,
                "method": "ai_generated",
                "message": f"AI가 {chart_type} 차트 코드를 생성했습니다"
            }
            
        except Exception as e:
            print(f"❌ AI 차트 코드 생성 실패: {e}")
            # 폴백으로 기존 방식 사용
            chart_code = self.chart_gen.create_chart_js_code(author_data, chart_type)
            return {
                "success": True,
                "chart_code": chart_code,
                "method": "fallback_after_ai_error",
                "message": f"AI 생성 실패로 기본 차트 생성됨: {str(e)}"
            }
    
    async def generate_multi_author_chart_code(self, author_data: List[Dict], chart_type: str, author_names: List[str]) -> Dict[str, Any]:
        """
        AI를 사용해서 다중 작성자 Chart.js 코드 생성
        """
        if not self.is_real_mcp_available():
            # 시뮬레이션 모드로 폴백
            chart_code = self._create_multi_author_chart_fallback(author_data, chart_type, author_names)
            return {
                "success": True,
                "chart_code": chart_code,
                "method": "fallback",
                "message": "시뮬레이션 모드로 다중 작성자 차트 생성됨"
            }
        
        try:
            # 작성자별 데이터 그룹화
            author_groups = {}
            for post in author_data:
                author = post.get('author', 'Unknown')
                if author not in author_groups:
                    author_groups[author] = []
                author_groups[author].append(post)
            
            # 차트 데이터 준비
            if chart_type in ['pie', 'doughnut']:
                # 원형/도넛 차트: 작성자별 총합
                labels = list(author_groups.keys())
                values = [sum(post['numeric_value'] for post in posts if post['numeric_value'] is not None) 
                         for posts in author_groups.values()]
            else:
                # 막대/선형 차트: 각 게시글별
                labels = [f"{post['author']}: {post['title']}" for post in author_data]
                values = [post['numeric_value'] for post in author_data if post['numeric_value'] is not None]
            
            if not values:
                values = [0] * len(labels)
            
            prompt = f"""
다음 다중 작성자 데이터로 Chart.js 코드를 생성해주세요:

작성자들: {', '.join(author_names)}
차트 타입: {chart_type}
라벨: {labels[:10]}...  # 처음 10개만 표시
값: {values[:10]}...

요구사항:
1. Chart.js 3.x 문법 사용
2. 기존 차트 제거 코드 포함 (window.myChart 확인)
3. 다중 작성자를 구분할 수 있는 색상 사용
4. 반응형 디자인
5. 한국어 제목과 라벨
6. 각 작성자별 구분되는 색상
7. 범례 표시
8. 캔버스 ID는 'dynamicChart' 사용

{chart_type} 차트의 경우:
- pie/doughnut: 작성자별 총합으로 표시
- bar/line: 모든 게시글을 작성자별 색상으로 구분

응답은 JavaScript 코드만 반환해주세요.
"""

            response = await self.client.messages.create(
                model=config.DEFAULT_MODEL,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            ai_response = response.content[0].text.strip()
            
            # JavaScript 코드 추출
            if "```javascript" in ai_response:
                code_start = ai_response.find("```javascript") + 13
                code_end = ai_response.find("```", code_start)
                chart_code = ai_response[code_start:code_end].strip()
            elif "```js" in ai_response:
                code_start = ai_response.find("```js") + 5
                code_end = ai_response.find("```", code_start)
                chart_code = ai_response[code_start:code_end].strip()
            elif "```" in ai_response:
                code_start = ai_response.find("```") + 3
                code_end = ai_response.find("```", code_start)
                chart_code = ai_response[code_start:code_end].strip()
            else:
                chart_code = ai_response
            
            print(f"🤖 AI가 생성한 다중 작성자 차트 코드 길이: {len(chart_code)} 문자")
            
            return {
                "success": True,
                "chart_code": chart_code,
                "method": "ai_generated",
                "message": f"AI가 {len(author_names)}명 작성자의 {chart_type} 차트 코드를 생성했습니다"
            }
            
        except Exception as e:
            print(f"❌ AI 다중 작성자 차트 코드 생성 실패: {e}")
            # 폴백으로 기존 방식 사용
            chart_code = self._create_multi_author_chart_fallback(author_data, chart_type, author_names)
            return {
                "success": True,
                "chart_code": chart_code,
                "method": "fallback_after_ai_error",
                "message": f"AI 생성 실패로 기본 다중 작성자 차트 생성됨: {str(e)}"
            }
    
    def _create_multi_author_chart_fallback(self, author_data: List[Dict], chart_type: str, author_names: List[str]) -> str:
        """다중 작성자 차트 코드 생성 (폴백)"""
        import json
        
        # 작성자별 데이터 그룹화
        author_groups = {}
        for post in author_data:
            author = post.get('author', 'Unknown')
            if author not in author_groups:
                author_groups[author] = []
            author_groups[author].append(post)
        
        # 색상 팔레트
        colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(199, 199, 199, 0.8)',
            'rgba(83, 102, 255, 0.8)'
        ]
        
        if chart_type in ['pie', 'doughnut']:
            # 원형 차트: 작성자별 총합
            labels = list(author_groups.keys())
            values = [sum(post['numeric_value'] for post in posts if post['numeric_value'] is not None) 
                     for posts in author_groups.values()]
            background_colors = colors[:len(labels)]
            
            chart_code = f"""
            if (window.myChart) {{
                window.myChart.destroy();
            }}
            
            const ctx = document.getElementById('dynamicChart').getContext('2d');
            window.myChart = new Chart(ctx, {{
                type: '{chart_type}',
                data: {{
                    labels: {json.dumps(labels, ensure_ascii=False)},
                    datasets: [{{
                        data: {json.dumps(values)},
                        backgroundColor: {json.dumps(background_colors)},
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '다중 작성자 데이터 차트 ({", ".join(author_names)})'
                        }},
                        legend: {{
                            display: true,
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            """
        else:
            # 막대/선형 차트: 데이터셋별 작성자 구분
            datasets = []
            for i, (author, posts) in enumerate(author_groups.items()):
                labels_for_author = [post['title'] for post in posts]
                values_for_author = [post['numeric_value'] for post in posts if post['numeric_value'] is not None]
                
                datasets.append({
                    "label": author,
                    "data": values_for_author,
                    "backgroundColor": colors[i % len(colors)],
                    "borderColor": colors[i % len(colors)].replace('0.8', '1'),
                    "borderWidth": 2
                })
            
            all_labels = [post['title'] for post in author_data]
            
            chart_code = f"""
            if (window.myChart) {{
                window.myChart.destroy();
            }}
            
            const ctx = document.getElementById('dynamicChart').getContext('2d');
            window.myChart = new Chart(ctx, {{
                type: '{chart_type}',
                data: {{
                    labels: {json.dumps(all_labels, ensure_ascii=False)},
                    datasets: {json.dumps(datasets, ensure_ascii=False)}
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '다중 작성자 데이터 차트 ({", ".join(author_names)})'
                        }},
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '값'
                            }}
                        }}
                    }}
                }}
            }});
            """
        
        return chart_code
    
    def _generate_multi_author_summary(self, author_names: List[str], all_data: List[Dict]) -> Dict[str, Any]:
        """다중 작성자 요약 정보 생성"""
        if not all_data:
            return {
                "authors": author_names,
                "total_authors": len(author_names),
                "total_posts": 0,
                "total_value": 0,
                "average_value": 0,
                "author_breakdown": {}
            }
        
        # 작성자별 통계
        author_stats = {}
        for author in author_names:
            author_posts = [post for post in all_data if post.get('author') == author]
            values = [post['numeric_value'] for post in author_posts if post['numeric_value'] is not None]
            
            author_stats[author] = {
                "posts": len(author_posts),
                "total_value": round(sum(values), 2) if values else 0,
                "average_value": round(sum(values) / len(values), 2) if values else 0,
                "max_value": max(values) if values else 0,
                "min_value": min(values) if values else 0
            }
        
        # 전체 통계
        all_values = [post['numeric_value'] for post in all_data if post['numeric_value'] is not None]
        
        return {
            "authors": author_names,
            "total_authors": len(author_names),
            "total_posts": len(all_data),
            "total_value": round(sum(all_values), 2) if all_values else 0,
            "average_value": round(sum(all_values) / len(all_values), 2) if all_values else 0,
            "author_breakdown": author_stats
            }
    
    async def generate_author_chart(self, author_name: str, chart_type: str = "bar") -> Dict[str, Any]:
        """
        통합 차트 생성 메서드 (AI + 기존 로직)
        """
        start_time = time.time()
        
        await mcp_logger.log_api_call("generate_author_chart", {
            "author_name": author_name,
            "chart_type": chart_type
        })
        
        try:
            # 차트 타입 유효성 검사
            if not self.chart_gen.validate_chart_type(chart_type):
                return {
                    "success": False,
                    "message": f"지원하지 않는 차트 타입입니다: {chart_type}",
                    "chart_code": None,
                    "method": "validation_error"
                }
            
            # 작성자 데이터 조회
            author_posts = self.chart_gen.get_author_numeric_data(author_name)
            
            if not author_posts:
                available_authors = self.chart_gen.get_available_authors()
                authors_str = ", ".join(available_authors) if available_authors else "없음"
                return {
                    "success": False,
                    "message": f"'{author_name}' 작성자의 숫자 데이터를 찾을 수 없습니다. 사용 가능한 작성자: {authors_str}",
                    "chart_code": None,
                    "method": "no_data_found"
                }
            
            # AI 또는 기존 방식으로 차트 코드 생성
            chart_result = await self.generate_chart_code_with_ai(author_posts, chart_type, author_name)
            
            if not chart_result["success"]:
                return chart_result
            
            # 차트 요약 정보 생성
            summary = self.chart_gen.generate_chart_summary(author_name, author_posts)
            
            method_msg = "🤖 AI로 생성됨" if chart_result["method"] == "ai_generated" else "⚙️ 로컬로 생성됨"
            
            # 성공 로그 기록
            duration_ms = (time.time() - start_time) * 1000
            await mcp_logger.log_chart_generation(chart_type, [author_name], True, chart_result["method"], duration_ms)
            await mcp_logger.log_api_response("generate_author_chart", True, duration_ms, {
                "author_name": author_name,
                "chart_type": chart_type,
                "data_count": len(author_posts),
                "method": chart_result["method"]
            })
            
            return {
                "success": True,
                "message": f"{method_msg} - '{author_name}' 작성자의 {chart_type} 차트가 생성되었습니다.",
                "chart_code": chart_result["chart_code"],
                "data_count": len(author_posts),
                "summary": summary,
                "method": chart_result["method"],
                "mcp_enabled": self.is_real_mcp_available()
            }
            
        except Exception as e:
            # 실패 로그 기록
            duration_ms = (time.time() - start_time) * 1000
            await mcp_logger.log_chart_generation(chart_type, [author_name], False, "error", duration_ms)
            await mcp_logger.log_error("chart_generation", f"차트 생성 실패: {str(e)}", {
                "author_name": author_name,
                "chart_type": chart_type
            })
            await mcp_logger.log_api_response("generate_author_chart", False, duration_ms, {"error": str(e)})
            
            return {
                "success": False,
                "message": f"차트 생성 중 오류가 발생했습니다: {str(e)}",
                "chart_code": None,
                "method": "error",
                "mcp_enabled": self.is_real_mcp_available()
            }
    
    async def get_api_status(self) -> Dict[str, Any]:
        """API 상태 확인"""
        status = {
            "api_key_configured": config.is_api_key_configured(),
            "client_initialized": self.client is not None,
            "mcp_available": self.is_real_mcp_available(),
            "model": config.DEFAULT_MODEL,
            "mode": "AI-Powered MCP" if self.is_real_mcp_available() else "Simulation Mode"
        }
        
        if self.is_real_mcp_available():
            try:
                # 간단한 API 테스트
                test_response = await self.client.messages.create(
                    model=config.DEFAULT_MODEL,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "안녕하세요"}]
                )
                status["api_test"] = "✅ 성공"
                status["api_response_length"] = len(test_response.content[0].text)
            except Exception as e:
                status["api_test"] = f"❌ 실패: {str(e)}"
        
        return status

# 전역 실제 MCP 서버 인스턴스
real_mcp_server = RealMCPServer()

# 호환성을 위한 함수들
async def generate_author_chart(author_name: str, chart_type: str = "bar"):
    """실제 MCP 차트 생성"""
    return await real_mcp_server.generate_author_chart(author_name, chart_type)

async def parse_chart_command(command: str):
    """실제 MCP 명령 파싱"""
    return await real_mcp_server.parse_chart_command_with_ai(command)

async def get_mcp_status():
    """MCP 상태 확인"""
    return await real_mcp_server.get_api_status()

# 테스트용 코드
if __name__ == "__main__":
    import asyncio
    
    async def test_real_mcp():
        print("=== 실제 MCP 서버 테스트 ===")
        
        # API 상태 확인
        status = await get_mcp_status()
        print(f"MCP 상태: {status}")
        
        if real_mcp_server.is_real_mcp_available():
            print("\n=== AI 명령 파싱 테스트 ===")
            test_command = "홍길동의 데이터를 막대차트로 보여줘"
            result = await parse_chart_command(test_command)
            print(f"파싱 결과: {result}")
            
            print("\n=== AI 차트 생성 테스트 ===")
            if result.get("valid"):
                chart_result = await generate_author_chart(result["author_name"], result["chart_type"])
                print(f"차트 생성: {chart_result['success']}")
                print(f"메시지: {chart_result['message']}")
        else:
            print("⚠️ API 키가 설정되지 않아 시뮬레이션 모드로 실행됩니다.")
    
    # 테스트 실행
    asyncio.run(test_real_mcp())