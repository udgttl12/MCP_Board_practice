"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio

# 로컬 모듈 임포트
from mcp_server_real import generate_author_chart, parse_chart_command, get_mcp_status
from mcp_server import get_available_authors, get_chart_types  # 기존 함수들
from database import db_manager, init_sample_data
from config import config, setup_api_key
from mcp_logger import mcp_logger, log_mcp_error

# 요청 모델 정의
class ChartRequest(BaseModel):
    command: str

class PostUpdate(BaseModel):
    title: str
    content: str
    author: str

class PostManagementRequest(BaseModel):
    command: str

class PostRequest(BaseModel):
    author: str
    title: str
    content: str = ""
    numeric_value: float = None
    category: str = None

# 시작 시 데이터베이스 초기화
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    print("🚀 MCP 게시판 애플리케이션을 시작합니다...")
    
    # API 키 설정 확인
    if config.is_api_key_configured():
        print(f"✅ Anthropic API 키가 설정되어 있습니다.")
        print(f"🤖 실제 MCP 모드로 실행됩니다.")
        await mcp_logger.log_system_event("서버 시작 - Real MCP 모드")
    else:
        print(f"⚠️  Anthropic API 키가 설정되지 않았습니다.")
        print(f"🔧 시뮬레이션 모드로 실행됩니다.")
        print(f"💡 실제 MCP를 사용하려면 API 키를 설정하세요.")
        await mcp_logger.log_system_event("서버 시작 - 시뮬레이션 모드")
    
    # 데이터베이스 초기화
    init_sample_data()
    print("📊 데이터베이스 초기화가 완료되었습니다.")
    
    # MCP 상태 확인
    mcp_status = await get_mcp_status()
    print(f"🔍 MCP 상태: {mcp_status['mode']}")
    await mcp_logger.log_system_event("MCP 상태 확인 완료", mcp_status)
    
    yield
    
    # 종료 시 실행
    print("🛑 서버가 종료됩니다.")
    await mcp_logger.log_system_event("서버 종료")

# FastAPI 앱 초기화
app = FastAPI(
    title="MCP 게시판",
    description="MCP를 활용한 게시판에서 차트 자동 생성 기능",
    version="1.0.0",
    lifespan=lifespan
)

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 라우트 정의
@app.get("/")
async def main_page(request: Request):
    """메인 게시판 페이지"""
    try:
        # 최근 게시글 목록을 가져와서 템플릿에 전달
        posts = db_manager.get_all_posts()[:10]  # 최근 10개만
        available_authors = db_manager.get_authors_with_numeric_data()
        
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request,
                "posts": posts,
                "available_authors": available_authors
            }
        )
    except Exception as e:
        print(f"메인 페이지 로딩 중 오류: {e}")
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "posts": [], "available_authors": []}
        )

@app.post("/generate-chart")
async def create_chart(request: ChartRequest):
    """차트 생성 API 엔드포인트"""
    try:
        command = request.command.strip()
        
        if not command:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "명령어를 입력해주세요."
                }
            )
        
        # 명령어 파싱
        parsed = await parse_chart_command(command)
        
        if not parsed['valid']:
            # 사용 가능한 작성자 목록 제공
            authors_result = await get_available_authors()
            authors_list = authors_result.get('authors', [])
            authors_str = ", ".join(authors_list) if authors_list else "없음"
            
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"작성자명을 찾을 수 없습니다. 예: '홍길동의 데이터를 차트로 보여줘' 또는 '홍길동과 김철수의 데이터를 차트로 보여줘'\\n사용 가능한 작성자: {authors_str}"
                }
            )
        
        # 다중 작성자 또는 단일 작성자 차트 생성
        if parsed.get('is_multi_author') and parsed.get('author_names'):
            # "모든 사람들" 특별 처리
            if parsed['author_names'] == "ALL_AUTHORS":
                # 데이터베이스에서 모든 작성자 가져오기
                authors_result = await get_available_authors()
                all_authors = authors_result.get('authors', [])
                
                if not all_authors:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "데이터베이스에 작성자가 없습니다."
                        }
                    )
                
                # 모든 작성자로 다중 차트 생성
                from mcp_server_real import real_mcp_server
                result = await real_mcp_server.generate_multi_author_chart(
                    all_authors, 
                    parsed['chart_type']
                )
            else:
                # 일반 다중 작성자 차트 생성
                from mcp_server_real import real_mcp_server
                result = await real_mcp_server.generate_multi_author_chart(
                    parsed['author_names'], 
                    parsed['chart_type']
                )
        else:
            # 단일 작성자 차트 생성 (기존 방식)
            result = await generate_author_chart(
                parsed['author_name'], 
                parsed['chart_type']
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"서버 오류가 발생했습니다: {str(e)}"
            }
        )

@app.post("/manage-post")
async def manage_post_with_mcp(request: PostManagementRequest):
    """MCP를 통한 자연어 게시글 관리 API"""
    try:
        # MCP로 명령 파싱
        from mcp_server_real import real_mcp_server
        parsed_result = await real_mcp_server.parse_post_management_command(request.command)
        
        if not parsed_result.get("valid"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"명령을 이해할 수 없습니다: {parsed_result.get('explanation', '알 수 없는 오류')}",
                    "parsed_result": parsed_result
                }
            )
        
        action = parsed_result.get("action")
        
        # 액션별 처리
        if action == "create":
            # 게시글 생성
            result = await _handle_create_post(parsed_result)
            
        elif action == "update":
            # 게시글 수정
            result = await _handle_update_post(parsed_result)
            
        elif action == "delete":
            # 게시글 삭제
            result = await _handle_delete_post(parsed_result)
            
        elif action == "list":
            # 게시글 목록 조회
            result = await _handle_list_posts(parsed_result)
            
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"지원하지 않는 액션입니다: {action}",
                    "parsed_result": parsed_result
                }
            )
        
        # MCP 로그 기록
        await mcp_logger.log_system_event(f"MCP 게시글 관리 - {action}", {
            "command": request.command,
            "action": action,
            "success": result.get("success", False),
            "method": parsed_result.get("method", "unknown")
        })
        
        # 파싱 결과도 함께 반환
        if isinstance(result, dict):
            result["parsed_result"] = parsed_result
            
            # status_code가 있으면 JSONResponse로 처리
            if "status_code" in result:
                status_code = result.pop("status_code")
                return JSONResponse(status_code=status_code, content=result)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        await log_mcp_error("system", f"MCP 게시글 관리 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"게시글 관리 중 오류가 발생했습니다: {str(e)}"
            }
        )

# MCP 게시글 관리 헬퍼 함수들
async def _handle_create_post(parsed_result: dict):
    """게시글 생성 처리"""
    try:
        author = parsed_result.get("author")
        title = parsed_result.get("title")
        content = parsed_result.get("content", "")
        numeric_value = parsed_result.get("numeric_value")
        category = parsed_result.get("category")
        
        if not author or not title:
            return {
                "success": False,
                "message": "게시글 생성에는 작성자와 제목이 필요합니다.",
                "status_code": 400
            }
        
        # 데이터베이스에 게시글 저장
        post = db_manager.add_post(
            author=author,
            title=title,
            content=content,
            numeric_value=numeric_value,
            category=category
        )
        
        return {
            "success": True,
            "message": f"게시글 '{title}'이(가) 성공적으로 생성되었습니다.",
            "post": post,
            "action": "create"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"게시글 생성 중 오류가 발생했습니다: {str(e)}",
            "status_code": 500
        }

async def _handle_update_post(parsed_result: dict):
    """게시글 수정 처리"""
    try:
        post_id = parsed_result.get("post_id")
        field_to_update = parsed_result.get("field_to_update")
        new_value = parsed_result.get("new_value")
        
        if not post_id or not field_to_update or new_value is None:
            return {
                "success": False,
                "message": "게시글 수정에는 게시글 ID, 수정할 필드, 새로운 값이 필요합니다.",
                "status_code": 400
            }
        
        # 게시글 존재 여부 확인
        existing_post = db_manager.get_post_by_id(post_id)
        if not existing_post:
            return {
                "success": False,
                "message": f"{post_id}번 게시글을 찾을 수 없습니다.",
                "status_code": 404
            }
        
        # 필드별 수정 처리 (한국어/영어 필드명 매핑)
        if field_to_update in ["title", "제목"]:
            success = db_manager.update_post(post_id, new_value, existing_post.content, existing_post.author)
        elif field_to_update in ["content", "내용"]:
            success = db_manager.update_post(post_id, existing_post.title, new_value, existing_post.author)
        elif field_to_update in ["author", "작성자"]:
            success = db_manager.update_post(post_id, existing_post.title, existing_post.content, new_value)
        else:
            return {
                "success": False,
                "message": f"지원하지 않는 필드입니다: {field_to_update}. 사용 가능한 필드: title, content, author",
                "status_code": 400
            }
        
        if success:
            return {
                "success": True,
                "message": f"{post_id}번 게시글의 {field_to_update}이(가) 성공적으로 수정되었습니다.",
                "action": "update",
                "post_id": post_id,
                "field": field_to_update,
                "new_value": new_value
            }
        else:
            return {
                "success": False,
                "message": "게시글 수정에 실패했습니다.",
                "status_code": 500
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"게시글 수정 중 오류가 발생했습니다: {str(e)}",
            "status_code": 500
        }

async def _handle_delete_post(parsed_result: dict):
    """게시글 삭제 처리"""
    try:
        post_id = parsed_result.get("post_id")
        filter_author = parsed_result.get("filter_author")
        
        if post_id:
            # 특정 게시글 삭제
            existing_post = db_manager.get_post_by_id(post_id)
            if not existing_post:
                return {
                    "success": False,
                    "message": f"{post_id}번 게시글을 찾을 수 없습니다.",
                    "status_code": 404
                }
            
            success = db_manager.delete_post(post_id)
            if success:
                return {
                    "success": True,
                    "message": f"{post_id}번 게시글 '{existing_post.title}'이(가) 성공적으로 삭제되었습니다.",
                    "action": "delete",
                    "post_id": post_id
                }
            else:
                return {
                    "success": False,
                    "message": "게시글 삭제에 실패했습니다.",
                    "status_code": 500
                }
                
        elif filter_author:
            # 특정 작성자의 모든 게시글 삭제
            author_posts = db_manager.get_posts_by_author(filter_author)
            if not author_posts:
                return {
                    "success": False,
                    "message": f"'{filter_author}' 작성자의 게시글을 찾을 수 없습니다.",
                    "status_code": 404
                }
            
            deleted_count = 0
            for post in author_posts:
                if db_manager.delete_post(post['id']):
                    deleted_count += 1
            
            return {
                "success": True,
                "message": f"'{filter_author}' 작성자의 게시글 {deleted_count}개가 성공적으로 삭제되었습니다.",
                "action": "delete",
                "filter_author": filter_author,
                "deleted_count": deleted_count
            }
        else:
            return {
                "success": False,
                "message": "삭제할 게시글 ID 또는 작성자명이 필요합니다.",
                "status_code": 400
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"게시글 삭제 중 오류가 발생했습니다: {str(e)}",
            "status_code": 500
        }

async def _handle_list_posts(parsed_result: dict):
    """게시글 목록 조회 처리"""
    try:
        filter_author = parsed_result.get("filter_author")
        
        if filter_author:
            # 특정 작성자의 게시글 목록
            posts = db_manager.get_posts_by_author(filter_author)
            if not posts:
                return {
                    "success": True,
                    "message": f"'{filter_author}' 작성자의 게시글이 없습니다.",
                    "action": "list",
                    "filter_author": filter_author,
                    "posts": [],
                    "count": 0
                }
            
            return {
                "success": True,
                "message": f"'{filter_author}' 작성자의 게시글 {len(posts)}개를 찾았습니다.",
                "action": "list",
                "filter_author": filter_author,
                "posts": posts,
                "count": len(posts)
            }
        else:
            # 전체 게시글 목록
            posts = db_manager.get_all_posts()
            return {
                "success": True,
                "message": f"전체 게시글 {len(posts)}개를 찾았습니다.",
                "action": "list",
                "posts": posts,
                "count": len(posts)
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"게시글 목록 조회 중 오류가 발생했습니다: {str(e)}",
            "status_code": 500
        }

@app.post("/add-post")
async def add_post(request: PostRequest):
    """게시글 추가 API"""
    try:
        # 입력 검증
        if not request.author or not request.title:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "작성자와 제목은 필수입니다."
                }
            )
        
        # 데이터베이스에 게시글 저장
        post = db_manager.add_post(
            author=request.author,
            title=request.title,
            content=request.content,
            numeric_value=request.numeric_value,
            category=request.category
        )
        
        return JSONResponse(
            content={
                "success": True,
                "message": "게시글이 추가되었습니다.",
                "post": post
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"게시글 추가 중 오류가 발생했습니다: {str(e)}"
            }
        )

@app.put("/posts/{post_id}")
async def update_post(post_id: int, post_data: PostUpdate):
    """게시글 수정"""
    try:
        # 게시글 존재 여부 확인
        existing_post = db_manager.get_post_by_id(post_id)
        if not existing_post:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "게시글을 찾을 수 없습니다."}
            )
        
        # 게시글 업데이트
        success = db_manager.update_post(post_id, post_data.title, post_data.content, post_data.author)
        
        if success:
            await mcp_logger.log_system_event("게시글 수정", {
                "post_id": post_id, 
                "title": post_data.title,
                "author": post_data.author
            })
            return JSONResponse(content={"success": True, "message": "게시글이 수정되었습니다."})
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "게시글 수정에 실패했습니다."}
            )
        
    except Exception as e:
        await log_mcp_error("system", f"게시글 수정 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"게시글 수정 중 오류가 발생했습니다: {str(e)}"}
        )

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    """게시글 삭제"""
    try:
        # 게시글 존재 여부 확인
        existing_post = db_manager.get_post_by_id(post_id)
        if not existing_post:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "게시글을 찾을 수 없습니다."}
            )
        
        # 게시글 삭제
        success = db_manager.delete_post(post_id)
        
        if success:
            await mcp_logger.log_system_event("게시글 삭제", {
                "post_id": post_id,
                "title": existing_post.title,
                "author": existing_post.author
            })
            return JSONResponse(content={"success": True, "message": "게시글이 삭제되었습니다."})
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "게시글 삭제에 실패했습니다."}
            )
        
    except Exception as e:
        await log_mcp_error("system", f"게시글 삭제 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"게시글 삭제 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/posts")
async def get_posts():
    """모든 게시글 조회 API"""
    try:
        posts = db_manager.get_all_posts()
        return JSONResponse(
            content={
                "success": True,
                "posts": posts,
                "count": len(posts)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"게시글 조회 중 오류가 발생했습니다: {str(e)}"
            }
        )

@app.get("/posts/author/{author_name}")
async def get_posts_by_author(author_name: str):
    """특정 작성자의 게시글 조회 API"""
    try:
        posts = db_manager.get_posts_by_author(author_name)
        return JSONResponse(
            content={
                "success": True,
                "author": author_name,
                "posts": posts,
                "count": len(posts)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"게시글 조회 중 오류가 발생했습니다: {str(e)}"
            }
        )

@app.get("/authors")
async def get_authors():
    """사용 가능한 작성자 목록 API"""
    try:
        result = await get_available_authors()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"작성자 목록 조회 중 오류가 발생했습니다: {str(e)}"
            }
        )

@app.get("/chart-types")
async def get_supported_chart_types():
    """지원하는 차트 타입 목록 API"""
    try:
        result = await get_chart_types()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"차트 타입 조회 중 오류가 발생했습니다: {str(e)}"
            }
        )

@app.get("/health")
async def health_check():
    """서버 상태 확인 API"""
    return {
        "status": "healthy",
        "message": "MCP 게시판 서버가 정상 작동 중입니다."
    }

@app.get("/mcp-status")
async def mcp_status_check():
    """MCP 상태 확인 API"""
    try:
        status = await get_mcp_status()
        return {
            "success": True,
            "mcp_status": status
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"MCP 상태 확인 중 오류: {str(e)}"
            }
        )

@app.post("/set-api-key")
async def set_api_key(request: dict):
    """API 키 설정 API"""
    try:
        api_key = request.get("api_key", "").strip()
        
        if not api_key:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "API 키를 입력해주세요."
                }
            )
        
        # API 키 설정
        config.set_anthropic_api_key(api_key)
        
        # MCP 서버 재초기화
        from mcp_server_real import real_mcp_server
        real_mcp_server._initialize_client()
        
        # 상태 확인
        status = await get_mcp_status()
        
        # 로그 기록
        await mcp_logger.log_system_event("API 키 설정 완료", {"status": status})
        
        return {
            "success": True,
            "message": "API 키가 설정되었습니다.",
            "mcp_status": status
        }
        
    except Exception as e:
        # 에러 로그 기록
        await log_mcp_error("system", f"API 키 설정 오류: {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"API 키 설정 중 오류: {str(e)}"
            }
        )

@app.get("/mcp-logs")
async def get_mcp_logs(limit: int = 50):
    """MCP 통신 로그 조회"""
    try:
        logs = await mcp_logger.get_logs(limit)
        return JSONResponse(content={
            "success": True,
            "logs": logs,
            "total_count": len(logs)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"로그 조회 중 오류가 발생했습니다: {str(e)}"
            }
        )

@app.post("/clear-mcp-logs")
async def clear_mcp_logs():
    """MCP 로그 초기화"""
    try:
        await mcp_logger.clear_logs()
        return JSONResponse(content={
            "success": True,
            "message": "로그가 초기화되었습니다."
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"로그 초기화 중 오류가 발생했습니다: {str(e)}"
            }
        )

# 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 에러 핸들러"""
    return JSONResponse(
        status_code=404,
        content={"message": "요청한 페이지를 찾을 수 없습니다."}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """500 에러 핸들러"""
    return JSONResponse(
        status_code=500,
        content={"message": "서버 내부 오류가 발생했습니다."}
    )

# 개발용 테스트 엔드포인트
@app.get("/test/mcp")
async def test_mcp_functionality():
    """MCP 기능 테스트 엔드포인트 (개발용)"""
    try:
        # 명령어 파싱 테스트
        test_command = "홍길동의 데이터를 막대차트로 보여줘"
        parsed = await parse_chart_command(test_command)
        
        if parsed['valid']:
            # 차트 생성 테스트
            chart_result = await generate_author_chart(
                parsed['author_name'], 
                parsed['chart_type']
            )
            
            return {
                "test_command": test_command,
                "parsed_result": parsed,
                "chart_generation": {
                    "success": chart_result['success'],
                    "message": chart_result['message'],
                    "has_chart_code": bool(chart_result.get('chart_code'))
                }
            }
        else:
            return {
                "test_command": test_command,
                "parsed_result": parsed,
                "chart_generation": None
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"MCP 테스트 중 오류: {str(e)}"
            }
        )

# 메인 실행 코드
if __name__ == "__main__":
    print("MCP 게시판 서버를 시작합니다...")
    print("브라우저에서 http://localhost:8000 으로 접속하세요.")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,  # 개발 모드에서 파일 변경 시 자동 재시작
        log_level="info"
    )