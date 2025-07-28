import os
import json
from typing import List, Dict, Any, AsyncGenerator
from openai import OpenAI
from backend.services.tavily_service import TavilyService

class OpenAIService:
    def __init__(self):
        # 使用 Ollama 本地服务
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"  # Ollama 不需要真实的 API key，只需要一个占位符
        )
        self.tavily_service = TavilyService()
        
        # 系统提示词
        self.system_prompt = (
            "你是一个智能助手。当用户询问需要实时信息的问题时，"
            "使用 search 工具来获取最新信息。请简洁而准确地回答用户的问题。"
        )
    
    def _prepare_messages(self, user_message: str) -> List[Dict[str, Any]]:
        """准备消息列表"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
    
    def chat_completion(self, message: str) -> Dict[str, Any]:
        """处理聊天完成，返回完整结果"""
        messages = self._prepare_messages(message)
        tools = [self.tavily_service.get_tool_definition()]
        tool_calls_made = []
        
        try:
            # 第一步：发送给 Ollama
            response = self.client.chat.completions.create(
                model="qwen3:1.7b",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # 检查是否需要工具调用
            if assistant_message.tool_calls:
                # 添加 assistant 消息到对话历史
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
                
                # 执行工具调用
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search":
                        tool_calls_made.append("search")
                        search_result = self.tavily_service.search(
                            function_args.get("query"),
                            function_args.get("max_results", 5)
                        )
                        
                        # 添加工具结果到消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(search_result, ensure_ascii=False)
                        })
                
                # 获取最终回复
                final_response = self.client.chat.completions.create(
                    model="qwen3:1.7b",
                    messages=messages
                )
                
                final_content = final_response.choices[0].message.content
            else:
                # 无需工具调用，直接返回
                final_content = assistant_message.content
            
            return {
                "success": True,
                "response": final_content,
                "tool_calls_made": tool_calls_made
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}"
            }
    
    async def chat_completion_stream(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """处理流式聊天完成"""
        messages = self._prepare_messages(message)
        tools = [self.tavily_service.get_tool_definition()]
        tool_calls_made = []
        
        try:
            yield {"type": "status", "content": "正在理解您的问题..."}
            
            # 第一步：发送给 Ollama
            response = self.client.chat.completions.create(
                model="qwen3:1.7b",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # 检查是否需要工具调用
            if assistant_message.tool_calls:
                yield {"type": "status", "content": "正在搜索相关信息..."}
                
                # 添加 assistant 消息到对话历史
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
                
                # 执行工具调用
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search":
                        tool_calls_made.append("search")
                        
                        # 发送工具调用事件
                        yield {
                            "type": "tool_call",
                            "tool_name": function_name,
                            "tool_args": function_args
                        }
                        
                        search_result = self.tavily_service.search(
                            function_args.get("query"),
                            function_args.get("max_results", 5)
                        )
                        
                        # 添加工具结果到消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(search_result, ensure_ascii=False)
                        })
                
                yield {"type": "status", "content": "正在生成回复..."}
                
                # 获取流式最终回复
                final_stream = self.client.chat.completions.create(
                    model="qwen3:1.7b",
                    messages=messages,
                    stream=True
                )
                
                for chunk in final_stream:
                    if chunk.choices[0].delta.content:
                        yield {
                            "type": "content",
                            "content": chunk.choices[0].delta.content
                        }
            else:
                # 无需工具调用，直接流式返回
                yield {"type": "status", "content": "正在生成回复..."}
                
                stream = self.client.chat.completions.create(
                    model="qwen3:1.7b",
                    messages=messages,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield {
                            "type": "content",
                            "content": chunk.choices[0].delta.content
                        }
            
            yield {"type": "done"}
            
        except Exception as e:
            yield {
                "type": "error",
                "content": f"{type(e).__name__}: {str(e)}"
            }