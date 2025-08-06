"""
MCP 게시판 설정 파일
"""

import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """애플리케이션 설정 클래스"""
    
    def __init__(self):
        # .env 파일 로드 (존재하는 경우)
        load_dotenv()
        
        # Anthropic API 키 (환경변수 또는 직접 설정)
        self.ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        
        # 데이터베이스 설정
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///board.db")
        
        # 서버 설정
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
        
        # MCP 설정
        self.MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "true").lower() == "true"
        self.DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
        
        # 보안 설정
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "mcp_board_secret_key_2024")
    
    def set_anthropic_api_key(self, api_key: str):
        """Anthropic API 키 설정"""
        self.ANTHROPIC_API_KEY = api_key
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    def is_api_key_configured(self) -> bool:
        """API 키가 설정되어 있는지 확인"""
        return self.ANTHROPIC_API_KEY is not None and len(self.ANTHROPIC_API_KEY.strip()) > 0
    
    def get_api_key_prompt(self) -> str:
        """API 키 입력 안내 메시지"""
        return """
🔑 Anthropic API 키가 필요합니다!

1. https://console.anthropic.com/ 에서 계정 생성
2. API 키 발급 (Credits 구매 필요)
3. 다음 중 한 가지 방법으로 API 키 설정:

방법 1 - 환경변수 설정:
   export ANTHROPIC_API_KEY="your_api_key_here"

방법 2 - config.py에서 직접 설정:
   config.set_anthropic_api_key("your_api_key_here")

방법 3 - 웹 인터페이스에서 설정 (곧 추가 예정)

현재 상태: ❌ API 키 미설정
"""

# 전역 설정 인스턴스
config = Config()

# API 키 설정 헬퍼 함수
def setup_api_key():
    """대화형 API 키 설정"""
    if not config.is_api_key_configured():
        print(config.get_api_key_prompt())
        
        # 사용자 입력 받기
        try:
            api_key = input("Anthropic API 키를 입력하세요 (Enter로 건너뛰기): ").strip()
            if api_key:
                config.set_anthropic_api_key(api_key)
                print("✅ API 키가 설정되었습니다!")
                return True
            else:
                print("⚠️ API 키를 건너뛰었습니다. 시뮬레이션 모드로 실행됩니다.")
                return False
        except KeyboardInterrupt:
            print("\n⚠️ API 키 설정을 취소했습니다. 시뮬레이션 모드로 실행됩니다.")
            return False
    return True

if __name__ == "__main__":
    # 설정 테스트
    print("=== MCP 게시판 설정 ===")
    print(f"HOST: {config.HOST}")
    print(f"PORT: {config.PORT}")
    print(f"DATABASE_URL: {config.DATABASE_URL}")
    print(f"MCP_ENABLED: {config.MCP_ENABLED}")
    print(f"API 키 설정됨: {config.is_api_key_configured()}")
    
    if not config.is_api_key_configured():
        setup_api_key()