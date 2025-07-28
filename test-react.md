# React 前端测试指南

## 🎯 测试目标

验证 AI 聊天系统前端功能是否正常：
- 与后端 API 连接
- 实时流式响应
- 搜索工具调用
- 用户界面交互

## 📋 环境要求

- Node.js（已安装）
- npm（已安装）
- 后端服务运行在 8081 端口
- 浏览器（推荐 Chrome 或 Firefox）

## 🚀 启动步骤

### 步骤 1：启动后端服务

**打开第一个终端窗口**：
```bash
cd /data/data/com.termux/files/home/co/tmp
source venv/bin/activate
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

**成功标志**：
```
INFO:     Uvicorn running on http://0.0.0.0:8081 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**测试后端是否工作**：
```bash
# 在另一个终端测试
curl http://localhost:8081/health
# 预期返回：{"status":"healthy","message":"All services are running"}
```

### 步骤 2：安装前端依赖

**打开第二个终端窗口**：
```bash
cd /data/data/com.termux/files/home/co/tmp/frontend
npm install
```

**安装过程说明**：
- 第一次需要 5-10 分钟下载依赖
- 会显示很多下载信息，这是正常的
- 看到 "added xxx packages" 表示成功

**如果安装失败**：
```bash
# 清理缓存后重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 步骤 3：启动前端开发服务器

**在前端目录执行**：
```bash
npm start
```

**启动过程**：
1. 显示 "Starting the development server..."
2. 编译过程（第一次较慢，约 1-3 分钟）
3. 看到 "Compiled successfully!" 表示成功

**成功标志**：
```
Compiled successfully!

You can now view ai-chat-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

## 🌐 访问应用

### 浏览器访问

**主要地址**：http://localhost:3000

**备用地址**（如果 localhost 不工作）：
- http://127.0.0.1:3000
- http://[显示的 Network IP]:3000

### 预期界面

**顶部区域**：
- 标题："AI Chat System"
- 右侧连接状态：圆点 + "已连接"/"未连接"

**中间区域**：
- 空白聊天区域（开始时）
- 消息会在这里显示

**底部区域**：
- 输入框："输入消息..."
- 发送按钮："📤 发送"

## 🧪 功能测试

### 测试用例 1：基本对话

**输入**："你好"

**操作**：
1. 在输入框输入文字
2. 点击发送按钮或按回车键

**预期结果**：
1. 右侧出现蓝色气泡（你的消息）
2. 左侧显示："💭 AI 正在思考..."
3. 加载指示器消失
4. 左侧出现白色气泡（AI 回复）
5. 包含时间戳和消息状态

### 测试用例 2：天气搜索

**输入**："北京今天的天气如何？"

**预期过程**：
1. 用户消息显示（蓝色气泡）
2. 状态变化序列：
   - "💭 AI 正在思考..."
   - "🔍 正在搜索相关信息..."
   - "⚙️ 正在生成回复..."
3. AI 回复包含实时天气信息

**验证要点**：
- 回复内容包含具体温度、天气状况
- 消息中可能显示工具调用信息
- 响应时间合理（10-30秒）

### 测试用例 3：新闻搜索

**输入**："今天有什么重要的科技新闻？"

**预期结果**：
- 搜索状态正确显示
- AI 回复包含最新科技新闻
- 可能包含新闻标题、来源等信息

### 测试用例 4：股价查询

**输入**："特斯拉股价现在多少？"

**预期结果**：
- 触发搜索工具
- 返回当前股价信息
- 可能包含涨跌幅信息

### 测试用例 5：停止生成

**操作**：
1. 发送一个会触发搜索的问题
2. 在 AI 回复过程中点击"⏹️ 停止"按钮

**预期结果**：
- 立即停止内容生成
- 按钮变回"📤 发送"
- 可以继续发送新消息

## ✅ 成功标准

### 连接状态
- [ ] 连接状态显示"已连接"
- [ ] 绿色指示点

### 消息功能
- [ ] 消息能正常发送
- [ ] 用户消息显示为蓝色气泡
- [ ] AI 消息显示为白色气泡
- [ ] 消息包含正确时间戳

### 流式响应
- [ ] 加载状态正确显示
- [ ] 状态文字会变化
- [ ] AI 回复逐字出现（流式效果）

### 搜索功能
- [ ] 搜索类问题能触发工具调用
- [ ] 显示"正在搜索相关信息..."
- [ ] 返回实时准确信息

### 界面交互
- [ ] 输入框正常工作
- [ ] 回车键能发送消息
- [ ] 滚动到最新消息
- [ ] 停止按钮正常工作

## 🐛 常见问题排查

### 问题 1：无法访问 http://localhost:3000

**可能原因**：
- 前端服务未启动
- 端口被占用
- 防火墙阻止

**解决方法**：
```bash
# 检查端口占用
lsof -ti:3000

# 如果有进程，杀死它
kill -9 $(lsof -ti:3000)

# 重新启动
npm start
```

### 问题 2：连接状态显示"未连接"

**可能原因**：
- 后端服务未运行
- 端口配置错误
- API 调用失败

**检查方法**：
```bash
# 测试后端健康状态
curl http://localhost:8081/health

# 检查后端进程
ps aux | grep uvicorn
```

### 问题 3：消息发送无反应

**检查要点**：
- 输入框是否为空
- 网络连接是否正常
- 浏览器控制台是否有错误

### 问题 4：搜索功能不工作

**可能原因**：
- API Keys 未正确配置
- Tavily 服务异常
- 网络连接问题

**验证方法**：
```bash
# 检查环境变量
echo $OPENAI_API_KEY
echo $TAVILY_API_KEY
```

### 问题 5：编译错误

**常见解决**：
```bash
# 删除依赖重新安装
rm -rf node_modules package-lock.json
npm install

# 清理缓存
npm cache clean --force
```

## 📊 性能预期

### 响应时间
- **普通对话**：1-3 秒
- **搜索查询**：5-15 秒
- **复杂问题**：10-30 秒

### 内存使用
- **前端页面**：约 50-100MB
- **Node.js 进程**：约 100-200MB

## 🔧 调试工具

### 浏览器开发者工具

**打开方式**：按 F12 或右键 → 检查

**Network 标签**：
- 查看 API 请求
- 检查响应状态码
- 观察数据流

**Console 标签**：
- 查看错误信息
- 观察日志输出

**常用命令**：
```bash
# 查看网络请求
# 在 Network 标签中筛选 "chat"

# 查看实时日志
# 在 Console 标签中观察输出
```

## 📝 测试记录模板

```
测试时间：____年__月__日 __:__

环境信息：
- 操作系统：Android/Termux
- 浏览器：Chrome/Firefox 版本____
- Node.js 版本：____
- 后端状态：正常/异常

测试结果：
[ ] 前端启动成功
[ ] 后端连接正常
[ ] 基本对话功能
[ ] 搜索功能
[ ] 流式响应
[ ] 界面交互

发现问题：
1. ________________
2. ________________

测试完成度：____%
```

## 🎯 下一步

测试完成后可以考虑：
1. UI 美化和优化
2. 添加更多功能
3. 性能优化
4. 移动端适配

---

**💡 提示**：
- 第一次启动较慢是正常的
- 确保同时运行后端和前端服务
- 遇到问题先检查终端输出信息
- 可以多刷新几次页面解决偶发问题