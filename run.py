#!/usr/bin/env python3
"""
MCP 게시판 프로젝트 실행 스크립트
"""

import sys
import subprocess
import os

def check_requirements():
    """필요한 패키지가 설치되어 있는지 확인"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import jinja2
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필수 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 패키지를 설치하세요:")
        print("pip install -r requirements.txt")
        return False

def run_server():
    """서버 실행"""
    if not check_requirements():
        return False
    
    print("🚀 MCP 게시판 서버를 시작합니다...")
    print("📡 서버 주소: http://localhost:8000")
    print("⏹️  서버를 중지하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    try:
        # uvicorn으로 직접 FastAPI 앱 실행
        import uvicorn
        uvicorn.run(
            "app:app",  # app.py의 app 변수를 import string으로 지정
            host="0.0.0.0",
            port=8000,
            reload=False,  # subprocess 환경에서는 reload 비활성화
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 중지되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류가 발생했습니다: {e}")
        return False
    
    return True

def install_requirements():
    """requirements.txt 패키지 설치"""
    print("📦 필요한 패키지를 설치합니다...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 패키지 설치가 완료되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 중 오류가 발생했습니다: {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 50)
    print("🎯 MCP 게시판 프로젝트")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    if not os.path.exists("app.py"):
        print("❌ 프로젝트 루트 디렉토리에서 실행해주세요.")
        sys.exit(1)
    
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            if install_requirements():
                print("이제 'python run.py' 명령으로 서버를 실행할 수 있습니다.")
            return
        elif sys.argv[1] == "help":
            print("사용법:")
            print("  python run.py          - 서버 실행")
            print("  python run.py install  - 패키지 설치")
            print("  python run.py help     - 도움말 표시")
            return
    
    # 서버 실행
    if not run_server():
        print("\n💡 문제가 발생했다면 다음을 시도해보세요:")
        print("1. python run.py install")
        print("2. python -m pip install --upgrade pip")
        print("3. python app.py")

if __name__ == "__main__":
    main()