import uuid
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ChatRequest, ChatResponse, SSEEvent, SSEEventType
from services.openai_service import OpenAIService

app = FastAPI(title="AI Chat System", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
try:
    openai_service = OpenAIService()
except Exception as e:
    print(f"服务初始化失败: {e}")
    openai_service = None

@app.get("/")
def root():
    return {"message": "AI Chat System API"}

@app.get("/health")
def health_check():
    """健康检查端点"""
    if openai_service is None:
        raise HTTPException(status_code=503, detail="服务未正确初始化")
    return {"status": "healthy", "message": "All services are running"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """非流式聊天端点"""
    if openai_service is None:
        raise HTTPException(status_code=503, detail="OpenAI 服务未初始化")
    
    try:
        # 生成对话 ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # 调用 OpenAI 服务
        result = openai_service.chat_completion(request.message)
        
        if result["success"]:
            return ChatResponse(
                response=result["response"],
                conversation_id=conversation_id,
                tool_calls_made=result.get("tool_calls_made", [])
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest):
    """流式聊天端点"""
    if openai_service is None:
        raise HTTPException(status_code=503, detail="OpenAI 服务未初始化")
    
    async def generate():
        try:
            async for event in openai_service.chat_completion_stream(request.message):
                # 格式化为 SSE 格式
                sse_data = json.dumps(event, ensure_ascii=False)
                yield f"data: {sse_data}\n\n"
        except Exception as e:
            error_event = {
                "type": "error",
                "content": f"{type(e).__name__}: {str(e)}"
            }
            sse_data = json.dumps(error_event, ensure_ascii=False)
            yield f"data: {sse_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    """获取对话历史（暂时返回空实现）"""
    return {
        "conversation_id": conversation_id,
        "messages": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)