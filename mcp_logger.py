"""
MCP 통신 로그 수집 및 관리 시스템
실시간으로 MCP 통신 상태를 추적하고 표시
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """로그 레벨"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


@dataclass
class MCPLogEntry:
    """MCP 로그 엔트리"""
    timestamp: str
    level: LogLevel
    category: str  # "api_call", "parsing", "chart_generation", "system"
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = asdict(self)
        result['level'] = self.level.value
        return result


class MCPLogger:
    """MCP 통신 로그 관리자"""
    
    def __init__(self, max_logs: int = 100):
        self.max_logs = max_logs
        self.logs: List[MCPLogEntry] = []
        self._lock = asyncio.Lock()
    
    async def log(
        self, 
        level: LogLevel, 
        category: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ):
        """로그 추가"""
        async with self._lock:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            entry = MCPLogEntry(
                timestamp=timestamp,
                level=level,
                category=category,
                message=message,
                details=details,
                duration_ms=duration_ms
            )
            
            self.logs.append(entry)
            
            # 최대 로그 수 제한
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[-self.max_logs:]
            
            # 콘솔에도 출력
            self._print_log(entry)
    
    def _print_log(self, entry: MCPLogEntry):
        """콘솔에 로그 출력"""
        icon_map = {
            LogLevel.INFO: "ℹ️",
            LogLevel.SUCCESS: "✅",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.DEBUG: "🔍"
        }
        
        icon = icon_map.get(entry.level, "📝")
        duration_str = f" ({entry.duration_ms:.1f}ms)" if entry.duration_ms else ""
        
        print(f"{icon} [{entry.timestamp}] {entry.category.upper()}: {entry.message}{duration_str}")
        
        if entry.details:
            # 중요한 정보만 간략하게 출력
            if 'command' in entry.details:
                print(f"    📝 명령: {entry.details['command']}")
            if 'author_names' in entry.details:
                print(f"    👥 작성자: {entry.details['author_names']}")
            if 'chart_type' in entry.details:
                print(f"    📊 차트: {entry.details['chart_type']}")
            if 'method' in entry.details:
                print(f"    🔧 방식: {entry.details['method']}")
    
    async def get_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """로그 조회"""
        async with self._lock:
            logs_to_return = self.logs[-limit:] if limit else self.logs
            return [log.to_dict() for log in logs_to_return]
    
    async def clear_logs(self):
        """로그 초기화"""
        async with self._lock:
            self.logs.clear()
            await self.log(LogLevel.INFO, "system", "로그가 초기화되었습니다.")
    
    async def log_api_call(self, api_name: str, parameters: Dict[str, Any]):
        """API 호출 로그"""
        await self.log(
            LogLevel.INFO,
            "api_call",
            f"{api_name} API 호출",
            {"api": api_name, "parameters": parameters}
        )
    
    async def log_api_response(self, api_name: str, success: bool, duration_ms: float, details: Dict[str, Any]):
        """API 응답 로그"""
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        status = "성공" if success else "실패"
        
        await self.log(
            level,
            "api_call",
            f"{api_name} API {status}",
            details,
            duration_ms
        )
    
    async def log_parsing(self, command: str, result: Dict[str, Any], duration_ms: float):
        """파싱 결과 로그"""
        is_valid = result.get('valid', False)
        level = LogLevel.SUCCESS if is_valid else LogLevel.WARNING
        
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        
        message = f"명령어 파싱 완료 (방식: {method}, 신뢰도: {confidence:.2f})"
        
        await self.log(
            level,
            "parsing",
            message,
            {
                "command": command,
                "method": method,
                "confidence": confidence,
                "author_names": result.get('author_names'),
                "chart_type": result.get('chart_type'),
                "is_multi_author": result.get('is_multi_author', False),
                "valid": is_valid
            },
            duration_ms
        )
    
    async def log_chart_generation(self, chart_type: str, authors: List[str], success: bool, method: str, duration_ms: float):
        """차트 생성 로그"""
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        status = "성공" if success else "실패"
        author_text = ", ".join(authors) if authors else "없음"
        
        message = f"{chart_type} 차트 생성 {status} (작성자: {author_text})"
        
        await self.log(
            level,
            "chart_generation",
            message,
            {
                "chart_type": chart_type,
                "authors": authors,
                "method": method,
                "success": success
            },
            duration_ms
        )
    
    async def log_system_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """시스템 이벤트 로그"""
        await self.log(
            LogLevel.INFO,
            "system",
            event,
            details
        )
    
    async def log_error(self, category: str, error_message: str, details: Optional[Dict[str, Any]] = None):
        """에러 로그"""
        await self.log(
            LogLevel.ERROR,
            category,
            f"오류 발생: {error_message}",
            details
        )


# 전역 로거 인스턴스
mcp_logger = MCPLogger(max_logs=200)


# 편의 함수들
async def log_mcp_info(category: str, message: str, details: Dict[str, Any] = None):
    """정보 로그"""
    await mcp_logger.log(LogLevel.INFO, category, message, details)


async def log_mcp_success(category: str, message: str, details: Dict[str, Any] = None, duration_ms: float = None):
    """성공 로그"""
    await mcp_logger.log(LogLevel.SUCCESS, category, message, details, duration_ms)


async def log_mcp_warning(category: str, message: str, details: Dict[str, Any] = None):
    """경고 로그"""
    await mcp_logger.log(LogLevel.WARNING, category, message, details)


async def log_mcp_error(category: str, message: str, details: Dict[str, Any] = None):
    """에러 로그"""
    await mcp_logger.log(LogLevel.ERROR, category, message, details)


async def log_mcp_debug(category: str, message: str, details: Dict[str, Any] = None):
    """디버그 로그"""
    await mcp_logger.log(LogLevel.DEBUG, category, message, details)