"""
MCP 게시판 데이터베이스 관리 모듈

이 모듈은 SQLAlchemy ORM을 사용하여 게시글 데이터를 관리합니다.
주요 기능:
- 게시글 모델 정의 (Post)
- 데이터베이스 연결 및 세션 관리
- CRUD 작업 (Create, Read, Update, Delete)
- 차트 생성용 숫자 데이터 조회
- 작성자별 데이터 필터링

데이터베이스 스키마:
- posts 테이블: 게시글 정보 저장
  - id: 고유 식별자
  - author: 작성자명
  - title: 게시글 제목
  - content: 게시글 내용
  - numeric_value: 차트 생성용 숫자 데이터
  - category: 카테고리 분류
  - created_at: 생성 시간
"""

# 데이터베이스 ORM 관련 임포트
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text  # SQLAlchemy 핵심 타입
from sqlalchemy.ext.declarative import declarative_base  # 모델 베이스 클래스
from sqlalchemy.orm import sessionmaker  # 세션 관리

# 표준 라이브러리
from datetime import datetime  # 시간 처리
import sqlite3                # SQLite 직접 접근용 (필요시)

# ==========================================
# 데이터베이스 모델 정의
# ==========================================

# SQLAlchemy 모델의 기본 클래스
Base = declarative_base()

class Post(Base):
    """
    게시글 데이터 모델
    
    MCP 게시판의 핵심 데이터 구조로, 일반적인 게시글 정보와 함께
    차트 생성을 위한 숫자 데이터를 포함합니다.
    
    특징:
    - numeric_value: 차트 시각화용 숫자 데이터 (선택적)
    - category: 게시글 분류용 카테고리 (선택적)
    - created_at: 자동 생성 시간 기록
    """
    __tablename__ = "posts"
    
    # 기본 필드들
    id = Column(Integer, primary_key=True, autoincrement=True)  # 고유 식별자 (자동증가)
    author = Column(String(50), nullable=False)                # 작성자명 (필수, 최대 50자)
    title = Column(String(200), nullable=False)                # 게시글 제목 (필수, 최대 200자)
    content = Column(Text)                                     # 게시글 내용 (선택적, 길이 제한 없음)
    
    # MCP 특화 필드들
    numeric_value = Column(Float)                              # 차트 생성용 숫자 데이터 (선택적)
    category = Column(String(50))                              # 카테고리 분류 (선택적, 최대 50자)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)     # 생성 시간 (자동 설정)

    def to_dict(self):
        """
        모델 객체를 딕셔너리로 변환
        
        SQLAlchemy 모델 객체를 JSON 직렬화 가능한 딕셔너리로 변환합니다.
        API 응답이나 템플릿 렌더링에 사용됩니다.
        
        Returns:
            dict: 게시글 정보를 담은 딕셔너리
        """
        return {
            'id': self.id,
            'author': self.author,
            'title': self.title,
            'content': self.content,
            'numeric_value': self.numeric_value,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==========================================
# 데이터베이스 관리 클래스
# ==========================================

class DatabaseManager:
    """
    데이터베이스 연결 및 작업 관리 클래스
    
    SQLAlchemy ORM을 사용하여 데이터베이스 작업을 추상화하고,
    게시글 관련 CRUD 작업을 제공합니다.
    
    주요 기능:
    - 데이터베이스 연결 관리
    - 세션 생성 및 관리
    - 게시글 CRUD 작업
    - 차트용 데이터 조회
    - 트랜잭션 관리 (자동 커밋/롤백)
    
    사용 패턴:
    1. 세션 생성
    2. 데이터베이스 작업 수행
    3. 성공시 커밋, 실패시 롤백
    4. 세션 종료 (finally 블록에서)
    """
    
    def __init__(self, db_url="sqlite:///board.db"):
        """
        데이터베이스 매니저 초기화
        
        Args:
            db_url (str): 데이터베이스 연결 URL (기본값: SQLite 파일)
        """
        # SQLAlchemy 엔진 생성 (데이터베이스 연결 풀 관리)
        self.engine = create_engine(db_url)
        
        # 세션 팩토리 생성 (각 요청마다 새로운 세션 생성용)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 테이블 생성 (존재하지 않는 경우)
        self.create_tables()
    
    def create_tables(self):
        """
        데이터베이스 테이블 생성
        
        SQLAlchemy 메타데이터를 기반으로 모든 테이블을 생성합니다.
        이미 존재하는 테이블은 무시됩니다.
        """
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """
        새로운 데이터베이스 세션 반환
        
        각 데이터베이스 작업마다 새로운 세션을 생성합니다.
        세션은 사용 후 반드시 close()해야 합니다.
        
        Returns:
            Session: SQLAlchemy 세션 객체
        """
        return self.SessionLocal()
    
    def add_post(self, author, title, content, numeric_value=None, category=None):
        """
        새로운 게시글 추가
        
        게시글 정보를 받아 데이터베이스에 저장합니다.
        numeric_value는 차트 생성용 숫자 데이터로 사용됩니다.
        
        Args:
            author (str): 작성자명 (필수)
            title (str): 게시글 제목 (필수)
            content (str): 게시글 내용 (선택)
            numeric_value (float): 차트용 숫자 데이터 (선택)
            category (str): 카테고리 (선택)
            
        Returns:
            dict: 생성된 게시글 정보 딕셔너리
            
        Raises:
            Exception: 데이터베이스 작업 실패 시
        """
        session = self.get_session()
        try:
            # 새로운 Post 객체 생성
            post = Post(
                author=author,
                title=title,
                content=content,
                numeric_value=numeric_value,
                category=category
            )
            
            # 세션에 추가하고 커밋
            session.add(post)
            session.commit()
            
            # 딕셔너리 형태로 반환
            return post.to_dict()
            
        except Exception as e:
            # 오류 발생 시 롤백
            session.rollback()
            raise e
        finally:
            # 항상 세션 종료
            session.close()
    
    def get_posts_by_author(self, author_name):
        """특정 작성자의 모든 게시글 조회"""
        session = self.get_session()
        try:
            posts = session.query(Post).filter(Post.author == author_name).all()
            return [post.to_dict() for post in posts]
        finally:
            session.close()
    
    def get_all_posts(self):
        """모든 게시글 조회"""
        session = self.get_session()
        try:
            posts = session.query(Post).order_by(Post.created_at.desc()).all()
            return [post.to_dict() for post in posts]
        finally:
            session.close()
    
    def get_authors_with_numeric_data(self):
        """숫자 데이터가 있는 작성자 목록 조회"""
        session = self.get_session()
        try:
            authors = session.query(Post.author).filter(
                Post.numeric_value.isnot(None)
            ).distinct().all()
            return [author[0] for author in authors]
        finally:
            session.close()
    
    def get_post_by_id(self, post_id):
        """ID로 게시글 조회"""
        session = self.get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            return post
        finally:
            session.close()
    
    def update_post(self, post_id, title, content, author):
        """게시글 수정"""
        session = self.get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                post.title = title
                post.content = content
                post.author = author
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_post(self, post_id):
        """게시글 삭제"""
        session = self.get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                session.delete(post)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()

def init_sample_data():
    """샘플 데이터 초기화"""
    try:
        # 기존 데이터가 있는지 확인
        posts = db_manager.get_all_posts()
        if len(posts) == 0:
            # 샘플 데이터 추가
            sample_posts = [
                {"author": "홍길동", "title": "1월 매출 보고", "content": "1월 매출 데이터입니다.", "numeric_value": 150.5, "category": "매출"},
                {"author": "홍길동", "title": "2월 매출 보고", "content": "2월 매출 데이터입니다.", "numeric_value": 180.2, "category": "매출"},
                {"author": "홍길동", "title": "3월 매출 보고", "content": "3월 매출 데이터입니다.", "numeric_value": 200.8, "category": "매출"},
                {"author": "김철수", "title": "사용자 수 증가", "content": "월별 사용자 수 현황", "numeric_value": 1200, "category": "사용자"},
                {"author": "김철수", "title": "신규 가입자", "content": "신규 가입자 현황", "numeric_value": 850, "category": "사용자"},
                {"author": "이영희", "title": "서버 성능 지표", "content": "서버 응답시간 측정", "numeric_value": 95.5, "category": "성능"},
                {"author": "이영희", "title": "데이터베이스 성능", "content": "DB 쿼리 성능 분석", "numeric_value": 120.3, "category": "성능"},
            ]
            
            for post_data in sample_posts:
                db_manager.add_post(**post_data)
            
            print("샘플 데이터가 추가되었습니다.")
    except Exception as e:
        print(f"샘플 데이터 초기화 중 오류: {e}")

# 모듈 import 시 샘플 데이터 초기화
if __name__ == "__main__":
    init_sample_data()