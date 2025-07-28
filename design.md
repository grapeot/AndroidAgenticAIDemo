# AI 聊天系统开发指南

## 项目目标

构建一个集成 Tavily 搜索功能的 AI 聊天系统，实现：
1. 用户通过 Web 界面与 AI 对话
2. AI 可以调用 Tavily 搜索工具获取实时信息
3. 支持流式响应，实时显示 AI 的思考和回复过程

## 技术栈

- **后端**: FastAPI
- **前端**: React
- **实时通信**: Server-Sent Events (SSE)
- **AI**: OpenAI API (GPT-4.1-mini)
- **搜索**: Tavily API

## 项目结构

```
ai-chat-system/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── requirements.txt     # Python 依赖
│   ├── services/
│   │   ├── openai_service.py   # OpenAI API 集成
│   │   └── tavily_service.py   # Tavily API 集成
│   └── models/
│       └── schemas.py       # 请求/响应模型
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── ChatInterface.js
│   │   │   ├── MessageBubble.js
│   │   │   └── LoadingIndicator.js
│   │   └── services/
│   │       └── api.js       # SSE 客户端
│   └── public/
└── README.md
```

## 开发里程碑

### Milestone 1: 后端基础设施（Day 1）
- [ ] 创建 FastAPI 项目结构
- [ ] 实现 OpenAI 服务集成
- [ ] 实现 Tavily 服务集成  
- [ ] 创建聊天 API 端点（POST /chat）
- [ ] 实现 SSE 端点（GET /chat/stream）
- [ ] 工具调用解析和执行逻辑

### Milestone 2: 前端基础界面（Day 2）
- [ ] 创建 React 项目
- [ ] 实现聊天界面组件
- [ ] 集成 SSE 客户端
- [ ] 实现消息显示和输入功能
- [ ] 添加加载状态指示器

### Milestone 3: 核心功能集成（Day 3）
- [ ] 前后端联调
- [ ] 实现完整的消息流：用户输入 → AI 处理 → 工具调用 → 结果展示
- [ ] 处理错误和边缘情况
- [ ] 优化流式响应体验

### Milestone 4: 优化和部署（Day 4）
- [ ] UI 美化和响应式设计
- [ ] 添加对话历史管理
- [ ] 性能优化
- [ ] 部署文档和脚本

## 核心数据结构

### 后端数据模型 (schemas.py)

```python
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
```

### 前端数据结构 (TypeScript)

```typescript
// types.ts
export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  args: Record<string, any>;
  result?: any;
}

export enum SSEEventType {
  STATUS = 'status',
  TOOL_CALL = 'tool_call',
  CONTENT = 'content',
  ERROR = 'error',
  DONE = 'done'
}

export interface SSEEvent {
  type: SSEEventType;
  content?: string;
  tool_name?: string;
  tool_args?: Record<string, any>;
}
```

## 核心接口定义

### REST API 接口

#### 1. 发送消息 (非流式)
```
POST /api/chat
Content-Type: application/json

Request:
{
    "message": "今天北京的天气如何？",
    "conversation_id": "optional-uuid"
}

Response:
{
    "response": "根据最新搜索结果，北京今天...",
    "conversation_id": "uuid",
    "tool_calls_made": ["tavily_search"]
}
```

#### 2. 流式聊天
```
POST /api/chat/stream
Content-Type: application/json

Request:
{
    "message": "今天北京的天气如何？",
    "conversation_id": "optional-uuid"
}

Response: EventStream
data: {"type": "status", "content": "正在理解您的问题..."}
data: {"type": "status", "content": "正在搜索相关信息..."}
data: {"type": "tool_call", "tool_name": "tavily_search", "tool_args": {"query": "北京今天天气"}}
data: {"type": "content", "content": "根据"}
data: {"type": "content", "content": "最新"}
data: {"type": "content", "content": "搜索结果，"}
data: {"type": "content", "content": "北京今天..."}
data: {"type": "done"}
```

#### 3. 获取对话历史
```
GET /api/conversations/{conversation_id}

Response:
{
    "conversation_id": "uuid",
    "messages": [
        {
            "role": "user",
            "content": "今天北京的天气如何？",
            "timestamp": "2024-01-20T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "根据最新搜索结果...",
            "timestamp": "2024-01-20T10:00:05Z"
        }
    ]
}
```

### WebSocket 接口（备选方案）

```
WS /ws/chat

// 客户端发送
{
    "type": "message",
    "content": "今天北京的天气如何？"
}

// 服务端响应
{
    "type": "status",
    "content": "正在搜索..."
}
{
    "type": "tool_call",
    "tool": "tavily_search",
    "query": "北京天气"
}
{
    "type": "stream",
    "content": "根据搜索结果，北京今天..."
}
{
    "type": "complete"
}
```

### 工具调用流程

1. 用户发送消息
2. 调用 OpenAI API，配置 tools 参数
3. 解析 AI 响应中的 tool_calls
4. 执行相应工具（如 Tavily 搜索）
5. 将工具结果返回给 AI
6. AI 生成最终回复

### SSE 实现要点

- 前端使用 EventSource API
- 后端使用 FastAPI 的 StreamingResponse
- 支持重连机制
- 实时显示状态更新

## 环境配置

API Keys 已在系统环境变量中配置：
- `OPENAI_API_KEY` - OpenAI API 密钥
- `TAVILY_API_KEY` - Tavily API 密钥

代码中直接使用 `os.environ` 读取即可。

## 开发命令

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 前端
cd frontend
npm install
npm start
```

## 注意事项

1. API Key 安全：确保 API Key 仅在后端使用，不要暴露到前端
2. CORS 配置：FastAPI 需要配置 CORS 以允许前端访问
3. 错误处理：实现完善的错误处理和用户提示
4. 流式响应：确保 SSE 连接的稳定性和错误恢复