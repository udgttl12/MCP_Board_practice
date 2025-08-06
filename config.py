"""
MCP 게시판 설정 관리 모듈

이 모듈은 애플리케이션의 모든 설정을 중앙화하여 관리합니다.
환경변수, .env 파일, 기본값을 우선순위에 따라 로드하고,
개발/프로덕션 환경 분리를 지원합니다.

설정 우선순위:
1. 시스템 환경변수
2. .env 파일의 변수
3. 기본값 (코드에 하드코딩된 값)

주요 설정 그룹:
- API 키: Anthropic Claude API 접근용
- 데이터베이스: SQLite 연결 설정
- 서버: 호스트, 포트, 디버그 모드
- MCP: AI 모델 및 기능 활성화 설정
- 보안: 암호화 키 및 보안 관련 설정
"""

import os                      # 환경변수 접근
from typing import Optional    # 타입 힌팅
from dotenv import load_dotenv # .env 파일 로딩

# ==========================================
# 애플리케이션 설정 클래스
# ==========================================

class Config:
    """
    애플리케이션 설정 관리 클래스
    
    환경변수와 .env 파일에서 설정을 로드하며,
    각 설정에 대한 기본값과 검증 로직을 제공합니다.
    
    설계 원칙:
    - 환경별 설정 분리 (개발/프로덕션)
    - 민감한 정보는 환경변수로 관리
    - 모든 설정에 안전한 기본값 제공
    - 타입 안전성 보장
    
    사용법:
        config = Config()
        api_key = config.ANTHROPIC_API_KEY
        is_debug = config.DEBUG
    """
    
    def __init__(self):
        """
        설정 초기화
        
        .env 파일을 로드하고 모든 설정값을 환경변수에서 읽어옵니다.
        각 설정에는 안전한 기본값이 설정되어 있습니다.
        """
        # 1. .env 파일 로드 (프로젝트 루트의 .env 파일)
        # 존재하지 않으면 무시됨
        load_dotenv()
        
        # ========== AI/MCP 관련 설정 ==========
        # Anthropic Claude API 키 (실제 MCP 기능 사용시 필수)
        self.ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        
        # ========== 데이터베이스 설정 ==========
        # 데이터베이스 연결 URL (SQLite 파일 경로)
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///board.db")
        
        # ========== 웹 서버 설정 ==========
        # 서버 바인딩 호스트 (0.0.0.0은 모든 인터페이스에서 접근 허용)
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        
        # 서버 포트 번호
        self.PORT: int = int(os.getenv("PORT", "8000"))
        
        # 디버그 모드 (개발시 True, 프로덕션시 False)
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
        
        # ========== MCP 기능 설정 ==========
        # MCP 기능 활성화 여부
        self.MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "true").lower() == "true"
        
        # 기본 AI 모델 (Anthropic Claude 모델명)
        self.DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
        
        # ========== 보안 설정 ==========
        # 애플리케이션 비밀 키 (세션, JWT 등에 사용)
        # 프로덕션에서는 반드시 강력한 랜덤 키로 변경해야 함
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "mcp_board_secret_key_2024")
    
    def set_anthropic_api_key(self, api_key: str):
        """
        Anthropic API 키 동적 설정
        
        런타임에 API 키를 설정하거나 변경할 때 사용합니다.
        웹 인터페이스를 통한 API 키 설정 시 호출됩니다.
        
        Args:
            api_key (str): Anthropic API 키 (sk-ant-로 시작하는 형식)
        """
        # 인스턴스 변수 업데이트
        self.ANTHROPIC_API_KEY = api_key
        
        # 환경변수도 동시 업데이트 (다른 모듈에서 접근 가능하도록)
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    def is_api_key_configured(self) -> bool:
        """
        API 키 설정 상태 확인
        
        Anthropic API 키가 올바르게 설정되어 있는지 검증합니다.
        None이 아니고 빈 문자열이 아닌 경우 설정된 것으로 판단합니다.
        
        Returns:
            bool: API 키 설정 여부
                 True: 설정됨, False: 미설정
        """
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