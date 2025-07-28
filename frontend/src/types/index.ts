// 基于 Design.md 中定义的前端数据结构

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  args: Record<string, any>;
  result?: any;
}

export enum SSEEventType {
  STATUS = 'status',
  TOOL_CALL = 'tool_call',
  CONTENT = 'content',
  ERROR = 'error',
  DONE = 'done'
}

export interface SSEEvent {
  type: SSEEventType;
  content?: string;
  tool_name?: string;
  tool_args?: Record<string, any>;
}

// API 请求/响应类型
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_calls_made?: string[];
}

export interface ConversationHistory {
  conversation_id: string;
  messages: Array<{
    role: MessageRole;
    content: string;
    timestamp: string;
  }>;
}

// 组件 Props 类型
export interface MessageBubbleProps {
  message: Message;
}

export interface LoadingIndicatorProps {
  type: 'typing' | 'searching' | 'processing';
  message?: string;
}

export interface ChatInterfaceProps {
  // 主聊天界面可能的 props（预留）
}

// 连接状态
export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  ERROR = 'error'
}

// 应用状态
export interface AppState {
  messages: Message[];
  currentMessage: string;
  isLoading: boolean;
  connectionStatus: ConnectionStatus;
  conversationId?: string;
  error?: string;
}