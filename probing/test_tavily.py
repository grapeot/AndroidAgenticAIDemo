#!/usr/bin/env python3
"""
第二阶段：Tavily 搜索 API 验证
测试目标：验证 Tavily API 搜索功能
"""

import os
import sys
import json
from tavily import TavilyClient

def test_tavily_basic_search():
    """测试基本的 Tavily 搜索功能"""
    
    # 从环境变量获取 API Key
    api_key = os.environ.get('TAVILY_API_KEY')
    if not api_key:
        print("错误：未找到 TAVILY_API_KEY 环境变量")
        sys.exit(1)
    
    print("✓ 找到 TAVILY_API_KEY")
    
    try:
        # 创建 Tavily 客户端
        client = TavilyClient(api_key=api_key)
        print("✓ Tavily 客户端创建成功")
        
        # 执行搜索测试
        print("\n正在搜索：'今天的科技新闻'...")
        
        response = client.search(
            query="今天的科技新闻",
            max_results=3,
            include_raw_content=False
        )
        
        print("✓ 搜索请求成功")
        
        # 显示搜索结果
        print(f"\n找到 {len(response['results'])} 个结果：")
        print("-" * 60)
        
        for i, result in enumerate(response['results'], 1):
            print(f"\n【结果 {i}】")
            print(f"标题：{result['title']}")
            print(f"URL：{result['url']}")
            print(f"内容摘要：{result['content'][:200]}...")
            if 'score' in result:
                print(f"相关性得分：{result['score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 搜索错误：{type(e).__name__}: {str(e)}")
        return False

def test_tavily_qna():
    """测试 Tavily Q&A 搜索功能"""
    
    api_key = os.environ.get('TAVILY_API_KEY')
    client = TavilyClient(api_key=api_key)
    
    print("\n\n=== 测试 Q&A 搜索 ===")
    
    try:
        question = "北京今天的天气如何？"
        print(f"问题：{question}")
        print("正在搜索答案...")
        
        answer = client.qna_search(query=question)
        
        print("✓ Q&A 搜索成功")
        print(f"\n答案：{answer}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Q&A 搜索错误：{type(e).__name__}: {str(e)}")
        return False

def test_tavily_context_search():
    """测试 Tavily 上下文搜索（适用于 RAG）"""
    
    api_key = os.environ.get('TAVILY_API_KEY')
    client = TavilyClient(api_key=api_key)
    
    print("\n\n=== 测试上下文搜索 (RAG) ===")
    
    try:
        query = "OpenAI GPT-4 最新功能"
        print(f"查询：{query}")
        print("正在获取上下文信息...")
        
        context = client.get_search_context(
            query=query,
            max_results=5
        )
        
        print("✓ 上下文搜索成功")
        print(f"\n上下文内容（前500字符）：")
        print("-" * 60)
        print(context[:500] + "...")
        print(f"\n总长度：{len(context)} 字符")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 上下文搜索错误：{type(e).__name__}: {str(e)}")
        return False

def test_search_with_filters():
    """测试带过滤器的搜索"""
    
    api_key = os.environ.get('TAVILY_API_KEY')
    client = TavilyClient(api_key=api_key)
    
    print("\n\n=== 测试高级搜索选项 ===")
    
    try:
        # 测试不同的搜索选项
        response = client.search(
            query="artificial intelligence news",
            search_depth="advanced",  # basic 或 advanced
            topic="news",  # general 或 news
            days=7,  # 限制最近7天的结果
            max_results=3
        )
        
        print("✓ 高级搜索成功")
        print(f"\n搜索参数：")
        print(f"- 搜索深度：advanced")
        print(f"- 主题：news")
        print(f"- 时间范围：最近7天")
        print(f"- 结果数量：{len(response['results'])}")
        
        # 显示第一个结果的详细信息
        if response['results']:
            first_result = response['results'][0]
            print(f"\n第一个结果详情：")
            print(f"- 标题：{first_result['title']}")
            print(f"- 发布时间：{first_result.get('published_date', 'N/A')}")
            print(f"- 来源：{first_result['url'].split('/')[2]}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 高级搜索错误：{type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Tavily API 验证脚本 ===\n")
    
    # 运行各项测试
    basic_success = test_tavily_basic_search()
    qna_success = test_tavily_qna()
    context_success = test_tavily_context_search()
    advanced_success = test_search_with_filters()
    
    # 总结
    print("\n\n=== 验证结果总结 ===")
    print(f"基本搜索：{'✓ 成功' if basic_success else '✗ 失败'}")
    print(f"Q&A 搜索：{'✓ 成功' if qna_success else '✗ 失败'}")
    print(f"上下文搜索：{'✓ 成功' if context_success else '✗ 失败'}")
    print(f"高级搜索：{'✓ 成功' if advanced_success else '✗ 失败'}")
    
    all_passed = all([basic_success, qna_success, context_success, advanced_success])
    
    if all_passed:
        print("\n🎉 所有测试通过！Tavily API 集成正常。")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        sys.exit(1)