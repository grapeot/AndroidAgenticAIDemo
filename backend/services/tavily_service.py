import os
from tavily import TavilyClient
from typing import Dict, Any

class TavilyService:
    def __init__(self):
        self.api_key = os.environ.get('TAVILY_API_KEY')
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        self.client = TavilyClient(api_key=self.api_key)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """返回搜索工具的定义"""
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
    
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """执行搜索功能"""
        try:
            # 使用基本搜索
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_raw_content=False
            )
            
            # 格式化结果
            formatted_results = []
            for result in response.get('results', []):
                content = result.get('content', '')
                if len(content) > 300:
                    content = content[:300] + "..."
                    
                formatted_results.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": content,
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