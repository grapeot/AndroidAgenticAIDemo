#!/usr/bin/env python3
"""
后端 Python Import 集成测试
测试目标：验证后端服务的核心功能（不需要运行服务器）
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.tavily_service import TavilyService
from backend.services.openai_service import OpenAIService
from backend.models.schemas import ChatRequest, MessageRole

def test_environment_variables():
    """测试环境变量配置"""
    print("=== 测试环境变量配置 ===")
    
    openai_key = os.environ.get('OPENAI_API_KEY')
    tavily_key = os.environ.get('TAVILY_API_KEY')
    
    print(f"OPENAI_API_KEY: {'✓' if openai_key else '✗'}")
    print(f"TAVILY_API_KEY: {'✓' if tavily_key else '✗'}")
    
    if not openai_key or not tavily_key:
        print("❌ 环境变量配置不完整")
        return False
    
    print("✅ 环境变量配置正确")
    return True

def test_tavily_service():
    """测试 Tavily 服务"""
    print("\n=== 测试 Tavily 服务 ===")
    
    try:
        # 初始化服务
        tavily_service = TavilyService()
        print("✓ TavilyService 初始化成功")
        
        # 测试工具定义
        tool_def = tavily_service.get_tool_definition()
        assert tool_def["type"] == "function"
        assert tool_def["function"]["name"] == "search"
        print("✓ 工具定义格式正确")
        
        # 测试搜索功能
        print("  测试搜索: '北京今天天气'")
        result = tavily_service.search("北京今天天气", max_results=3)
        
        if result["success"]:
            print(f"✓ 搜索成功，找到 {result['results_count']} 个结果")
            if result["results"]:
                first_result = result["results"][0]
                print(f"  首个结果: {first_result['title'][:50]}...")
        else:
            print(f"✗ 搜索失败: {result['error']}")
            return False
        
        print("✅ Tavily 服务测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Tavily 服务测试失败: {type(e).__name__}: {str(e)}")
        return False

def test_openai_service():
    """测试 OpenAI 服务"""
    print("\n=== 测试 OpenAI 服务 ===")
    
    try:
        # 初始化服务
        openai_service = OpenAIService()
        print("✓ OpenAIService 初始化成功")
        
        # 测试非流式聊天
        print("  测试非流式聊天: '今天是星期几？'")
        result = openai_service.chat_completion("今天是星期几？")
        
        if result["success"]:
            print("✓ 非流式聊天成功")
            print(f"  响应: {result['response'][:100]}...")
        else:
            print(f"✗ 非流式聊天失败: {result['error']}")
            return False
        
        # 测试需要搜索的问题
        print("  测试工具调用: '北京今天的天气如何？'")
        result = openai_service.chat_completion("北京今天的天气如何？")
        
        if result["success"]:
            print("✓ 工具调用聊天成功")
            print(f"  工具调用: {result.get('tool_calls_made', [])}")
            print(f"  响应: {result['response'][:100]}...")
        else:
            print(f"✗ 工具调用聊天失败: {result['error']}")
            return False
        
        print("✅ OpenAI 服务测试通过")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI 服务测试失败: {type(e).__name__}: {str(e)}")
        return False

async def test_openai_service_stream():
    """测试 OpenAI 流式服务"""
    print("\n=== 测试 OpenAI 流式服务 ===")
    
    try:
        openai_service = OpenAIService()
        print("✓ OpenAIService 初始化成功")
        
        # 测试流式响应
        print("  测试流式响应: '今天北京的天气如何？'")
        
        events = []
        async for event in openai_service.chat_completion_stream("今天北京的天气如何？"):
            events.append(event)
            event_type = event.get("type")
            if event_type == "status":
                print(f"  状态: {event.get('content')}")
            elif event_type == "tool_call":
                print(f"  工具调用: {event.get('tool_name')} - {event.get('tool_args')}")
            elif event_type == "content":
                print(f"  内容片段: {event.get('content')}", end="", flush=True)
            elif event_type == "done":
                print("\n  ✓ 流式响应完成")
            elif event_type == "error":
                print(f"\n  ✗ 流式响应错误: {event.get('content')}")
                return False
        
        # 验证事件序列
        event_types = [e.get("type") for e in events]
        if "done" in event_types:
            print("✅ OpenAI 流式服务测试通过")
            return True
        else:
            print("❌ OpenAI 流式服务测试失败: 未收到完成事件")
            return False
        
    except Exception as e:
        print(f"❌ OpenAI 流式服务测试失败: {type(e).__name__}: {str(e)}")
        return False

def test_schemas():
    """测试数据模型"""
    print("\n=== 测试数据模型 ===")
    
    try:
        # 测试 ChatRequest
        request = ChatRequest(message="测试消息")
        assert request.message == "测试消息"
        assert request.conversation_id is None
        print("✓ ChatRequest 模型正确")
        
        # 测试带对话 ID 的请求
        request_with_id = ChatRequest(message="测试", conversation_id="test-123")
        assert request_with_id.conversation_id == "test-123"
        print("✓ ChatRequest 带对话ID 模型正确")
        
        print("✅ 数据模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {type(e).__name__}: {str(e)}")
        return False

async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始后端 Python Import 集成测试\n")
    
    tests = [
        ("环境变量", test_environment_variables),
        ("Tavily 服务", test_tavily_service),
        ("OpenAI 服务", test_openai_service),
        ("数据模型", test_schemas),
    ]
    
    # 运行同步测试
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # 运行异步测试
    async_result = await test_openai_service_stream()
    results.append(("OpenAI 流式服务", async_result))
    
    # 总结结果
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！后端核心功能正常工作。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)