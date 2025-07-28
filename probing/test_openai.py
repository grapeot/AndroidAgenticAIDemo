#!/usr/bin/env python3
"""
第一阶段：OpenAI API 基础验证
测试目标：验证 OpenAI API 连接和基本对话功能
"""

import os
import sys
from openai import OpenAI

def test_openai_basic():
    """测试基本的 OpenAI API 调用"""
    
    # 从环境变量获取 API Key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("错误：未找到 OPENAI_API_KEY 环境变量")
        sys.exit(1)
    
    print("✓ 找到 OPENAI_API_KEY")
    
    try:
        # 创建 OpenAI 客户端
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI 客户端创建成功")
        
        # 发送测试请求
        print("\n正在发送测试请求：'给我讲个笑话'...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "给我讲个笑话"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        print("✓ API 请求成功")
        
        # 提取并显示响应
        joke = response.choices[0].message.content
        print(f"\n响应内容：\n{joke}")
        
        # 显示响应元数据
        print(f"\n响应元数据：")
        print(f"- 模型：{response.model}")
        print(f"- 使用的 tokens：{response.usage.total_tokens}")
        print(f"- 响应 ID：{response.id}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 错误：{type(e).__name__}: {str(e)}")
        return False

def test_streaming():
    """测试流式响应"""
    
    api_key = os.environ.get('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)
    
    print("\n\n=== 测试流式响应 ===")
    print("正在发送流式请求...")
    
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "用三句话介绍Python"}
            ],
            temperature=0.7,
            stream=True
        )
        
        print("✓ 流式请求成功，开始接收响应：\n")
        
        collected_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                print(content, end='', flush=True)
        
        print("\n\n✓ 流式响应接收完成")
        print(f"总字符数：{len(''.join(collected_content))}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 流式响应错误：{type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== OpenAI API 验证脚本 ===\n")
    
    # 测试基本功能
    basic_success = test_openai_basic()
    
    # 测试流式响应
    streaming_success = test_streaming()
    
    # 总结
    print("\n\n=== 验证结果总结 ===")
    print(f"基本 API 调用：{'✓ 成功' if basic_success else '✗ 失败'}")
    print(f"流式响应：{'✓ 成功' if streaming_success else '✗ 失败'}")
    
    if basic_success and streaming_success:
        print("\n🎉 所有测试通过！OpenAI API 集成正常。")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        sys.exit(1)