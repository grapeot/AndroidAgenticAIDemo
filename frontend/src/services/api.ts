// SSE 客户端实现，基于 Design.md 中的 API 接口定义

import { ChatRequest, ChatResponse, SSEEvent, SSEEventType, ConversationHistory } from '../types';

const API_BASE_URL = '/api';

export class ChatAPI {
  // 非流式聊天 API
  static async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // 流式聊天 API - 使用 fetch 实现 POST SSE
  static createStreamingConnection(
    request: ChatRequest,
    onEvent: (event: SSEEvent) => void,
    onError: (error: Error) => void,
    onClose: () => void
  ): () => void {
    let abortController = new AbortController();
    let isConnected = true;

    const startStreaming = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('Failed to get response reader');
        }

        while (isConnected) {
          const { done, value } = await reader.read();
          
          if (done) {
            onClose();
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = line.slice(6); // 移除 'data: ' 前缀
                if (eventData.trim()) {
                  const sseEvent: SSEEvent = JSON.parse(eventData);
                  onEvent(sseEvent);
                  
                  // 如果收到 done 事件，关闭连接
                  if (sseEvent.type === 'done') {
                    isConnected = false;
                    onClose();
                    break;
                  }
                }
              } catch (error) {
                console.error('Failed to parse SSE event:', error);
                // 不要因为单个解析错误而终止整个流
              }
            }
          }
        }
      } catch (error) {
        if (!abortController.signal.aborted) {
          console.error('SSE connection error:', error);
          onError(error as Error);
        }
      }
    };

    // 开始流式连接
    startStreaming();

    // 返回关闭连接的函数
    return () => {
      isConnected = false;
      abortController.abort();
    };
  }

  // 获取对话历史
  static async getConversationHistory(conversationId: string): Promise<ConversationHistory> {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// SSE 事件处理器类型
export interface SSEEventHandlers {
  onStatus: (message: string) => void;
  onToolCall: (toolName: string, args: Record<string, any>) => void;
  onContent: (content: string) => void;
  onError: (error: string) => void;
  onDone: () => void;
}

// 简化的 SSE 连接管理器
export class StreamingChatManager {
  private closeConnection?: () => void;
  private isConnected = false;

  constructor(private handlers: SSEEventHandlers) {}

  startStreaming(request: ChatRequest): void {
    if (this.isConnected) {
      this.stopStreaming();
    }

    this.closeConnection = ChatAPI.createStreamingConnection(
      request,
      this.handleSSEEvent.bind(this),
      (error) => {
        this.handlers.onError(error.message);
        this.isConnected = false;
      },
      () => {
        this.isConnected = false;
      }
    );

    this.isConnected = true;
  }

  stopStreaming(): void {
    if (this.closeConnection) {
      this.closeConnection();
      this.closeConnection = undefined;
    }
    this.isConnected = false;
  }

  private handleSSEEvent(event: SSEEvent): void {
    switch (event.type) {
      case SSEEventType.STATUS:
        if (event.content) {
          this.handlers.onStatus(event.content);
        }
        break;
      
      case SSEEventType.TOOL_CALL:
        if (event.tool_name && event.tool_args) {
          this.handlers.onToolCall(event.tool_name, event.tool_args);
        }
        break;
      
      case SSEEventType.CONTENT:
        if (event.content) {
          this.handlers.onContent(event.content);
        }
        break;
      
      case SSEEventType.ERROR:
        if (event.content) {
          this.handlers.onError(event.content);
        }
        break;
      
      case SSEEventType.DONE:
        this.handlers.onDone();
        this.stopStreaming();
        break;
      
      default:
        console.warn('Unknown SSE event type:', event.type);
    }
  }

  get connected(): boolean {
    return this.isConnected;
  }
}