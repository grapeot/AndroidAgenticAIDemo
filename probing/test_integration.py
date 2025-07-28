#!/usr/bin/env python3
"""
第三阶段：工具调用集成验证
测试目标：验证 OpenAI 的 Function Calling 功能与 Tavily 的集成
"""

import os
import sys
import json
from openai import OpenAI
from tavily import TavilyClient

def create_search_tool_definition():
    """创建简化的搜索工具定义"""
    return {
        "type": "function",
        "function": {
            "name": "search",
            "description": "搜索实时信息。当用户询问最新新闻、天气、股价、体育赛事结果等需要实时信息的问题时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询字符串"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大结果数量",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }

def execute_search(tavily_client, query, max_results=5):
    """执行简化的搜索功能"""
    try:
        # 只使用基本搜索
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            include_raw_content=False
        )
        
        # 格式化结果
        formatted_results = []
        for result in response.get('results', []):
            formatted_results.append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "content": result.get('content', '')[:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', ''),
                "score": result.get('score', 0)
            })
        
        return {
            "success": True,
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}"
        }

def test_function_calling_integration():
    """测试 OpenAI Function Calling 与 Tavily 的完整集成"""
    
    # 检查环境变量
    openai_key = os.environ.get('OPENAI_API_KEY')
    tavily_key = os.environ.get('TAVILY_API_KEY')
    
    if not openai_key or not tavily_key:
        print("错误：未找到必要的环境变量")
        print(f"OPENAI_API_KEY: {'✓' if openai_key else '✗'}")
        print(f"TAVILY_API_KEY: {'✓' if tavily_key else '✗'}")
        return False
    
    print("✓ 找到所有必要的 API Keys")
    
    try:
        # 初始化客户端
        openai_client = OpenAI(api_key=openai_key)
        tavily_client = TavilyClient(api_key=tavily_key)
        print("✓ 客户端初始化成功")
        
        # 创建工具定义
        tools = [create_search_tool_definition()]
        print("✓ 工具定义创建成功")
        
        # 测试查询
        test_query = "北京今天的天气如何？"
        print(f"\n用户问题：{test_query}")
        print("=" * 60)
        
        # 第一步：发送给 OpenAI，让它决定是否需要使用工具
        print("\n步骤 1: 发送问题给 OpenAI...")
        
        messages = [
            {"role": "system", "content": "你是一个智能助手。当用户询问需要实时信息的问题时，使用 search 工具来获取最新信息。"},
            {"role": "user", "content": test_query}
        ]
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        print("✓ OpenAI 响应接收成功")
        
        assistant_message = response.choices[0].message
        
        # 检查是否有工具调用
        if assistant_message.tool_calls:
            print(f"\n步骤 2: 检测到 {len(assistant_message.tool_calls)} 个工具调用")
            
            # 处理工具调用
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in assistant_message.tool_calls
                ]
            })
            
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"\n工具调用详情：")
                print(f"- 函数名：{function_name}")
                print(f"- 参数：{json.dumps(function_args, ensure_ascii=False, indent=2)}")
                
                if function_name == "search":
                    print(f"\n步骤 3: 执行搜索...")
                    
                    # 执行搜索
                    search_result = execute_search(
                        tavily_client,
                        function_args.get("query"),
                        function_args.get("max_results", 5)
                    )
                    
                    if search_result["success"]:
                        print("✓ 搜索成功")
                        
                        # 将搜索结果添加到消息中
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(search_result, ensure_ascii=False)
                        })
                        
                        print(f"\n步骤 4: 将搜索结果返回给 OpenAI...")
                        
                        # 再次调用 OpenAI，让它基于搜索结果生成最终回复
                        final_response = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages
                        )
                        
                        final_answer = final_response.choices[0].message.content
                        print("✓ 最终回复生成成功")
                        
                        print(f"\n最终回复：")
                        print("-" * 60)
                        print(final_answer)
                        
                        return True
                    else:
                        print(f"✗ Tavily 搜索失败：{search_result['error']}")
                        return False
        else:
            print("\n无需工具调用，AI 直接回复：")
            print("-" * 60)
            print(assistant_message.content)
            return True
            
    except Exception as e:
        print(f"\n✗ 集成测试错误：{type(e).__name__}: {str(e)}")
        return False

def test_multiple_queries():
    """测试多种类型的查询"""
    
    print("\n\n=== 测试多种查询类型 ===")
    
    test_queries = [
        "今天有什么重要的科技新闻？",
        "特斯拉股价现在多少？",
        "2024年奥运会什么时候开始？"
    ]
    
    openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    tavily_client = TavilyClient(api_key=os.environ.get('TAVILY_API_KEY'))
    tools = [create_search_tool_definition()]
    
    successful_tests = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n【测试 {i}】：{query}")
        print("-" * 40)
        
        try:
            messages = [
                {"role": "system", "content": "你是一个智能助手。当用户询问需要实时信息的问题时，使用 search 工具来获取最新信息。请简洁地回答用户的问题。"},
                {"role": "user", "content": query}
            ]
            
            # 发送给 OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            if assistant_message.tool_calls:
                # 执行工具调用
                for tool_call in assistant_message.tool_calls:
                    if tool_call.function.name == "search":
                        function_args = json.loads(tool_call.function.arguments)
                        search_result = execute_search(
                            tavily_client,
                            function_args.get("query"),
                            function_args.get("max_results", 5)
                        )
                        
                        if search_result["success"]:
                            print(f"找到 {search_result['results_count']} 个相关结果")
                            successful_tests += 1
                        else:
                            print(f"搜索失败：{search_result['error']}")
            else:
                print(f"AI 直接回复：{assistant_message.content}")
                successful_tests += 1
                
        except Exception as e:
            print(f"测试失败：{type(e).__name__}: {str(e)}")
    
    print(f"\n多查询测试结果：{successful_tests}/{len(test_queries)} 成功")
    return successful_tests == len(test_queries)

if __name__ == "__main__":
    print("=== OpenAI + Tavily 集成验证脚本 ===\n")
    
    # 主要集成测试
    integration_success = test_function_calling_integration()
    
    # 多查询测试
    multi_query_success = test_multiple_queries()
    
    # 总结
    print("\n\n=== 验证结果总结 ===")
    print(f"主要集成测试：{'✓ 成功' if integration_success else '✗ 失败'}")
    print(f"多查询测试：{'✓ 成功' if multi_query_success else '✗ 失败'}")
    
    if integration_success and multi_query_success:
        print("\n🎉 所有集成测试通过！OpenAI Function Calling + Tavily 集成正常。")
        print("\n核心功能验证完成：")
        print("✓ OpenAI API 基本功能")
        print("✓ Tavily 搜索功能")
        print("✓ Function Calling 工具调用")
        print("✓ 端到端集成流程")
        print("\n系统已准备好进入正式开发阶段！")
    else:
        print("\n⚠️  部分集成测试失败，请检查错误信息。")
        sys.exit(1)