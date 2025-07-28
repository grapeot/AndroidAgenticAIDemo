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
- **AI**: OpenAI API (GPT-4-mini)
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
├── .env.example             # 环境变量示例
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

## 核心实现细节

### 后端 API 设计

```python
# POST /chat - 发送消息
{
    "message": "今天北京的天气如何？"
}

# GET /chat/stream - SSE 流式响应
# 返回格式：
data: {"type": "status", "content": "正在搜索..."}
data: {"type": "tool_call", "tool": "tavily_search", "query": "北京天气"}
data: {"type": "content", "content": "根据搜索结果，北京今天..."}
data: {"type": "done"}
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

创建 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

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