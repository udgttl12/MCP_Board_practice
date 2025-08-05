"""
MCP 서버 구성
"""

import re
from chart_generator import chart_generator

class MCPServer:
    """MCP 서버 시뮬레이션 클래스"""
    
    def __init__(self):
        self.chart_gen = chart_generator
    
    async def generate_author_chart(self, author_name: str, chart_type: str = "bar"):
        """
        특정 작성자의 숫자 데이터로 차트 생성
        
        Args:
            author_name (str): 차트를 생성할 작성자명
            chart_type (str): 차트 타입 (bar, line, pie 등)
        
        Returns:
            dict: 성공 여부, 차트 코드, 데이터 개수
        """
        try:
            # 차트 타입 유효성 검사
            if not self.chart_gen.validate_chart_type(chart_type):
                return {
                    "success": False,
                    "message": f"지원하지 않는 차트 타입입니다: {chart_type}",
                    "chart_code": None,
                    "summary": None
                }
            
            # 작성자의 데이터 조회
            author_posts = self.chart_gen.get_author_numeric_data(author_name)
            
            if not author_posts:
                available_authors = self.chart_gen.get_available_authors()
                authors_str = ", ".join(available_authors) if available_authors else "없음"
                return {
                    "success": False,
                    "message": f"'{author_name}' 작성자의 숫자 데이터를 찾을 수 없습니다. 사용 가능한 작성자: {authors_str}",
                    "chart_code": None,
                    "summary": None
                }
            
            # Chart.js 코드 생성
            chart_code = self.chart_gen.create_chart_js_code(author_posts, chart_type)
            
            # 차트 요약 정보 생성
            summary = self.chart_gen.generate_chart_summary(author_name, author_posts)
            
            return {
                "success": True,
                "message": f"'{author_name}' 작성자의 {chart_type} 차트가 생성되었습니다.",
                "chart_code": chart_code,
                "data_count": len(author_posts),
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"차트 생성 중 오류가 발생했습니다: {str(e)}",
                "chart_code": None,
                "summary": None
            }
    
    async def parse_chart_command(self, command: str):
        """
        자연어 명령을 파싱해서 차트 생성 파라미터 추출
        
        Args:
            command (str): 사용자가 입력한 자연어 명령
            
        Returns:
            dict: 파싱된 작성자명과 차트 타입
        """
        try:
            command = command.strip()
            
            # 작성자명 추출 패턴들
            author_patterns = [
                r'(\w+)의\s*(?:데이터|값|수치|글)',  # "홍길동의 데이터"
                r'(\w+)\s*작성자',  # "홍길동 작성자"
                r'(\w+)\s*님',      # "홍길동님"
                r'"([^"]+)"',       # "홍길동" (따옴표로 감싼 경우)
                r"'([^']+)'",       # '홍길동' (따옴표로 감싼 경우)
            ]
            
            author_name = None
            for pattern in author_patterns:
                match = re.search(pattern, command)
                if match:
                    author_name = match.group(1).strip()
                    break
            
            # 차트 타입 추출
            chart_type = "bar"  # 기본값
            
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
                if chart_type != "bar":  # 기본값이 아닌 타입을 찾았으면 중단
                    break
            
            # 명령어 유효성 검사
            is_valid = author_name is not None and len(author_name) > 0
            
            return {
                "author_name": author_name,
                "chart_type": chart_type,
                "valid": is_valid,
                "parsed_command": {
                    "original": command,
                    "extracted_author": author_name,
                    "extracted_chart_type": chart_type
                }
            }
            
        except Exception as e:
            return {
                "author_name": None,
                "chart_type": "bar",
                "valid": False,
                "error": f"명령어 파싱 중 오류: {str(e)}"
            }
    
    async def get_available_authors(self):
        """사용 가능한 작성자 목록 반환"""
        try:
            authors = self.chart_gen.get_available_authors()
            return {
                "success": True,
                "authors": authors,
                "count": len(authors)
            }
        except Exception as e:
            return {
                "success": False,
                "authors": [],
                "count": 0,
                "error": str(e)
            }
    
    async def get_chart_types(self):
        """지원하는 차트 타입 목록 반환"""
        return {
            "chart_types": [
                {"type": "bar", "name": "막대차트", "description": "막대 형태로 데이터를 표시"},
                {"type": "line", "name": "선그래프", "description": "선으로 연결된 데이터 포인트"},
                {"type": "pie", "name": "원그래프", "description": "원형 섹터로 비율 표시"},
                {"type": "doughnut", "name": "도넛차트", "description": "중앙이 비어있는 원형 차트"}
            ],
            "keywords": {
                "bar": ["막대", "바", "막대그래프", "바차트"],
                "line": ["선그래프", "라인", "선형", "꺾은선"],
                "pie": ["원그래프", "파이", "원형"],
                "doughnut": ["도넛", "도너츠"]
            }
        }
    
    async def test_command_parsing(self, test_commands):
        """명령어 파싱 테스트 (개발용)"""
        results = []
        for command in test_commands:
            parsed = await self.parse_chart_command(command)
            results.append({
                "command": command,
                "parsed": parsed
            })
        return results

# 전역 MCP 서버 인스턴스
mcp_server = MCPServer()

# MCP 도구들 (FastAPI에서 사용할 함수들)
async def generate_author_chart(author_name: str, chart_type: str = "bar"):
    """MCP 도구: 작성자별 차트 생성"""
    return await mcp_server.generate_author_chart(author_name, chart_type)

async def parse_chart_command(command: str):
    """MCP 도구: 자연어 명령 파싱"""
    return await mcp_server.parse_chart_command(command)

async def get_available_authors():
    """MCP 도구: 사용 가능한 작성자 목록"""
    return await mcp_server.get_available_authors()

async def get_chart_types():
    """MCP 도구: 지원하는 차트 타입 목록"""
    return await mcp_server.get_chart_types()

# 테스트용 코드
if __name__ == "__main__":
    import asyncio
    
    async def test_mcp_server():
        # 명령어 파싱 테스트
        test_commands = [
            "홍길동의 데이터를 막대차트로 보여줘",
            "김철수의 값을 선그래프로 표시해줘",
            "이영희의 수치를 원그래프로 만들어줘",
            "홍길동님 데이터 차트",
            "잘못된 명령어"
        ]
        
        print("=== 명령어 파싱 테스트 ===")
        for command in test_commands:
            result = await parse_chart_command(command)
            print(f"명령어: {command}")
            print(f"결과: {result}")
            print("-" * 50)
        
        print("\n=== 차트 생성 테스트 ===")
        chart_result = await generate_author_chart("홍길동", "bar")
        print(f"차트 생성 결과: {chart_result['success']}")
        print(f"메시지: {chart_result['message']}")
        
        print("\n=== 사용 가능한 작성자 ===")
        authors_result = await get_available_authors()
        print(f"작성자 목록: {authors_result}")
    
    # 테스트 실행
    asyncio.run(test_mcp_server())