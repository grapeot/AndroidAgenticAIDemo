# Claude Development Notes

## 项目环境

- **Python 虚拟环境**: 使用 uv 创建的虚拟环境
- **虚拟环境名称**: `venv`
- **Python 版本**: CPython 3.12.11

## 重要提醒

### 依赖安装
本项目使用 `uv` 管理虚拟环境，安装依赖时请使用：
```bash
uv pip install <package>
```

**不要使用**：
```bash
pip install <package>  # 错误方式
```

### 激活虚拟环境
```bash
source venv/bin/activate
```

### API Keys
API Keys 已在系统环境变量中配置：
- `OPENAI_API_KEY` - OpenAI API 密钥
- `TAVILY_API_KEY` - Tavily API 密钥

代码中直接使用 `os.environ` 读取，无需 .env 文件。

## 项目结构
- `design.md` - 系统设计文档
- `Probing.md` - 技术验证计划
- `venv/` - Python 虚拟环境（已添加到 .gitignore）
- `probing/` - 技术验证脚本目录（待创建）