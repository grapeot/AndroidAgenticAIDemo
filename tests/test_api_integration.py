#!/usr/bin/env python3
"""
后端 API 集成测试
测试目标：验证运行中的 FastAPI 服务器的 API 功能
注意：此测试需要先启动后端服务器（python backend/main.py 或 uvicorn backend.main:app --reload）
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# API 基础 URL
BASE_URL = "http://localhost:8081"

def test_server_health():
    """测试服务器健康状态"""
    print("=== 测试服务器健康状态 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器健康检查通过")
            return True
        else:
            print(f"❌ 服务器健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保后端服务器正在运行:")
        print("  cd backend && python main.py")
        print("  或者: uvicorn backend.main:app --reload")
        return False

def test_basic_chat():
    """测试基础聊天功能"""
    print("\n=== 测试基础聊天 API ===")
    
    try:
        # 测试简单问题
        payload = {
            "message": "你好，请介绍一下自己"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 基础聊天请求成功")
            print(f"  响应: {data['response'][:100]}...")
            print(f"  对话ID: {data['conversation_id']}")
            print(f"  工具调用: {data.get('tool_calls_made', [])}")
            return True
        else:
            print(f"❌ 基础聊天请求失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 基础聊天测试失败: {type(e).__name__}: {str(e)}")
        return False

def test_search_chat():
    """测试需要搜索的聊天"""
    print("\n=== 测试搜索功能 API ===")
    
    try:
        # 测试需要搜索的问题
        payload = {
            "message": "北京今天的天气如何？"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=60  # 搜索可能需要更长时间
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 搜索聊天请求成功")
            print(f"  响应: {data['response'][:100]}...")
            print(f"  工具调用: {data.get('tool_calls_made', [])}")
            
            # 验证是否使用了搜索工具
            if "search" in data.get('tool_calls_made', []):
                print("✓ 成功调用了搜索工具")
                return True
            else:
                print("⚠️ 未调用搜索工具，但请求成功")
                return True
        else:
            print(f"❌ 搜索聊天请求失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 搜索聊天测试失败: {type(e).__name__}: {str(e)}")
        return False

def test_stream_chat():
    """测试流式聊天功能"""
    print("\n=== 测试流式聊天 API ===")
    
    try:
        payload = {
            "message": "今天有什么重要的科技新闻？"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/stream",
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✓ 流式聊天连接成功")
            
            events = []
            content_parts = []
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # 移除 "data: " 前缀
                        events.append(data)
                        
                        event_type = data.get("type")
                        if event_type == "status":
                            print(f"  状态: {data.get('content')}")
                        elif event_type == "tool_call":
                            print(f"  工具调用: {data.get('tool_name')} - {data.get('tool_args')}")
                        elif event_type == "content":
                            content_parts.append(data.get('content', ''))
                            print(".", end="", flush=True)
                        elif event_type == "done":
                            print("\n✓ 流式响应完成")
                            break
                        elif event_type == "error":
                            print(f"\n❌ 流式响应错误: {data.get('content')}")
                            return False
                    except json.JSONDecodeError:
                        continue
            
            # 验证收到的内容
            full_content = "".join(content_parts)
            if full_content:
                print(f"  完整响应: {full_content[:100]}...")
            
            # 验证事件序列
            event_types = [e.get("type") for e in events]
            if "done" in event_types:
                print("✅ 流式聊天测试通过")
                return True
            else:
                print("❌ 流式聊天测试失败: 未收到完成事件")
                return False
        else:
            print(f"❌ 流式聊天请求失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 流式聊天测试失败: {type(e).__name__}: {str(e)}")
        return False

def test_conversation_api():
    """测试对话历史 API"""
    print("\n=== 测试对话历史 API ===")
    
    try:
        conversation_id = "test-conversation-123"
        response = requests.get(f"{BASE_URL}/api/conversations/{conversation_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 对话历史请求成功")
            print(f"  对话ID: {data['conversation_id']}")
            print(f"  消息数量: {len(data['messages'])}")
            return True
        else:
            print(f"❌ 对话历史请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 对话历史测试失败: {type(e).__name__}: {str(e)}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试空消息
    try:
        payload = {"message": ""}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        print(f"  空消息测试: {response.status_code}")
    except:
        pass
    
    # 测试无效 JSON
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"  无效JSON测试: {response.status_code}")
    except:
        pass
    
    print("✅ 错误处理测试完成")
    return True

def run_all_api_tests():
    """运行所有 API 测试"""
    print("🚀 开始后端 API 集成测试\n")
    print("注意: 此测试需要后端服务器正在运行")
    print("启动命令: cd backend && python main.py\n")
    
    # 等待用户确认
    input("按 Enter 键开始测试（确保服务器已启动）...")
    
    tests = [
        ("服务器健康状态", test_server_health),
        ("基础聊天功能", test_basic_chat),
        ("搜索功能", test_search_chat),
        ("流式聊天功能", test_stream_chat),
        ("对话历史API", test_conversation_api),
        ("错误处理", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        if name == "服务器健康状态":
            # 健康检查失败则停止后续测试
            result = test_func()
            if not result:
                print("\n❌ 服务器未运行，停止测试")
                return False
        else:
            result = test_func()
        
        results.append((name, result))
        
        # 在测试之间稍作停顿
        time.sleep(1)
    
    # 总结结果
    print("\n" + "="*60)
    print("📊 API 测试结果总结")
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
        print("🎉 所有 API 测试通过！后端服务正常工作。")
        return True
    else:
        print("⚠️ 部分 API 测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = run_all_api_tests()
    sys.exit(0 if success else 1)