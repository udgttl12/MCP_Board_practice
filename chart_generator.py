"""
차트 생성 로직 구현
"""

import json
from database import db_manager

class ChartGenerator:
    """Chart.js 코드를 동적으로 생성하는 클래스"""
    
    def __init__(self):
        self.db = db_manager
    
    def create_chart_js_code(self, author_data, chart_type="bar"):
        """
        작성자 데이터를 받아서 Chart.js 코드를 동적으로 생성
        
        Args:
            author_data (list): 작성자의 게시글 데이터 리스트
            chart_type (str): 차트 타입 (bar, line, pie 등)
        
        Returns:
            str: Chart.js 코드 문자열
        """
        if not author_data:
            return ""
        
        # 라벨과 값 추출
        labels = [post['title'] for post in author_data]
        values = [post['numeric_value'] for post in author_data if post['numeric_value'] is not None]
        
        # 데이터가 없으면 빈 차트
        if not values:
            values = [0] * len(labels)
        
        # JSON 형태로 변환 (JavaScript에서 사용하기 위해)
        labels_json = json.dumps(labels, ensure_ascii=False)
        values_json = json.dumps(values)
        
        # 차트 타입별 설정
        chart_config = self._get_chart_config(chart_type)
        
        chart_code = f"""
        // 기존 차트가 있다면 제거
        if (window.myChart) {{
            window.myChart.destroy();
        }}
        
        const ctx = document.getElementById('dynamicChart').getContext('2d');
        window.myChart = new Chart(ctx, {{
            type: '{chart_type}',
            data: {{
                labels: {labels_json},
                datasets: [{{
                    label: '수치 데이터',
                    data: {values_json},
                    backgroundColor: {json.dumps(chart_config['backgroundColor'])},
                    borderColor: {json.dumps(chart_config['borderColor'])},
                    borderWidth: {chart_config['borderWidth']}
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '작성자별 데이터 차트'
                    }},
                    legend: {{
                        display: {str(chart_config['showLegend']).lower()}
                    }}
                }},
                scales: {json.dumps(chart_config['scales'], ensure_ascii=False) if chart_config['scales'] else '{}'}
            }}
        }});
        """
        return chart_code
    
    def _get_chart_config(self, chart_type):
        """차트 타입별 설정 반환"""
        configs = {
            "bar": {
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
                "showLegend": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "값"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "게시글"
                        }
                    }
                }
            },
            "line": {
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 2,
                "showLegend": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "값"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "게시글"
                        }
                    }
                }
            },
            "pie": {
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 205, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(153, 102, 255, 0.8)",
                    "rgba(255, 159, 64, 0.8)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 205, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)"
                ],
                "borderWidth": 1,
                "showLegend": True,
                "scales": None  # 파이 차트는 스케일 불필요
            },
            "doughnut": {
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 205, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(153, 102, 255, 0.8)",
                    "rgba(255, 159, 64, 0.8)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 205, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)"
                ],
                "borderWidth": 1,
                "showLegend": True,
                "scales": None  # 도넛 차트는 스케일 불필요
            }
        }
        
        return configs.get(chart_type, configs["bar"])
    
    def get_author_numeric_data(self, author_name):
        """
        특정 작성자의 숫자 데이터를 데이터베이스에서 조회
        
        Args:
            author_name (str): 작성자명
        
        Returns:
            list: 작성자의 게시글 데이터 리스트
        """
        try:
            posts = self.db.get_posts_by_author(author_name)
            # 숫자 값이 있는 게시글만 필터링
            numeric_posts = [
                post for post in posts 
                if post.get('numeric_value') is not None
            ]
            return numeric_posts
        except Exception as e:
            print(f"데이터 조회 중 오류: {e}")
            return []
    
    def get_available_authors(self):
        """숫자 데이터를 가진 작성자 목록 반환"""
        try:
            return self.db.get_authors_with_numeric_data()
        except Exception as e:
            print(f"작성자 목록 조회 중 오류: {e}")
            return []
    
    def validate_chart_type(self, chart_type):
        """차트 타입 유효성 검사"""
        valid_types = ["bar", "line", "pie", "doughnut"]
        return chart_type in valid_types
    
    def generate_chart_summary(self, author_name, chart_data):
        """차트 데이터 요약 정보 생성"""
        if not chart_data:
            return {
                "author": author_name,
                "total_posts": 0,
                "average_value": 0,
                "max_value": 0,
                "min_value": 0
            }
        
        values = [post['numeric_value'] for post in chart_data if post['numeric_value'] is not None]
        
        return {
            "author": author_name,
            "total_posts": len(chart_data),
            "average_value": round(sum(values) / len(values), 2) if values else 0,
            "max_value": max(values) if values else 0,
            "min_value": min(values) if values else 0
        }

# 전역 차트 생성기 인스턴스
chart_generator = ChartGenerator()