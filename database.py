"""
데이터베이스 모델 및 연결 설정
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sqlite3

Base = declarative_base()

class Post(Base):
    """게시글 모델"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    numeric_value = Column(Float)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'author': self.author,
            'title': self.title,
            'content': self.content,
            'numeric_value': self.numeric_value,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_url="sqlite:///board.db"):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """테이블 생성"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """데이터베이스 세션 반환"""
        return self.SessionLocal()
    
    def add_post(self, author, title, content, numeric_value=None, category=None):
        """게시글 추가"""
        session = self.get_session()
        try:
            post = Post(
                author=author,
                title=title,
                content=content,
                numeric_value=numeric_value,
                category=category
            )
            session.add(post)
            session.commit()
            return post.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
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