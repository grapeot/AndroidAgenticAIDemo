# Android Agentic AI Demo

一个在 Android 环境下运行的智能聊天系统，集成了本地 Ollama AI 模型和 Tavily 搜索服务。

## 项目特性

- 🤖 本地 AI 模型推理（使用 Ollama + qwen3:1.7b）
- 🔍 实时网络搜索功能（Tavily 集成）
- 💬 React 前端聊天界面
- 🚀 FastAPI 后端服务
- 📱 专为 Android/Termux 环境优化

## 技术栈

### 后端
- **FastAPI** - 现代、快速的 Python Web 框架
- **Ollama** - 本地大语言模型运行环境
- **qwen3:1.7b** - 轻量级中文语言模型
- **Tavily** - 实时搜索 API
- **uvicorn** - ASGI 服务器

### 前端
- **React 18** - 用户界面库
- **TypeScript** - 类型安全的 JavaScript
- **Server-Sent Events (SSE)** - 实时流式响应
- **Webpack** - 模块打包工具

## 项目结构

```
.
├── backend/
│   ├── main.py                 # FastAPI 应用主文件
│   ├── models/
│   │   └── schemas.py          # 数据模型定义
│   └── services/
│       ├── openai_service.py   # AI 模型服务（Ollama）
│       └── tavily_service.py   # 搜索服务
├── frontend/
│   ├── src/
│   │   ├── components/         # React 组件
│   │   ├── services/          # API 服务
│   │   └── types/             # TypeScript 类型定义
│   ├── package.json
│   └── tsconfig.json
├── probing/                    # 技术验证脚本
├── tests/                      # 测试文件
├── requirements.txt            # Python 依赖
├── start_backend.sh           # 后端启动脚本
└── README.md
```

## 环境要求

- **Python 3.12+** 
- **Node.js 18+**
- **Ollama** 服务
- **Android/Termux** 环境（推荐）

## 安装和运行

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/grapeot/AndroidAgenticAIDemo.git
cd AndroidAgenticAIDemo

# 创建 Python 虚拟环境
uv venv
source venv/bin/activate

# 安装 Python 依赖
uv pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 设置 Tavily API Key（可选，用于搜索功能）
export TAVILY_API_KEY="your_tavily_api_key"
```

### 3. 启动 Ollama 服务

```bash
# 确保 Ollama 运行在 11434 端口
ollama serve

# 拉取 qwen3:1.7b 模型
ollama pull qwen3:1.7b
```

### 4. 启动后端服务

```bash
# 使用启动脚本
./start_backend.sh

# 或手动启动
uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload
```

### 5. 启动前端服务

```bash
cd frontend
npm install
npm start
```

## 使用说明

1. 前端服务启动后，访问 `http://localhost:3000`
2. 在聊天界面输入消息，AI 会使用本地 qwen3:1.7b 模型回复
3. 当询问需要实时信息的问题时，系统会自动调用 Tavily 搜索
4. 支持流式和非流式两种响应模式

## API 端点

### 后端 API (Port 8081)

- `GET /` - 健康检查
- `POST /api/chat` - 非流式聊天
- `POST /api/chat/stream` - 流式聊天
- `GET /api/conversations/{id}` - 获取对话历史

### 前端开发服务器 (Port 3000)

- 通过代理自动转发 API 请求到后端 8081 端口

## 开发笔记

### 依赖管理
- 使用 `uv` 管理 Python 虚拟环境和依赖
- 使用 `npm` 管理前端依赖

### 重要配置
- 前端代理配置：`"proxy": "http://localhost:8081"`
- Ollama API 兼容端点：`http://localhost:11434/v1`
- 模型配置：qwen3:1.7b（2B 参数，Q4_K_M 量化）

## 故障排除

### 常见问题

1. **前端显示"未连接"**
   - 检查后端服务是否在 8081 端口运行
   - 确认代理配置正确

2. **AI 回复为空**
   - 检查 Ollama 服务状态：`curl http://localhost:11434/api/tags`
   - 确认 qwen3:1.7b 模型已下载

3. **搜索功能不工作**
   - 检查 TAVILY_API_KEY 环境变量
   - 查看后端日志确认搜索服务状态

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**注意**: 此项目专为 Android/Termux 环境设计，在其他平台可能需要调整配置。