from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

# 消息角色枚举
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# 聊天消息
class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = None

# 工具调用
class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]  # {"name": "tavily_search", "arguments": "{\"query\": \"北京天气\"}"}

# SSE 事件类型
class SSEEventType(str, Enum):
    STATUS = "status"
    TOOL_CALL = "tool_call"
    CONTENT = "content"
    ERROR = "error"
    DONE = "done"

# SSE 事件
class SSEEvent(BaseModel):
    type: SSEEventType
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None

# API 请求响应
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls_made: Optional[List[str]] = None